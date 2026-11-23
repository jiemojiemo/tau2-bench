"""Run one Chinese airline split and publish its results to LangSmith.

Usage:
    uv run --frozen --extra langsmith python scripts/run_airline_zh_eval.py \
        --split test --save-to airline-zh-test-dev-v1
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from tau2.utils.utils import DATA_DIR

ROOT = Path(__file__).resolve().parents[1]
MODEL = "openai/gpt-6-luna"
MODEL_ARGS = {"reasoning_effort": "low", "allowed_openai_params": ["reasoning_effort"]}


def main() -> int:
    """Select localized task IDs and run the benchmark CLI."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--split", choices=("train", "test"), default="test")
    parser.add_argument("--save-to", required=True, help="Name for this run's results")
    parser.add_argument("--agent", default="my_agent", help="Registered tau2 agent")
    parser.add_argument("--max-concurrency", type=int, default=8)
    parser.add_argument("--auto-resume", action="store_true")
    args = parser.parse_args()

    data_dir = ROOT / DATA_DIR
    save_path = data_dir / "simulations" / args.save_to / "results.json"
    if save_path.exists() and not args.auto_resume:
        parser.error("run already exists; choose a new --save-to or add --auto-resume")

    splits = json.loads(
        (data_dir / "tau2/domains/airline/split_tasks.json").read_text()
    )
    metadata_path = data_dir / "tau2/multilingual/zh/airline_metadata_zh.json"
    metadata = json.loads(metadata_path.read_text())
    canonical_ids = set(splits[args.split])
    task_ids = [
        task_id
        for task_id, task in metadata.items()
        if task["canonical_task_id"] in canonical_ids
    ]
    if (
        len(task_ids) != len(canonical_ids)
        or {metadata[task_id]["canonical_task_id"] for task_id in task_ids}
        != canonical_ids
    ):
        parser.error(f"expected one Chinese task for each canonical {args.split} task")

    print(f"Airline zh {args.split}: {len(task_ids)} tasks, one trial each", flush=True)
    command = [
        sys.executable,
        "-m",
        "tau2.cli",
        "run",
        "--benchmark",
        "none",
        "--domain",
        "airline",
        "--language",
        "zh",
        "--task-ids",
        *task_ids,
        "--num-trials",
        "1",
        "--workers",
        "0",
        "--max-concurrency",
        str(args.max_concurrency),
        "--agent",
        args.agent,
        "--agent-llm",
        MODEL,
        "--agent-llm-args",
        json.dumps(MODEL_ARGS),
        "--user-llm",
        MODEL,
        "--user-llm-args",
        json.dumps(MODEL_ARGS),
        "--communicate-judge",
        json.dumps({"model": MODEL, "model_args": MODEL_ARGS}),
        "--save-to",
        args.save_to,
    ]
    if args.auto_resume:
        command.append("--auto-resume")
    return subprocess.call(
        command, cwd=ROOT, env={**os.environ, "LANGSMITH_TRACING": "true"}
    )


if __name__ == "__main__":
    raise SystemExit(main())
