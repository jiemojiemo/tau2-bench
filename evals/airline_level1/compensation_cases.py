"""航空退款与补偿 Level 1 用例。history 是固定对话，user 是本轮输入。"""

import json
from pathlib import Path

COMPENSATION_DBS = json.loads(
    (Path(__file__).parent / "fixtures" / "compensation_db.json").read_text(
        encoding="utf-8"
    )
)

COMPENSATION_EXAMPLES = [
    {
        "metadata": {
            "case_id": "COMP-01",
            "level": "level1",
            "feature": "退款与补偿",
            "scenario": "金卡会员抱怨航司取消，但只查询航班状态",
        },
        "inputs": {
            "user": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 CMP001。原来安排好的行程全被打乱了。帮我看看 5 月 16 日的 HAT001 到底是不是被航司取消了？",
            "initial_db": COMPENSATION_DBS["金卡航司取消"],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": ["send_certificate"],
            "db_actions": [],
        },
    },
    {
        "metadata": {
            "case_id": "COMP-02",
            "level": "level1",
            "feature": "退款与补偿",
            "scenario": "普通会员无保险、基础经济舱，航司取消后主动索要补偿",
        },
        "inputs": {
            "user": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 CMP001。5 月 16 日的 HAT001 被航空公司取消，耽误了我的行程。我是普通会员，没买保险，坐基础经济舱，能给我补偿代金券吗？如果能发，我确认领取。",
            "initial_db": COMPENSATION_DBS["普卡无险基础经济舱取消"],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": ["send_certificate"],
            "db_actions": [],
        },
    },
    {
        "metadata": {
            "case_id": "COMP-03",
            "level": "level1",
            "feature": "退款与补偿",
            "scenario": "银卡会员无保险、普通经济舱，两名乘客因航司取消要求补偿",
        },
        "inputs": {
            "user": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 CMP001。我们 5 月 16 日的 HAT001 被航空公司取消了，耽误了两个人的行程。请核实订单和我的银卡资格，符合规则的话，我确认领取补偿代金券，请直接发到这个账户。",
            "initial_db": COMPENSATION_DBS["银卡双人订单取消"],
        },
        "outputs": {
            "lookups": {
                "get_reservation_details": {
                    "arguments": {"reservation_id": "CMP001"},
                    "result_contains": {
                        "reservation_id": "CMP001",
                        "cabin": "economy",
                        "insurance": "no",
                        "passengers": [
                            {
                                "first_name": "晨",
                                "last_name": "张",
                                "dob": "1990-04-05",
                            },
                            {
                                "first_name": "敏",
                                "last_name": "李",
                                "dob": "1992-06-18",
                            },
                        ],
                    },
                    "before": "send_certificate",
                },
                "get_user_details": {
                    "arguments": {"user_id": "chen_zhang_1001"},
                    "result_contains": {
                        "user_id": "chen_zhang_1001",
                        "membership": "silver",
                    },
                    "before": "send_certificate",
                },
                "get_flight_status": {
                    "arguments": {"flight_number": "HAT001", "date": "2024-05-16"},
                    "result_contains": "cancelled",
                    "before": "send_certificate",
                },
            },
            "forbidden_calls": [],
            "db_actions": [
                {
                    "name": "send_certificate",
                    "arguments": {"user_id": "chen_zhang_1001", "amount": 1400},
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "COMP-04",
            "level": "level1",
            "feature": "退款与补偿",
            "scenario": "普通会员、有保险、普通经济舱，一名乘客因航司取消要求补偿",
        },
        "inputs": {
            "user": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 CMP001。我一个人坐 5 月 16 日的 HAT001，航空公司取消航班给我造成了不便。我是普通会员，订单买了旅行保险。请核实后按规则发补偿券，符合的话我确认直接领取。",
            "initial_db": COMPENSATION_DBS["普卡经济舱有保险取消"],
        },
        "outputs": {
            "lookups": {
                "get_reservation_details": {
                    "arguments": {"reservation_id": "CMP001"},
                    "result_contains": {
                        "reservation_id": "CMP001",
                        "cabin": "economy",
                        "insurance": "yes",
                        "passengers": [
                            {
                                "first_name": "晨",
                                "last_name": "张",
                                "dob": "1990-04-05",
                            },
                        ],
                    },
                    "before": "send_certificate",
                },
                "get_flight_status": {
                    "arguments": {"flight_number": "HAT001", "date": "2024-05-16"},
                    "result_contains": "cancelled",
                    "before": "send_certificate",
                },
            },
            "forbidden_calls": [],
            "db_actions": [
                {
                    "name": "send_certificate",
                    "arguments": {"user_id": "chen_zhang_1001", "amount": 700},
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "COMP-05",
            "level": "level1",
            "feature": "退款与补偿",
            "scenario": "金卡双人订单延误，改签成功后发一张两人份代金券",
        },
        "inputs": {
            "user": "确认按上述方案把两个人都改到 5 月 16 日 HAT002，使用尾号 1111 的信用卡。请先核实原航班延误，改签成功后把补偿代金券发到我的账户。",
            "initial_db": COMPENSATION_DBS["金卡双人订单延误"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 CMP001。听说今天的 HAT001 延误了，耽误了我们两个人的行程。我想改到明天，并要求延误补偿代金券。还是普通经济舱，用档案里的尾号 1111 信用卡。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "CMP001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_get_reservation_details",
                    "content": (
                        '{"reservation_id": "CMP001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "one_way", '
                        '"cabin": "economy", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-15", "price": 1000}], '
                        '"passengers": [{"first_name": "晨", "last_name": "张", "dob": "1990-04-05"}, {"first_name": "敏", "last_name": "李", "dob": "1992-06-18"}], '
                        '"payment_history": [{"payment_id": "credit_card_1111", "amount": 2000}], '
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
                            "id": "call_history_search_direct_flight",
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
                    "id": "call_history_search_direct_flight",
                    "content": (
                        '[{"flight_number": "HAT002", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"status": "available", '
                        '"scheduled_departure_time_est": "09:00:00", '
                        '"scheduled_arrival_time_est": "10:00:00", '
                        '"date": null, '
                        '"available_seats": {"basic_economy": 4, "economy": 4, "business": 0}, '
                        '"prices": {"basic_economy": 800, "economy": 1000, "business": 2200}}]'
                    ),
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_get_user_details",
                            "name": "get_user_details",
                            "arguments": {"user_id": "chen_zhang_1001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_get_user_details",
                    "content": (
                        '{"user_id": "chen_zhang_1001", '
                        '"name": {"first_name": "晨", "last_name": "张"}, '
                        '"address": {"address1": "测试路 1 号", "address2": null, "city": "杭州", "country": "CN", "state": "浙江", "zip": "310000"}, '
                        '"email": "chen@example.test", '
                        '"dob": "1990-04-05", '
                        '"payment_methods": {"credit_card_1111": {"source": "credit_card", "id": "credit_card_1111", "brand": "visa", "last_four": "1111"}}, '
                        '"saved_passengers": [], '
                        '"membership": "gold", '
                        '"reservations": ["CMP001"]}'
                    ),
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "已查到原订单、金卡档案和明天的航班。5 月 16 日 HAT002 有两张普通经济舱票，路线、舱等和总价不变，支付方式是尾号 1111 的信用卡。请确认是否在查实原航班延误后按这个方案改签，并在改签成功后领取补偿券。",
                },
            ],
        },
        "outputs": {
            "lookups": {
                "get_flight_status": {
                    "arguments": {"flight_number": "HAT001", "date": "2024-05-15"},
                    "result_contains": "delayed",
                    "before": "update_reservation_flights",
                },
            },
            "forbidden_calls": ["book_reservation", "cancel_reservation"],
            "db_actions": [
                {
                    "name": "update_reservation_flights",
                    "arguments": {
                        "reservation_id": "CMP001",
                        "cabin": "economy",
                        "flights": [
                            {"flight_number": "HAT002", "date": "2024-05-16"},
                        ],
                        "payment_id": "credit_card_1111",
                    },
                },
                {
                    "name": "send_certificate",
                    "arguments": {"user_id": "chen_zhang_1001", "amount": 700},
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "COMP-06",
            "level": "level1",
            "feature": "退款与补偿",
            "scenario": "普通会员无保险、商务舱延误，取消并退款后发券",
        },
        "inputs": {
            "user": "是，确认取消 CMP001 整笔订单并原路退款。请核实我投诉的航班延误，取消成功后也把延误补偿券发到这个账户。",
            "initial_db": COMPENSATION_DBS["普卡无险商务舱延误"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 CMP001。我一个人订了今天的 HAT001 商务舱，听说航班延误了，我要取消订单，也明确要求延误补偿。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "CMP001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_get_reservation_details",
                    "content": (
                        '{"reservation_id": "CMP001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "one_way", '
                        '"cabin": "business", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-15", "price": 2200}], '
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
                    "content": "查到订单 CMP001 是 5 月 15 日杭州到无锡 HAT001 的单程商务舱，¥2,200 付自尾号 1111 的信用卡。请确认是否取消整笔订单并将 ¥2,200 原路退回。核实延误后，补偿券会在取消成功后发放。",
                },
            ],
        },
        "outputs": {
            "lookups": {
                "get_flight_status": {
                    "arguments": {"flight_number": "HAT001", "date": "2024-05-15"},
                    "result_contains": "delayed",
                    "before": "cancel_reservation",
                },
            },
            "forbidden_calls": ["book_reservation", "update_reservation_flights"],
            "db_actions": [
                {
                    "name": "cancel_reservation",
                    "arguments": {"reservation_id": "CMP001"},
                },
                {
                    "name": "send_certificate",
                    "arguments": {"user_id": "chen_zhang_1001", "amount": 350},
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "COMP-07",
            "level": "level1",
            "feature": "退款与补偿",
            "scenario": "符合资格的用户遇到延误，只要求补偿并明确保留行程",
        },
        "inputs": {
            "user": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 CMP001。今天的 HAT001 延误了，我是金卡会员。这对我们两个人影响很大。我只想要补偿代金券，原航班照坐，不改签也不取消。",
            "initial_db": COMPENSATION_DBS["金卡双人订单延误"],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": [
                "send_certificate",
                "update_reservation_flights",
                "cancel_reservation",
            ],
            "db_actions": [],
        },
    },
    {
        "metadata": {
            "case_id": "COMP-08",
            "level": "level1",
            "feature": "退款与补偿",
            "scenario": "延误改签已经报价，用户尚未确认但要求先发补偿",
        },
        "inputs": {
            "user": "改签我还要考虑，还没确认。订单先保留在原来那班，但能不能先把延误补偿券发给我？",
            "initial_db": COMPENSATION_DBS["金卡双人订单延误"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 CMP001。我们两个人今天 HAT001 延误了，我想看看能否改到明天，也想要补偿代金券。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "CMP001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_get_reservation_details",
                    "content": (
                        '{"reservation_id": "CMP001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "one_way", '
                        '"cabin": "economy", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-15", "price": 1000}], '
                        '"passengers": [{"first_name": "晨", "last_name": "张", "dob": "1990-04-05"}, {"first_name": "敏", "last_name": "李", "dob": "1992-06-18"}], '
                        '"payment_history": [{"payment_id": "credit_card_1111", "amount": 2000}], '
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
                                "date": "2024-05-15",
                            },
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_get_flight_status",
                    "content": "delayed",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_search_direct_flight",
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
                    "id": "call_history_search_direct_flight",
                    "content": (
                        '[{"flight_number": "HAT002", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"status": "available", '
                        '"scheduled_departure_time_est": "09:00:00", '
                        '"scheduled_arrival_time_est": "10:00:00", '
                        '"date": null, '
                        '"available_seats": {"basic_economy": 4, "economy": 4, "business": 0}, '
                        '"prices": {"basic_economy": 800, "economy": 1000, "business": 2200}}]'
                    ),
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "已核实今天 HAT001 延误，明天 HAT002 同路线、同舱等有两张票，总价不变。您是否确认改签？",
                },
            ],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": [
                "send_certificate",
                "update_reservation_flights",
                "cancel_reservation",
            ],
            "db_actions": [],
        },
    },
    {
        "metadata": {
            "case_id": "COMP-09",
            "level": "level1",
            "feature": "退款与补偿",
            "scenario": "用户以为航班被取消，但实际正常有票",
        },
        "inputs": {
            "user": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 CMP001。我听说 5 月 16 日的 HAT001 被航司取消了。我是金卡会员，请先查实，符合规则的话我确认领取航班取消补偿券。",
            "initial_db": COMPENSATION_DBS["金卡航班正常"],
        },
        "outputs": {
            "lookups": {
                "get_flight_status": {
                    "arguments": {"flight_number": "HAT001", "date": "2024-05-16"},
                    "result_contains": "available",
                },
            },
            "forbidden_calls": ["send_certificate"],
            "db_actions": [],
        },
    },
    {
        "metadata": {
            "case_id": "COMP-10",
            "level": "level1",
            "feature": "退款与补偿",
            "scenario": "正常航班仅因服务态度问题要求补偿",
        },
        "inputs": {
            "user": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 CMP001。5 月 16 日的 HAT001 航班安排没问题，也没有取消或延误。我要投诉客服服务态度差，我是金卡会员，希望发一张代金券补偿。",
            "initial_db": COMPENSATION_DBS["金卡航班正常"],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": ["send_certificate"],
            "db_actions": [],
        },
    },
]
