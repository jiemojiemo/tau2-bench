"""Sync the versioned, synthetic airline examples to LangSmith."""

from langsmith import Client
from langsmith.schemas import Example
from langsmith.utils import LangSmithNotFoundError

DATASET_NAME = "tau2-airline-zh-level1-booking-v8"
CONFIRMED_DATASET_NAME = "tau2-airline-zh-level1-booking-confirmed-v3"
FLIGHT_DATASET_NAME = "tau2-airline-zh-level1-flight-search-v1"


def sync_examples(client: Client, dataset_name: str, cases: dict) -> dict[str, Example]:
    """Create missing examples and detect drift before running the agent."""
    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
    except LangSmithNotFoundError:
        dataset = client.create_dataset(
            dataset_name, description="航空 Level 1 固定用例与工具调用断言"
        )
    existing = list(client.list_examples(dataset_id=dataset.id))
    by_id = {(example.metadata or {}).get("case_id"): example for example in existing}
    if len(by_id) != len(existing) or not by_id.keys() <= cases.keys():
        raise ValueError(f"Unexpected or duplicate case IDs in {dataset_name}")

    for case_id, example in by_id.items():
        case = cases[case_id]
        if (example.inputs, example.outputs) != (
            case["inputs"],
            case["outputs"],
        ) or any(
            (example.metadata or {}).get(key) != value
            for key, value in case["metadata"].items()
        ):
            raise ValueError(
                f"{case_id} differs from {dataset_name}; use a new dataset version"
            )

    for case_id, case in cases.items():
        if case_id not in by_id:
            by_id[case_id] = client.create_example(dataset_id=dataset.id, **case)
    return by_id
