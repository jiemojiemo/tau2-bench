"""航空取消订单 Level 1 用例。history 是固定对话，user 是本轮输入。"""

import json
from pathlib import Path

CANCEL_DBS = json.loads(
    (Path(__file__).parent / "fixtures" / "cancel_db.json").read_text(encoding="utf-8")
)

CANCEL_EXAMPLES = [
    {
        "metadata": {
            "case_id": "CANCEL-01",
            "level": "level1",
            "feature": "取消航班",
            "scenario": "普通经济舱购票未满 24 小时，行程变更并确认后取消",
        },
        "inputs": {
            "user": "是，确认取消这笔订单。",
            "initial_db": CANCEL_DBS["CANCEL-01"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 TST001。行程变了，请帮我取消这笔订单。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "TST001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_get_reservation_details",
                    "content": (
                        '{"reservation_id": "TST001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "one_way", '
                        '"cabin": "economy", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-16", "price": 1000}], '
                        '"passengers": [{"first_name": "晨", "last_name": "张", "dob": "1990-04-05"}], '
                        '"payment_history": [{"payment_id": "credit_card_1111", "amount": 1000}], '
                        '"created_at": "2024-05-15T10:00:00", '
                        '"total_baggages": 0, '
                        '"nonfree_baggages": 0, '
                        '"insurance": "no", '
                        '"status": null}'
                    ),
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_get_flight_status",
                            "name": "get_flight_status",
                            "arguments": {
                                "flight_number": "HAT001",
                                "date": "2024-05-16",
                            },
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_get_flight_status",
                    "content": "available",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "这张普通经济舱机票购票未满 24 小时。 可以取消 TST001 整笔订单（5 月 16 日杭州到无锡 HAT001）。退款 1000 元将在 5 至 7 个工作日内退回尾号 1111 的信用卡。请确认是否取消。",
                },
            ],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": ["transfer_to_human_agents"],
            "db_actions": [
                {
                    "name": "cancel_reservation",
                    "arguments": {"reservation_id": "TST001"},
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "CANCEL-02",
            "level": "level1",
            "feature": "取消航班",
            "scenario": "基础经济舱购票超过 24 小时，无保险且航班正常，因行程变更无法取消",
        },
        "inputs": {
            "user": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 TST001。行程有变，麻烦帮我取消整笔订单。",
            "initial_db": CANCEL_DBS["CANCEL-02"],
        },
        "outputs": {
            "lookups": {
                "get_reservation_details": {
                    "arguments": {"reservation_id": "TST001"},
                    "result_contains": {
                        "reservation_id": "TST001",
                        "cabin": "basic_economy",
                        "insurance": "no",
                    },
                },
            },
            "forbidden_calls": ["cancel_reservation", "transfer_to_human_agents"],
            "db_actions": [],
        },
    },
    {
        "metadata": {
            "case_id": "CANCEL-03",
            "level": "level1",
            "feature": "取消航班",
            "scenario": "超过 24 小时的无保险基础经济舱，查实航司已取消航班，用户确认后取消订单",
        },
        "inputs": {
            "user": "是，我确认取消整笔订单。",
            "initial_db": CANCEL_DBS["CANCEL-03"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 TST001。听说航空公司取消了这个航班，请核实后帮我取消订单。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "TST001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_get_reservation_details",
                    "content": (
                        '{"reservation_id": "TST001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "one_way", '
                        '"cabin": "basic_economy", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-16", "price": 800}], '
                        '"passengers": [{"first_name": "晨", "last_name": "张", "dob": "1990-04-05"}], '
                        '"payment_history": [{"payment_id": "credit_card_1111", "amount": 800}], '
                        '"created_at": "2024-05-10T10:00:00", '
                        '"total_baggages": 0, '
                        '"nonfree_baggages": 0, '
                        '"insurance": "no", '
                        '"status": null}'
                    ),
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_get_flight_status",
                            "name": "get_flight_status",
                            "arguments": {
                                "flight_number": "HAT001",
                                "date": "2024-05-16",
                            },
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_get_flight_status",
                    "content": "cancelled",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "已查实 HAT001 被航空公司取消。 可以取消 TST001 整笔订单（5 月 16 日杭州到无锡 HAT001）。退款 800 元将在 5 至 7 个工作日内退回尾号 1111 的信用卡。请确认是否取消。",
                },
            ],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": ["transfer_to_human_agents"],
            "db_actions": [
                {
                    "name": "cancel_reservation",
                    "arguments": {"reservation_id": "TST001"},
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "CANCEL-04",
            "level": "level1",
            "feature": "取消航班",
            "scenario": "商务舱往返订单的去程已落地，回程未飞，要求取消整笔订单时转人工",
        },
        "inputs": {
            "user": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 TST001。取消原因是个人行程变更，原定的会议改期了。请帮我取消整笔往返订单。",
            "initial_db": CANCEL_DBS["CANCEL-04"],
        },
        "outputs": {
            "lookups": {
                "get_reservation_details": {
                    "arguments": {"reservation_id": "TST001"},
                    "result_contains": {
                        "reservation_id": "TST001",
                        "flight_type": "round_trip",
                    },
                },
                "get_flight_status": {
                    "arguments": {"flight_number": "HAT001", "date": "2024-05-15"},
                    "result_contains": "landed",
                },
                "transfer_to_human_agents": {"result_contains": "Transfer successful"},
            },
            "forbidden_calls": ["cancel_reservation"],
            "db_actions": [],
        },
    },
    {
        "metadata": {
            "case_id": "CANCEL-05",
            "level": "level1",
            "feature": "取消航班",
            "scenario": "商务舱购票超过 24 小时，无保险，行程变更并确认后取消",
        },
        "inputs": {
            "user": "是，确认取消整笔订单。",
            "initial_db": CANCEL_DBS["CANCEL-05"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 TST001。行程有变，想取消这笔订单。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "TST001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_get_reservation_details",
                    "content": (
                        '{"reservation_id": "TST001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "one_way", '
                        '"cabin": "business", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-16", "price": 2200}], '
                        '"passengers": [{"first_name": "晨", "last_name": "张", "dob": "1990-04-05"}], '
                        '"payment_history": [{"payment_id": "credit_card_1111", "amount": 2200}], '
                        '"created_at": "2024-05-10T10:00:00", '
                        '"total_baggages": 0, '
                        '"nonfree_baggages": 0, '
                        '"insurance": "no", '
                        '"status": null}'
                    ),
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_get_flight_status",
                            "name": "get_flight_status",
                            "arguments": {
                                "flight_number": "HAT001",
                                "date": "2024-05-16",
                            },
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_get_flight_status",
                    "content": "available",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "已查到整笔订单都是商务舱，航班尚未起飞。 可以取消 TST001 整笔订单（5 月 16 日杭州到无锡 HAT001）。退款 2200 元将在 5 至 7 个工作日内退回尾号 1111 的信用卡。请确认是否取消。",
                },
            ],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": ["transfer_to_human_agents"],
            "db_actions": [
                {
                    "name": "cancel_reservation",
                    "arguments": {"reservation_id": "TST001"},
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "CANCEL-06",
            "level": "level1",
            "feature": "取消航班",
            "scenario": "普通经济舱购票超过 24 小时，因旅行保险覆盖的健康原因取消，用户已确认",
        },
        "inputs": {
            "user": "是，确认取消整笔订单。",
            "initial_db": CANCEL_DBS["CANCEL-06"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 TST001。我生病了，医生建议我不要乘机，请帮我取消这笔订单。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "TST001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_get_reservation_details",
                    "content": (
                        '{"reservation_id": "TST001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "one_way", '
                        '"cabin": "economy", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-16", "price": 1000}], '
                        '"passengers": [{"first_name": "晨", "last_name": "张", "dob": "1990-04-05"}], '
                        '"payment_history": [{"payment_id": "credit_card_1111", "amount": 1210}], '
                        '"created_at": "2024-05-10T10:00:00", '
                        '"total_baggages": 0, '
                        '"nonfree_baggages": 0, '
                        '"insurance": "yes", '
                        '"status": null}'
                    ),
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_get_flight_status",
                            "name": "get_flight_status",
                            "arguments": {
                                "flight_number": "HAT001",
                                "date": "2024-05-16",
                            },
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_get_flight_status",
                    "content": "available",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "订单有旅行保险，您因生病需要取消，属于保险覆盖的健康原因。 可以取消 TST001 整笔订单（5 月 16 日杭州到无锡 HAT001）。退款 1210 元将在 5 至 7 个工作日内退回尾号 1111 的信用卡。请确认是否取消。",
                },
            ],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": ["transfer_to_human_agents"],
            "db_actions": [
                {
                    "name": "cancel_reservation",
                    "arguments": {"reservation_id": "TST001"},
                },
            ],
        },
    },
]
