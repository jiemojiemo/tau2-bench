"""Sync the versioned, synthetic airline examples to LangSmith."""

from langsmith import Client
from langsmith.schemas import Example
from langsmith.utils import LangSmithNotFoundError

from .cancel_cases import CANCEL_EXAMPLES
from .cases import EXAMPLES
from .change_cases import CHANGE_EXAMPLES
from .compensation_cases import COMPENSATION_EXAMPLES
from .confirmed_cases import CONFIRMED_EXAMPLES
from .flight_cases import FLIGHT_EXAMPLES

DATASET_NAME = "tau2-airline-zh-level1-v1"
CASES = {
    case["metadata"]["case_id"]: case
    for case in (
        *EXAMPLES,
        *CONFIRMED_EXAMPLES,
        *FLIGHT_EXAMPLES,
        *CANCEL_EXAMPLES,
        *CHANGE_EXAMPLES,
        *COMPENSATION_EXAMPLES,
    )
}


def sync_examples(client: Client) -> dict[str, Example]:
    """Create missing examples and detect drift before running the agent."""
    try:
        dataset = client.read_dataset(dataset_name=DATASET_NAME)
    except LangSmithNotFoundError:
        dataset = client.create_dataset(
            DATASET_NAME, description="航空 Level 1 固定用例与工具、数据库断言"
        )
    existing = list(client.list_examples(dataset_id=dataset.id))
    by_id = {(example.metadata or {}).get("case_id"): example for example in existing}
    if len(by_id) != len(existing) or not by_id.keys() <= CASES.keys():
        raise ValueError(f"Unexpected or duplicate case IDs in {DATASET_NAME}")

    for case_id, example in by_id.items():
        case = CASES[case_id]
        if (example.inputs, example.outputs) != (
            case["inputs"],
            case["outputs"],
        ) or any(
            (example.metadata or {}).get(key) != value
            for key, value in case["metadata"].items()
        ):
            raise ValueError(
                f"{case_id} differs from {DATASET_NAME}; use a new dataset version"
            )

    for case_id, case in CASES.items():
        if case_id not in by_id:
            by_id[case_id] = client.create_example(dataset_id=dataset.id, **case)
    return by_id
