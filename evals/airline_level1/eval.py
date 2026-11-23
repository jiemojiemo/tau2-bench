"""Run airline Level 1 cases locally or publish a LangSmith Experiment.

uv run --frozen --extra langsmith python -m evals.airline_level1.eval --upload
"""

import argparse
import os
import sys
from fnmatch import fnmatchcase
from uuid import NAMESPACE_URL, uuid5

from langsmith import Client, evaluate
from langsmith.schemas import Example
from loguru import logger

from .confirmed_cases import CONFIRMED_EXAMPLES
from .dataset import CASES, DATASET_NAME, sync_examples
from .flight_cases import FLIGHT_EXAMPLES


def main() -> int:
    """Run selected cases and report deterministic feedback."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--case", nargs="+")
    parser.add_argument(
        "--filter",
        action="append",
        default=[],
        metavar="PATTERN",
        help="Match case ID, feature or scenario by glob. Repeat to match any pattern.",
    )
    parser.add_argument("--list", action="store_true", help="List matching cases")
    suite = parser.add_mutually_exclusive_group()
    suite.add_argument(
        "--after-confirmation",
        action="store_true",
        help="Run the cases that start from the user's confirmation",
    )
    suite.add_argument(
        "--flight-search", action="store_true", help="Run the flight search cases"
    )
    parser.add_argument(
        "--upload", action="store_true", help="Publish the experiment to LangSmith"
    )
    args = parser.parse_args()
    cases = CASES
    if args.flight_search or args.after_confirmation:
        suite_cases = FLIGHT_EXAMPLES if args.flight_search else CONFIRMED_EXAMPLES
        cases = {case["metadata"]["case_id"]: case for case in suite_cases}
    selected = list(dict.fromkeys(args.case or cases))
    if unknown := set(selected) - cases.keys():
        parser.error(
            f"unknown cases {', '.join(sorted(unknown))}; choose from {', '.join(cases)}"
        )
    if args.filter:
        selected = [
            case_id
            for case_id in selected
            if any(
                fnmatchcase(cases[case_id]["metadata"][field], pattern)
                for pattern in args.filter
                for field in ("case_id", "feature", "scenario")
            )
        ]
    if not selected:
        parser.error("no matching cases; use --list to see the available cases")
    if args.list:
        for case_id in selected:
            metadata = cases[case_id]["metadata"]
            print(f"{case_id}\t{metadata['feature']}\t{metadata['scenario']}")
        print(f"{len(selected)} cases")
        return 0

    from .evaluator import evaluate_case
    from .target import MODEL, REASONING_EFFORT, target

    logger.remove()
    logger.add(sys.stderr, level="WARNING")
    os.environ["LANGSMITH_TRACING"] = "true" if args.upload else "false"
    client = Client()
    if args.upload:
        examples = sync_examples(client)
    else:
        examples = {
            case_id: Example(
                id=uuid5(NAMESPACE_URL, f"{DATASET_NAME}/{case_id}"), **cases[case_id]
            )
            for case_id in selected
        }
    rows = evaluate(
        target,
        data=[examples[case_id] for case_id in selected],
        evaluators=[evaluate_case],
        experiment_prefix="airline-zh-level1",
        metadata={
            "agent": "my_agent",
            "model": MODEL,
            "reasoning_effort": REASONING_EFFORT,
        },
        upload_results=args.upload,
        max_concurrency=2,
        client=client,
    )
    passed = 0
    for row in rows:
        case_id = row["example"].metadata["case_id"]
        results = row["evaluation_results"]["results"]
        overall = next((check for check in results if check.key == "case_pass"), None)
        if row["run"].error:
            print(f"{case_id} ERROR")
        elif overall and overall.score:
            passed += 1
            print(f"{case_id} PASS")
        else:
            print(
                f"{case_id} FAIL ({overall.comment if overall else 'missing feedback'})"
            )
    print(f"Airline Level 1: {passed}/{len(selected)} passed")
    return int(passed != len(selected))


if __name__ == "__main__":
    raise SystemExit(main())
