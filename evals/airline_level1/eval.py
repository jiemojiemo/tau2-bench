"""Run the five airline booking cases locally or publish a LangSmith Experiment.

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
from .dataset import DATASET_NAME, sync_examples
from .evaluator import evaluate_booking
from .target import MODEL, REASONING_EFFORT, target


def main() -> int:
    """Run selected cases and report deterministic feedback."""
    cases = {case["metadata"]["case_id"]: case for case in EXAMPLES}
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--case", nargs="+", choices=cases)
    parser.add_argument(
        "--upload", action="store_true", help="Publish the experiment to LangSmith"
    )
    args = parser.parse_args()
    selected = list(dict.fromkeys(args.case or cases))

    logger.remove()
    logger.add(sys.stderr, level="WARNING")
    os.environ["LANGSMITH_TRACING"] = "true" if args.upload else "false"
    client = Client()
    if args.upload:
        examples = sync_examples(client)
    else:
        examples = {
            case_id: Example(
                id=uuid5(NAMESPACE_URL, f"{DATASET_NAME}/{case_id}"), **case
            )
            for case_id, case in cases.items()
        }
    rows = evaluate(
        target,
        data=[examples[case_id] for case_id in selected],
        evaluators=[evaluate_booking],
        experiment_prefix="airline-zh-level1-booking",
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
        overall = next(
            (check for check in results if check.key == "booking_pass"), None
        )
        if row["run"].error:
            print(f"{case_id} ERROR")
        elif overall and overall.score:
            passed += 1
            print(f"{case_id} PASS")
        else:
            print(
                f"{case_id} FAIL ({overall.comment if overall else 'missing feedback'})"
            )
    print(f"Booking Level 1: {passed}/{len(selected)} passed")
    return int(passed != len(selected))


if __name__ == "__main__":
    raise SystemExit(main())
