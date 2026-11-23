"""Score pre-booking tool calls and their results."""

import json


def _contains_fields(actual, expected) -> bool:
    if isinstance(actual, list):
        return any(_contains_fields(item, expected) for item in actual)
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and _contains_fields(actual[key], value)
            for key, value in expected.items()
        )
    return actual == expected


def evaluate_booking(outputs: dict, reference_outputs: dict) -> dict:
    """Assert required lookups and flag forbidden tool calls."""
    calls = (outputs or {}).get("tool_calls")
    if calls is None:
        return {"key": "booking_pass", "score": False, "comment": "缺少工具调用记录"}

    failures = [
        f"下单前禁止调用 {name}"
        for name in reference_outputs["forbidden_calls"]
        if any(call["name"] == name for call in calls)
    ]
    for name, expected in reference_outputs["lookups"].items():
        matching_calls = [
            call
            for call in calls
            if call["name"] == name
            and call["arguments"] == expected["arguments"]
            and call["ok"]
        ]
        if not matching_calls:
            failures.append(f"缺少查询 {name}")
            continue
        if not any(
            _contains_fields(
                json.loads(call.get("result") or "null"), expected["result_contains"]
            )
            for call in matching_calls
        ):
            failures.append(f"{name} 返回值未匹配 {expected['result_contains']}")
    return {
        "key": "booking_pass",
        "score": not failures,
        "comment": "；".join(failures),
    }
