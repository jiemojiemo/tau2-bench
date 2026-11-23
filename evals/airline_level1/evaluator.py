"""Score the tool calls and state after the evaluated user turn."""

import json

from tau2.data_model.tasks import InitialState
from tau2.environment.toolkit import ToolType

from .target import booking_environment

FLIGHT_QUERY_TOOLS = {
    "search_direct_flight",
    "search_onestop_flight",
    "get_flight_status",
}


def _contains_fields(actual, expected) -> bool:
    if isinstance(expected, list):
        return (
            isinstance(actual, list)
            and len(actual) == len(expected)
            and all(
                _contains_fields(item, fields) for item, fields in zip(actual, expected)
            )
        )
    if isinstance(actual, list):
        return any(_contains_fields(item, expected) for item in actual)
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and _contains_fields(actual[key], value)
            for key, value in expected.items()
        )
    return actual == expected


def _expected_db_hash(inputs: dict, actions: list[dict]) -> str | None:
    environment = booking_environment(inputs["initial_db"])
    history = InitialState(message_history=inputs.get("history", []))
    environment.set_state(None, None, history.message_history)
    for action in actions:
        environment.make_tool_call(action["name"], **action["arguments"])
    return environment.get_db_hash()


def evaluate_booking(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    """Assert tool calls and compare the final database for write cases."""
    calls = (outputs or {}).get("tool_calls")
    if calls is None:
        return {"key": "case_pass", "score": False, "comment": "缺少工具调用记录"}

    failures = [
        f"禁止调用 {name}"
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
            failures.append(f"缺少参数正确且成功的 {name} 调用")
            continue
        if not any(
            _contains_fields(
                json.loads(call.get("result") or "null"), expected["result_contains"]
            )
            for call in matching_calls
        ):
            failures.append(f"{name} 返回值未匹配 {expected['result_contains']}")
    db_match = None
    if (actions := reference_outputs.get("db_actions")) is not None:
        action_names = {action["name"] for action in actions}
        actual_actions = [
            {key: call[key] for key in ("name", "arguments", "ok")}
            for call in calls
            if call["name"] in action_names
        ]
        if actual_actions != [{**action, "ok": True} for action in actions]:
            failures.append("写库调用的次数、参数或执行结果与预期不符")
        expected_db_hash = _expected_db_hash(inputs, actions)
        db_match = (
            expected_db_hash is not None and outputs.get("db_hash") == expected_db_hash
        )
        if not db_match:
            failures.append("最终数据库与预期不一致")

    booking_pass = {
        "key": "case_pass",
        "score": not failures,
        "comment": "；".join(failures),
    }
    if db_match is None:
        return booking_pass
    return {"results": [booking_pass, {"key": "db_match", "score": db_match}]}


def evaluate_flight_search(
    inputs: dict, outputs: dict, reference_outputs: dict
) -> dict:
    """Check the sequence, arguments, and results of the requested flight lookups."""
    calls = (outputs or {}).get("tool_calls") or []
    queries = [call for call in calls if call["name"] in FLIGHT_QUERY_TOOLS]
    expected_queries = reference_outputs["queries"]
    actual_names = [call["name"] for call in queries]
    expected_names = [query["name"] for query in expected_queries]
    failures = []
    if actual_names != expected_names:
        failures.append(f"预期查询顺序 {expected_names}，实际 {actual_names}")
    else:
        if any(
            first["step"] >= second["step"]
            for first, second in zip(queries, queries[1:])
        ):
            failures.append("必须拿到上一次查询的结果，再发起下一次查询")
        for call, expected in zip(queries, expected_queries):
            name = call["name"]
            if not call["ok"] or call["arguments"] != expected["arguments"]:
                failures.append(f"{name} 调用失败或参数不符，实际 {call['arguments']}")
                continue
            expected_result = expected["result"]
            result = call["result"]
            if isinstance(expected_result, list):
                result = json.loads(result or "null")
                if name == "search_direct_flight" and isinstance(result, list):
                    result = sorted(result, key=lambda flight: flight["flight_number"])
                    expected_result = sorted(
                        expected_result, key=lambda flight: flight["flight_number"]
                    )
            if not _contains_fields(result, expected_result):
                failures.append(f"{name} 返回值未匹配 {expected_result}")

    tools = booking_environment(inputs["initial_db"]).tools
    writes = [
        call["name"]
        for call in calls
        if tools.has_tool(call["name"])
        and tools.tool_type(call["name"]) == ToolType.WRITE
    ]
    if writes:
        failures.append(f"查询航班时调用了写库工具 {writes}")
    return {
        "key": "case_pass",
        "score": not failures,
        "comment": "；".join(failures),
    }


def evaluate_case(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    """Run the checks for this case's expected outputs."""
    if "queries" in reference_outputs:
        return evaluate_flight_search(inputs, outputs, reference_outputs)
    return evaluate_booking(inputs, outputs, reference_outputs)
