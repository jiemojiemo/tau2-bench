"""Run airline Level 1 cases locally or publish a LangSmith Experiment.

uv run --frozen --extra langsmith python -m evals.airline_level1.eval --upload
"""

import argparse
import os
import sys
from uuid import NAMESPACE_URL, uuid5

from langsmith import Client, evaluate
from langsmith.schemas import Example
from loguru import logger

from .cases import EXAMPLES
from .confirmed_cases import CONFIRMED_EXAMPLES
from .dataset import (
    CONFIRMED_DATASET_NAME,
    DATASET_NAME,
    FLIGHT_DATASET_NAME,
    sync_examples,
)
from .evaluator import evaluate_booking, evaluate_flight_search
from .flight_cases import FLIGHT_EXAMPLES
from .target import MODEL, REASONING_EFFORT, target


def main() -> int:
    """Run selected cases and report deterministic feedback."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--case", nargs="+")
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
    if args.flight_search:
        suite_cases = FLIGHT_EXAMPLES
        dataset_name = FLIGHT_DATASET_NAME
        evaluator = evaluate_flight_search
        score_key = "flight_search_pass"
        experiment_prefix = "airline-zh-level1-flight-search"
        label = "Flight Search Level 1"
    else:
        suite_cases = CONFIRMED_EXAMPLES if args.after_confirmation else EXAMPLES
        dataset_name = (
            CONFIRMED_DATASET_NAME if args.after_confirmation else DATASET_NAME
        )
        evaluator = evaluate_booking
        score_key = "booking_pass"
        experiment_prefix = "airline-zh-level1-booking"
        label = "Booking Level 1"
    cases = {case["metadata"]["case_id"]: case for case in suite_cases}
    selected = list(dict.fromkeys(args.case or cases))
    if unknown := set(selected) - cases.keys():
        parser.error(
            f"unknown cases {', '.join(sorted(unknown))}; choose from {', '.join(cases)}"
        )

    logger.remove()
    logger.add(sys.stderr, level="WARNING")
    os.environ["LANGSMITH_TRACING"] = "true" if args.upload else "false"
    client = Client()
    if args.upload:
        examples = sync_examples(client, dataset_name, cases)
    else:
        examples = {
            case_id: Example(
                id=uuid5(NAMESPACE_URL, f"{dataset_name}/{case_id}"), **case
            )
            for case_id, case in cases.items()
        }
    rows = evaluate(
        target,
        data=[examples[case_id] for case_id in selected],
        evaluators=[evaluator],
        experiment_prefix=experiment_prefix,
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
        overall = next((check for check in results if check.key == score_key), None)
        if row["run"].error:
            print(f"{case_id} ERROR")
        elif overall and overall.score:
            passed += 1
            print(f"{case_id} PASS")
        else:
            print(
                f"{case_id} FAIL ({overall.comment if overall else 'missing feedback'})"
            )
    print(f"{label}: {passed}/{len(selected)} passed")
    return int(passed != len(selected))


if __name__ == "__main__":
    raise SystemExit(main())
