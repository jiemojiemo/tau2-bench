"""Publish completed text-run scores as a LangSmith experiment."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from time import sleep
from uuid import NAMESPACE_URL, uuid5

from loguru import logger

from tau2.data_model.simulation import Results, TerminationReason
from tau2.data_model.tasks import RewardType
from tau2.metrics.agent_metrics import AgentMetrics
from tau2.utils.artifacts import content_digest
from tau2.utils.tracing import tracing_enabled
from tau2.utils.utils import get_dict_hash


def _format_scores(scores: dict[str, float]) -> list[dict[str, str | float]]:
    # LangSmith accepts scores with up to four decimal places.
    return [{"key": key, "score": round(score, 4)} for key, score in scores.items()]


def _experiment_rows(results: Results, dataset_name: str, trace_urls: dict) -> list:
    rows = []
    for sim in results.simulations:
        reward = sim.reward_info
        scores = {}
        if (
            reward is not None
            and sim.termination_reason != TerminationReason.INFRASTRUCTURE_ERROR
        ):
            scores["reward"] = reward.reward
            if reward.db_check is not None:
                scores["db_match"] = int(reward.db_check.db_match)
            for basis, score in (reward.reward_breakdown or {}).items():
                if basis != RewardType.DB and (
                    basis != RewardType.COMMUNICATE or reward.communicate_checks
                ):
                    scores[basis.value.lower()] = score

        outputs = {"termination_reason": sim.termination_reason.value}
        trace = (sim.info or {}).get("langsmith_trace")
        if trace and (url := trace_urls.get(trace["project"])):
            outputs["agent_trace"] = f"{url}/r/{trace['id']}"
        row = {
            "row_id": str(
                uuid5(NAMESPACE_URL, f"{dataset_name}/{sim.task_id}/{sim.trial}")
            ),
            "inputs": {"task_id": sim.task_id, "trial": sim.trial},
            "actual_outputs": outputs,
            "evaluation_scores": _format_scores(scores),
            "start_time": datetime.fromisoformat(sim.start_time)
            .astimezone(timezone.utc)
            .isoformat(),
            "end_time": datetime.fromisoformat(sim.end_time)
            .astimezone(timezone.utc)
            .isoformat(),
        }
        if sim.termination_reason == TerminationReason.INFRASTRUCTURE_ERROR:
            row["error"] = sim.termination_reason.value
        rows.append(row)
    return rows


def _publish_trace_feedback(client, results: Results, rows: list, trace_projects: dict):
    from langsmith.utils import LangSmithError

    def publish(sim, row):
        trace = (sim.info or {}).get("langsmith_trace")
        if not trace or not (project := trace_projects.get(trace["project"])):
            return
        for score in row["evaluation_scores"]:
            try:
                client.create_feedback(
                    trace_id=trace["id"],
                    session_id=project.id,
                    feedback_id=uuid5(
                        NAMESPACE_URL, f"tau2/{trace['id']}/{score['key']}"
                    ),
                    extend_trace_retention=False,
                    stop_after_attempt=2,
                    **score,
                )
            except (LangSmithError, ValueError) as exc:
                logger.warning(
                    "LangSmith trace feedback failed for task {} ({})",
                    sim.task_id,
                    type(exc).__name__,
                )

    if trace_projects:
        with ThreadPoolExecutor(max_workers=8) as executor:
            list(executor.map(publish, results.simulations, rows))


def _agent_spans(source_runs, source_root, target) -> list[dict]:
    """Build the missing child runs under an imported Experiment row."""
    existing_ids = set(target.child_run_ids or ())
    parents = {source_root.id: (target.id, target.dotted_order)}
    spans = []

    for span in sorted(source_runs, key=lambda run: run.dotted_order):
        if span.run_type not in {"llm", "tool"} or not (
            parent := parents.get(span.parent_run_id)
        ):
            continue
        parent_id, parent_order = parent
        span_id = uuid5(NAMESPACE_URL, f"tau2/{target.id}/{span.id}")
        start = span.start_time.astimezone(timezone.utc)
        dotted_order = f"{parent_order}.{start:%Y%m%dT%H%M%S%fZ}{span_id}"
        parents[span.id] = span_id, dotted_order
        if span_id not in existing_ids:
            metadata = (span.extra or {}).get("metadata") or {}
            spans.append(
                {
                    "id": span_id,
                    "trace_id": target.id,
                    "parent_run_id": parent_id,
                    "session_id": target.session_id,
                    "dotted_order": dotted_order,
                    "name": span.name,
                    "run_type": span.run_type,
                    "start_time": start,
                    "end_time": span.end_time,
                    "inputs": span.inputs,
                    "outputs": span.outputs,
                    "error": span.error,
                    "extra": {
                        "metadata": {
                            key: metadata[key]
                            for key in ("ls_model_name", "ls_provider")
                            if key in metadata
                        }
                    },
                }
            )
    return spans


def _publish_experiment_traces(client, experiment_id, results: Results, projects: dict):
    from langsmith.utils import LangSmithError, LangSmithRateLimitError

    traced_cases = {}
    for sim in results.simulations:
        if (trace := (sim.info or {}).get("langsmith_trace")) and (
            project := projects.get(trace["project"])
        ):
            traced_cases[sim.task_id, sim.trial] = (sim, trace["id"], project.id)
    if not traced_cases:
        return

    # Experiment runs can take a moment to appear after the import returns.
    targets = {}
    for attempt in range(8):
        if attempt:
            sleep(1)
        targets = {
            (run.inputs.get("task_id"), run.inputs.get("trial")): run
            for run in client.list_runs(
                project_id=experiment_id,
                is_root=True,
                select=[
                    "id",
                    "inputs",
                    "name",
                    "run_type",
                    "start_time",
                    "dotted_order",
                    "session_id",
                    "child_run_ids",
                ],
            )
        }
        if traced_cases.keys() <= targets.keys():
            break

    def copy(case):
        sim, trace_id, source_project_id = traced_cases[case]
        if not (target := targets.get(case)):
            logger.warning("LangSmith experiment row missing for task {}", sim.task_id)
            return
        for delay in (0, 2, 5):
            if delay:
                sleep(delay)
            try:
                source_runs = list(
                    client.list_runs(project_id=source_project_id, trace_id=trace_id)
                )
                source = next((r for r in source_runs if str(r.id) == trace_id), None)
                if (
                    source is None
                    or source.name != "tau2.simulation"
                    or source.inputs.get("simulation_id") != sim.id
                    or source.inputs.get("task_id") != sim.task_id
                ):
                    raise ValueError("Unexpected Agent Trace")
                if spans := _agent_spans(source_runs, source, target):
                    client.batch_ingest_runs(create=spans)
                return
            except LangSmithRateLimitError:
                continue
            except (LangSmithError, ValueError) as exc:
                logger.warning(
                    "LangSmith experiment trace upload failed for task {} ({})",
                    sim.task_id,
                    type(exc).__name__,
                )
                return
        logger.warning(
            "LangSmith rate limited the experiment trace for task {}", sim.task_id
        )

    with ThreadPoolExecutor(max_workers=3) as executor:
        list(executor.map(copy, traced_cases))


def publish_experiment(
    results: Results, metrics: AgentMetrics, run_name: str
) -> str | None:
    """Upload existing scores and return the comparison URL, with no model calls."""
    if not tracing_enabled() or not results.simulations:
        return None

    from langsmith.run_trees import get_cached_client
    from langsmith.utils import LangSmithError, LangSmithNotFoundError

    info = results.info
    domain = info.environment_info.domain_name
    language = info.language or "en"
    dataset_digest = get_dict_hash(
        {
            "artifacts": info.language_artifacts.model_dump(mode="json")
            if info.language_artifacts
            else None,
            "tasks": {task.id: content_digest(task) for task in results.tasks},
            "trials": info.num_trials,
        }
    )[:12]
    dataset_name = f"tau2-{domain}-{language}-{len(results.tasks)}-{dataset_digest}"
    run_digest = get_dict_hash(
        {"simulations": sorted(sim.id for sim in results.simulations)}
    )[:12]
    experiment_name = f"tau2-{run_name}-{run_digest}"

    try:
        client = get_cached_client(timeout_ms=15000)
        projects = {
            trace["project"]
            for sim in results.simulations
            if (trace := (sim.info or {}).get("langsmith_trace"))
        }
        trace_projects = {}
        if projects:
            client.flush(timeout=15)
            for project in sorted(projects):
                try:
                    trace_projects[project] = client.read_project(project_name=project)
                except LangSmithError as exc:
                    logger.warning(
                        "LangSmith trace project {} could not be read ({})",
                        project,
                        type(exc).__name__,
                    )
        rows = _experiment_rows(
            results,
            dataset_name,
            {name: project.url for name, project in trace_projects.items()},
        )

        try:
            existing = client.read_project(project_name=experiment_name)
        except LangSmithNotFoundError:
            summary = {f"pass^{k}": score for k, score in metrics.pass_hat_ks.items()}
            if metrics.total_simulations:
                summary["average_reward"] = metrics.avg_reward
            db_total = metrics.db_match_count + metrics.db_mismatch_count
            if db_total:
                summary["db_match_rate"] = metrics.db_match_count / db_total
            for action, correct, total in (
                ("read", metrics.correct_read_actions, metrics.total_read_actions),
                ("write", metrics.correct_write_actions, metrics.total_write_actions),
            ):
                if total:
                    summary[f"{action}_action_match_rate"] = correct / total

            response = client.request_with_retries(
                "POST",
                "/api/v1/datasets/upload-experiment",
                request_kwargs={
                    "json": {
                        "dataset_name": dataset_name,
                        "experiment_name": experiment_name,
                        "experiment_start_time": min(row["start_time"] for row in rows),
                        "experiment_end_time": max(row["end_time"] for row in rows),
                        "experiment_metadata": {
                            "agent": info.agent_info.implementation,
                            "model": info.agent_info.llm,
                            "language": language,
                            "domain": domain,
                            "evaluated_simulations": metrics.total_simulations,
                            "infrastructure_errors": metrics.infra_error_count,
                        },
                        "summary_experiment_scores": _format_scores(summary),
                        "results": rows,
                    }
                },
            ).json()
            experiment_id, dataset_id = (
                response["experiment"]["id"],
                response["dataset"]["id"],
            )
        else:
            experiment_id, dataset_id = existing.id, existing.reference_dataset_id
        dataset_url = client.read_dataset(dataset_id=dataset_id).url
        try:
            _publish_experiment_traces(client, experiment_id, results, trace_projects)
        except (LangSmithError, ValueError) as exc:
            logger.warning(
                "LangSmith experiment traces unavailable ({})", type(exc).__name__
            )
        _publish_trace_feedback(client, results, rows, trace_projects)
        return f"{dataset_url}/compare?selectedSessions={experiment_id}"
    except (LangSmithError, ValueError) as exc:
        logger.error(
            "LangSmith experiment upload failed ({}); local results are saved.",
            type(exc).__name__,
        )
        return None
