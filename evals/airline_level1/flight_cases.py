"""航空查询 Level 1 单轮用例，断言查询路径和工具返回值。"""

import json
from copy import deepcopy

from tau2.domains.airline.data_model import DirectFlight


def _available_flight(
    flight_number: str,
    origin: str,
    destination: str,
    date: str,
    departure: str,
    arrival: str,
) -> dict:
    return {
        "flight_number": flight_number,
        "origin": origin,
        "destination": destination,
        "scheduled_departure_time_est": departure,
        "scheduled_arrival_time_est": arrival,
        "dates": {
            date: {
                "status": "available",
                "available_seats": {"economy": 4, "business": 0, "basic_economy": 4},
                "prices": {"economy": 1000, "business": 2200, "basic_economy": 800},
            },
        },
    }


SEARCH_DB = {
    "flights": {
        flight["flight_number"]: flight
        for flight in (
            _available_flight(
                "HAT001", "HGH", "WUX", "2024-05-16", "09:00:00", "10:00:00"
            ),
            _available_flight(
                "HAT002", "HGH", "WUX", "2024-05-16", "18:00:00", "19:00:00"
            ),
            _available_flight(
                "HAT003", "HGH", "WUX", "2024-05-17", "12:00:00", "13:00:00"
            ),
            _available_flight(
                "HAT011", "HGH", "CSX", "2024-05-16", "08:00:00", "09:20:00"
            ),
            _available_flight(
                "HAT012", "CSX", "SZX", "2024-05-16", "11:00:00", "12:15:00"
            ),
        )
    },
    "users": {},
    "reservations": {},
}

DELAYED_DB = deepcopy(SEARCH_DB)
DELAYED_DB["flights"]["HAT001"]["dates"]["2024-05-16"] = {
    "status": "delayed",
    "estimated_departure_time_est": "2024-05-16T10:30:00",
    "estimated_arrival_time_est": "2024-05-16T11:30:00",
}

# The recorded lookup in FLIGHT-05 uses the same schema as the live tool result.
MAY_16_DIRECT_RESULTS = [
    DirectFlight.model_validate({**flight, **flight["dates"]["2024-05-16"]}).model_dump(
        mode="json"
    )
    for flight in (SEARCH_DB["flights"]["HAT001"], SEARCH_DB["flights"]["HAT002"])
]

FLIGHT_EXAMPLES = [
    {
        "metadata": {
            "case_id": "FLIGHT-01",
            "level": "level1",
            "feature": "查询航班",
            "scenario": "同一天有多班直飞，查询航班号和起飞时间",
        },
        "inputs": {
            "user": "查一下 2024 年 5 月 16 日杭州萧山（HGH）到无锡硕放（WUX）有哪些直飞，几点起飞？",
            "initial_db": SEARCH_DB,
        },
        "outputs": {
            "queries": [
                {
                    "name": "search_direct_flight",
                    "arguments": {
                        "origin": "HGH",
                        "destination": "WUX",
                        "date": "2024-05-16",
                    },
                    "result": [
                        {
                            "flight_number": "HAT001",
                            "scheduled_departure_time_est": "09:00:00",
                        },
                        {
                            "flight_number": "HAT002",
                            "scheduled_departure_time_est": "18:00:00",
                        },
                    ],
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "FLIGHT-02",
            "level": "level1",
            "feature": "查询航班",
            "scenario": "直飞查不到时，继续查询一次中转",
        },
        "inputs": {
            "user": (
                "查一下 2024 年 5 月 16 日杭州萧山（HGH）到深圳宝安（SZX）的航班。"
                "优先直飞，如果没有直飞，再帮我查一次中转。只查询。"
            ),
            "initial_db": SEARCH_DB,
        },
        "outputs": {
            "queries": [
                {
                    "name": "search_direct_flight",
                    "arguments": {
                        "origin": "HGH",
                        "destination": "SZX",
                        "date": "2024-05-16",
                    },
                    "result": [],
                },
                {
                    "name": "search_onestop_flight",
                    "arguments": {
                        "origin": "HGH",
                        "destination": "SZX",
                        "date": "2024-05-16",
                    },
                    "result": [
                        [
                            {
                                "flight_number": "HAT011",
                                "origin": "HGH",
                                "destination": "CSX",
                                "date": "2024-05-16",
                            },
                            {
                                "flight_number": "HAT012",
                                "origin": "CSX",
                                "destination": "SZX",
                                "date": "2024-05-16",
                            },
                        ],
                    ],
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "FLIGHT-03",
            "level": "level1",
            "feature": "查询航班",
            "scenario": "直飞查不到，用户明确拒绝中转",
        },
        "inputs": {
            "user": (
                "查一下 2024 年 5 月 16 日杭州萧山（HGH）到深圳宝安（SZX）的航班。"
                "只看直飞，没有就算了，不要查中转。"
            ),
            "initial_db": SEARCH_DB,
        },
        "outputs": {
            "queries": [
                {
                    "name": "search_direct_flight",
                    "arguments": {
                        "origin": "HGH",
                        "destination": "SZX",
                        "date": "2024-05-16",
                    },
                    "result": [],
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "FLIGHT-04",
            "level": "level1",
            "feature": "查询航班",
            "scenario": "用航班号和日期查询是否延误",
        },
        "inputs": {
            "user": "请帮我查一下 2024 年 5 月 16 日的 HAT001 航班延误了吗？",
            "initial_db": DELAYED_DB,
        },
        "outputs": {
            "queries": [
                {
                    "name": "get_flight_status",
                    "arguments": {"flight_number": "HAT001", "date": "2024-05-16"},
                    "result": "delayed",
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "FLIGHT-05",
            "level": "level1",
            "feature": "查询航班",
            "scenario": "沿用历史中的路线，按追问的新日期重查",
        },
        "inputs": {
            "initial_db": SEARCH_DB,
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "查一下 2024 年 5 月 16 日杭州萧山（HGH）到无锡硕放（WUX）的直飞航班。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_may_16",
                            "name": "search_direct_flight",
                            "arguments": {
                                "origin": "HGH",
                                "destination": "WUX",
                                "date": "2024-05-16",
                            },
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_may_16",
                    "content": json.dumps(MAY_16_DIRECT_RESULTS),
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "2024 年 5 月 16 日杭州萧山到无锡硕放有两班直飞，HAT001 09:00 起飞，HAT002 18:00 起飞。",
                },
            ],
            "user": "那 17 号呢？",
        },
        "outputs": {
            "queries": [
                {
                    "name": "search_direct_flight",
                    "arguments": {
                        "origin": "HGH",
                        "destination": "WUX",
                        "date": "2024-05-17",
                    },
                    "result": [
                        {
                            "flight_number": "HAT003",
                            "scheduled_departure_time_est": "12:00:00",
                        },
                    ],
                },
            ],
        },
    },
]
