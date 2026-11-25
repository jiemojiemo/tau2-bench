"""修改航班 Level 1 用例。history 是固定对话，user 是本轮输入。"""

import json
from pathlib import Path

CHANGE_DBS = json.loads(
    (Path(__file__).parent / "fixtures" / "change_db.json").read_text(encoding="utf-8")
)

CHANGE_EXAMPLES = [
    # 更改航段
    {
        "metadata": {
            "case_id": "CHANGE-FLIGHT-01",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "普通经济舱单程改到次日，同价且用户已确认",
        },
        "inputs": {
            "user": "是，确认改到 5 月 17 日的 HAT001。若需要支付方式，用档案里尾号 1111 的信用卡。",
            "initial_db": CHANGE_DBS["单程同价"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。请把 5 月 16 日杭州到无锡的单程票改到 5 月 17 日，还是普通经济舱，用档案里尾号 1111 的信用卡。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_1_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "MOD001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_1_get_reservation_details",
                    "content": (
                        '{"reservation_id": "MOD001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "one_way", '
                        '"cabin": "economy", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-16", "price": 1000}], '
                        '"passengers": [{"first_name": "晨", "last_name": "张", "dob": "1990-04-05"}], '
                        '"payment_history": [{"payment_id": "credit_card_1111", "amount": 1000}], '
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
                            "id": "call_history_3_search_direct_flight",
                            "name": "search_direct_flight",
                            "arguments": {
                                "origin": "HGH",
                                "destination": "WUX",
                                "date": "2024-05-17",
                            },
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_3_search_direct_flight",
                    "content": '[{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "status": "available", "scheduled_departure_time_est": "09:00:00", "scheduled_arrival_time_est": "10:00:00", "date": null, "available_seats": {"basic_economy": 4, "economy": 4, "business": 4}, "prices": {"basic_economy": 800, "economy": 1000, "business": 2200}}]',
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_5_get_user_details",
                            "name": "get_user_details",
                            "arguments": {"user_id": "chen_zhang_1001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_5_get_user_details",
                    "content": (
                        '{"user_id": "chen_zhang_1001", '
                        '"name": {"first_name": "晨", "last_name": "张"}, '
                        '"address": {"address1": "测试路 1 号", "address2": null, "city": "杭州", "country": "CN", "state": "浙江", "zip": "310000"}, '
                        '"email": "chen@example.test", '
                        '"dob": "1990-04-05", '
                        '"payment_methods": {"credit_card_1111": {"source": "credit_card", "id": "credit_card_1111", "brand": "visa", "last_four": "1111"}, "credit_card_3333": {"source": "credit_card", "id": "credit_card_3333", "brand": "mastercard", "last_four": "3333"}, "gift_card_2222": {"source": "gift_card", "id": "gift_card_2222", "amount": 500.0}, "certificate_4444": {"source": "certificate", "id": "certificate_4444", "amount": 600.0}}, '
                        '"saved_passengers": [], '
                        '"membership": "regular", '
                        '"reservations": ["MOD001"]}'
                    ),
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "5 月 17 日同航线 HAT001 普通经济舱有票，¥1,000，与原价相同。行程仍是杭州往无锡单程，支付方式是档案里尾号 1111 的信用卡。请确认是否改签。",
                },
            ],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": [
                "book_reservation",
                "cancel_reservation",
                "send_certificate",
                "update_reservation_baggages",
                "update_reservation_passengers",
            ],
            "db_actions": [
                {
                    "name": "update_reservation_flights",
                    "arguments": {
                        "reservation_id": "MOD001",
                        "cabin": "economy",
                        "flights": [
                            {"flight_number": "HAT001", "date": "2024-05-17"},
                        ],
                        "payment_id": "credit_card_1111",
                    },
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "CHANGE-FLIGHT-02",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "基础经济舱改日期，新航班有票但原舱等不可改签",
        },
        "inputs": {
            "user": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。我想把 5 月 16 日杭州到无锡的 HAT001 改到 5 月 17 日，仍坐基础经济舱。就用档案里尾号 1111 的信用卡。我确认想改这一天。",
            "initial_db": CHANGE_DBS["基础经济舱单程"],
        },
        "outputs": {
            "lookups": {
                "get_reservation_details": {
                    "arguments": {"reservation_id": "MOD001"},
                    "result_contains": {
                        "reservation_id": "MOD001",
                        "cabin": "basic_economy",
                    },
                },
            },
            "forbidden_calls": [
                "book_reservation",
                "cancel_reservation",
                "send_certificate",
                "update_reservation_baggages",
                "update_reservation_flights",
                "update_reservation_passengers",
            ],
            "db_actions": [],
        },
    },
    {
        "metadata": {
            "case_id": "CHANGE-FLIGHT-03",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "只改往返回程，保留的去程按原订单价格结算",
        },
        "inputs": {
            "user": "是，确认保留原去程，把回程改到 5 月 19 日，用尾号 1111 的信用卡补 ¥400。",
            "initial_db": CHANGE_DBS["往返只改回程"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。我只想把 5 月 18 日无锡飞杭州的回程改到 5 月 19 日。去程照旧，继续坐普通经济舱，用尾号 1111 的信用卡补差价。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_1_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "MOD001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_1_get_reservation_details",
                    "content": (
                        '{"reservation_id": "MOD001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "round_trip", '
                        '"cabin": "economy", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-16", "price": 1000}, {"flight_number": "HAT002", "origin": "WUX", "destination": "HGH", "date": "2024-05-18", "price": 800}], '
                        '"passengers": [{"first_name": "晨", "last_name": "张", "dob": "1990-04-05"}], '
                        '"payment_history": [{"payment_id": "credit_card_1111", "amount": 1800}], '
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
                            "id": "call_history_3_search_direct_flight",
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
                    "id": "call_history_3_search_direct_flight",
                    "content": '[{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "status": "available", "scheduled_departure_time_est": "09:00:00", "scheduled_arrival_time_est": "10:00:00", "date": null, "available_seats": {"basic_economy": 4, "economy": 4, "business": 4}, "prices": {"basic_economy": 800, "economy": 1500, "business": 2200}}]',
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_5_search_direct_flight",
                            "name": "search_direct_flight",
                            "arguments": {
                                "origin": "WUX",
                                "destination": "HGH",
                                "date": "2024-05-19",
                            },
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_5_search_direct_flight",
                    "content": '[{"flight_number": "HAT002", "origin": "WUX", "destination": "HGH", "status": "available", "scheduled_departure_time_est": "11:00:00", "scheduled_arrival_time_est": "12:00:00", "date": null, "available_seats": {"basic_economy": 4, "economy": 4, "business": 4}, "prices": {"basic_economy": 800, "economy": 1200, "business": 2200}}]',
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_7_get_user_details",
                            "name": "get_user_details",
                            "arguments": {"user_id": "chen_zhang_1001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_7_get_user_details",
                    "content": (
                        '{"user_id": "chen_zhang_1001", '
                        '"name": {"first_name": "晨", "last_name": "张"}, '
                        '"address": {"address1": "测试路 1 号", "address2": null, "city": "杭州", "country": "CN", "state": "浙江", "zip": "310000"}, '
                        '"email": "chen@example.test", '
                        '"dob": "1990-04-05", '
                        '"payment_methods": {"credit_card_1111": {"source": "credit_card", "id": "credit_card_1111", "brand": "visa", "last_four": "1111"}, "credit_card_3333": {"source": "credit_card", "id": "credit_card_3333", "brand": "mastercard", "last_four": "3333"}, "gift_card_2222": {"source": "gift_card", "id": "gift_card_2222", "amount": 500.0}, "certificate_4444": {"source": "certificate", "id": "certificate_4444", "amount": 600.0}}, '
                        '"saved_passengers": [], '
                        '"membership": "regular", '
                        '"reservations": ["MOD001"]}'
                    ),
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "5 月 16 日 HAT001 去程保留，原价 ¥1,000，今天查询现价 ¥1,500。回程改为 5 月 19 日 HAT002 普通经济舱，¥1,200，原回程 ¥800。只需补 ¥400，使用档案里尾号 1111 的信用卡。请确认。",
                },
            ],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": [
                "book_reservation",
                "cancel_reservation",
                "send_certificate",
                "update_reservation_baggages",
                "update_reservation_passengers",
            ],
            "db_actions": [
                {
                    "name": "update_reservation_flights",
                    "arguments": {
                        "reservation_id": "MOD001",
                        "cabin": "economy",
                        "flights": [
                            {"flight_number": "HAT001", "date": "2024-05-16"},
                            {"flight_number": "HAT002", "date": "2024-05-19"},
                        ],
                        "payment_id": "credit_card_1111",
                    },
                },
            ],
        },
    },
    # 更改舱等
    {
        "metadata": {
            "case_id": "CHANGE-CABIN-01",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "基础经济舱保留同航班升到普通经济舱，补差价",
        },
        "inputs": {
            "user": "是，确认保留原航班，升到普通经济舱，用尾号 1111 的信用卡补 ¥200。",
            "initial_db": CHANGE_DBS["基础经济舱单程"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。我不改航班，只想把 5 月 16 日 HAT001 的基础经济舱升到普通经济舱，用档案里尾号 1111 的信用卡。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_1_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "MOD001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_1_get_reservation_details",
                    "content": (
                        '{"reservation_id": "MOD001", '
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
                            "id": "call_history_3_search_direct_flight",
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
                    "id": "call_history_3_search_direct_flight",
                    "content": '[{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "status": "available", "scheduled_departure_time_est": "09:00:00", "scheduled_arrival_time_est": "10:00:00", "date": null, "available_seats": {"basic_economy": 4, "economy": 4, "business": 4}, "prices": {"basic_economy": 800, "economy": 1000, "business": 2200}}]',
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_5_get_user_details",
                            "name": "get_user_details",
                            "arguments": {"user_id": "chen_zhang_1001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_5_get_user_details",
                    "content": (
                        '{"user_id": "chen_zhang_1001", '
                        '"name": {"first_name": "晨", "last_name": "张"}, '
                        '"address": {"address1": "测试路 1 号", "address2": null, "city": "杭州", "country": "CN", "state": "浙江", "zip": "310000"}, '
                        '"email": "chen@example.test", '
                        '"dob": "1990-04-05", '
                        '"payment_methods": {"credit_card_1111": {"source": "credit_card", "id": "credit_card_1111", "brand": "visa", "last_four": "1111"}, "credit_card_3333": {"source": "credit_card", "id": "credit_card_3333", "brand": "mastercard", "last_four": "3333"}, "gift_card_2222": {"source": "gift_card", "id": "gift_card_2222", "amount": 500.0}, "certificate_4444": {"source": "certificate", "id": "certificate_4444", "amount": 600.0}}, '
                        '"saved_passengers": [], '
                        '"membership": "regular", '
                        '"reservations": ["MOD001"]}'
                    ),
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "5 月 16 日 HAT001 普通经济舱有票，航班号和日期保持不变。现价 ¥1,000，原价 ¥800，需从尾号 1111 的信用卡收 ¥200 差价。请确认。",
                },
            ],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": [
                "book_reservation",
                "cancel_reservation",
                "send_certificate",
                "update_reservation_baggages",
                "update_reservation_passengers",
            ],
            "db_actions": [
                {
                    "name": "update_reservation_flights",
                    "arguments": {
                        "reservation_id": "MOD001",
                        "cabin": "economy",
                        "flights": [
                            {"flight_number": "HAT001", "date": "2024-05-16"},
                        ],
                        "payment_id": "credit_card_1111",
                    },
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "CHANGE-CABIN-02",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "全未飞的往返订单整单从商务舱降到普通经济舱，退差价",
        },
        "inputs": {
            "user": "是，确认去程和回程都改成普通经济舱，原航班和日期不变，差价退到尾号 1111 的信用卡。",
            "initial_db": CHANGE_DBS["商务舱往返"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。请保留往返航班和日期，把两个航段都从商务舱降到普通经济舱，退款退到档案里尾号 1111 的信用卡。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_1_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "MOD001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_1_get_reservation_details",
                    "content": (
                        '{"reservation_id": "MOD001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "round_trip", '
                        '"cabin": "business", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-16", "price": 2200}, {"flight_number": "HAT002", "origin": "WUX", "destination": "HGH", "date": "2024-05-18", "price": 2200}], '
                        '"passengers": [{"first_name": "晨", "last_name": "张", "dob": "1990-04-05"}], '
                        '"payment_history": [{"payment_id": "credit_card_1111", "amount": 4400}], '
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
                            "id": "call_history_3_search_direct_flight",
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
                    "id": "call_history_3_search_direct_flight",
                    "content": '[{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "status": "available", "scheduled_departure_time_est": "09:00:00", "scheduled_arrival_time_est": "10:00:00", "date": null, "available_seats": {"basic_economy": 4, "economy": 4, "business": 4}, "prices": {"basic_economy": 800, "economy": 1000, "business": 2200}}]',
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_5_search_direct_flight",
                            "name": "search_direct_flight",
                            "arguments": {
                                "origin": "WUX",
                                "destination": "HGH",
                                "date": "2024-05-18",
                            },
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_5_search_direct_flight",
                    "content": '[{"flight_number": "HAT002", "origin": "WUX", "destination": "HGH", "status": "available", "scheduled_departure_time_est": "11:00:00", "scheduled_arrival_time_est": "12:00:00", "date": null, "available_seats": {"basic_economy": 4, "economy": 4, "business": 4}, "prices": {"basic_economy": 800, "economy": 1000, "business": 2200}}]',
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_7_get_user_details",
                            "name": "get_user_details",
                            "arguments": {"user_id": "chen_zhang_1001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_7_get_user_details",
                    "content": (
                        '{"user_id": "chen_zhang_1001", '
                        '"name": {"first_name": "晨", "last_name": "张"}, '
                        '"address": {"address1": "测试路 1 号", "address2": null, "city": "杭州", "country": "CN", "state": "浙江", "zip": "310000"}, '
                        '"email": "chen@example.test", '
                        '"dob": "1990-04-05", '
                        '"payment_methods": {"credit_card_1111": {"source": "credit_card", "id": "credit_card_1111", "brand": "visa", "last_four": "1111"}, "credit_card_3333": {"source": "credit_card", "id": "credit_card_3333", "brand": "mastercard", "last_four": "3333"}, "gift_card_2222": {"source": "gift_card", "id": "gift_card_2222", "amount": 500.0}, "certificate_4444": {"source": "certificate", "id": "certificate_4444", "amount": 600.0}}, '
                        '"saved_passengers": [], '
                        '"membership": "regular", '
                        '"reservations": ["MOD001"]}'
                    ),
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "5 月 16 日去程 HAT001 和 5 月 18 日回程 HAT002 均有普通经济舱。两段航班均保留，舱等一起调整。总价由 ¥4,400 降为 ¥2,000，退 ¥2,400 到尾号 1111 的信用卡。请确认。",
                },
            ],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": [
                "book_reservation",
                "cancel_reservation",
                "send_certificate",
                "update_reservation_baggages",
                "update_reservation_passengers",
            ],
            "db_actions": [
                {
                    "name": "update_reservation_flights",
                    "arguments": {
                        "reservation_id": "MOD001",
                        "cabin": "economy",
                        "flights": [
                            {"flight_number": "HAT001", "date": "2024-05-16"},
                            {"flight_number": "HAT002", "date": "2024-05-18"},
                        ],
                        "payment_id": "credit_card_1111",
                    },
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "CHANGE-CABIN-03",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "商务舱往返去程已落地，拦截整单降舱",
        },
        "inputs": {
            "user": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。请保留 5 月 15 日 HAT001 和 5 月 18 日 HAT002，把整个商务舱往返订单降到普通经济舱。若产生退款，退到档案里尾号 1111 的信用卡。",
            "initial_db": CHANGE_DBS["商务舱去程已飞"],
        },
        "outputs": {
            "lookups": {
                "get_reservation_details": {
                    "arguments": {"reservation_id": "MOD001"},
                    "result_contains": {
                        "reservation_id": "MOD001",
                        "cabin": "business",
                        "flight_type": "round_trip",
                    },
                },
                "get_flight_status": {
                    "arguments": {"flight_number": "HAT001", "date": "2024-05-15"},
                    "result_contains": "landed",
                },
            },
            "forbidden_calls": [
                "book_reservation",
                "cancel_reservation",
                "send_certificate",
                "update_reservation_baggages",
                "update_reservation_flights",
                "update_reservation_passengers",
            ],
            "db_actions": [],
        },
    },
    {
        "metadata": {
            "case_id": "CHANGE-CABIN-04",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "往返两段均未飞，用户明确只升回程舱等",
        },
        "inputs": {
            "user": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。我只想把 5 月 18 日回程 HAT002 升到商务舱。5 月 16 日去程 HAT001 必须保留普通经济舱，两段都不要改日期。不要给我整单升舱。",
            "initial_db": CHANGE_DBS["普通经济舱往返"],
        },
        "outputs": {
            "lookups": {
                "get_reservation_details": {
                    "arguments": {"reservation_id": "MOD001"},
                    "result_contains": {
                        "reservation_id": "MOD001",
                        "flight_type": "round_trip",
                        "cabin": "economy",
                        "flights": [
                            {"flight_number": "HAT001", "date": "2024-05-16"},
                            {"flight_number": "HAT002", "date": "2024-05-18"},
                        ],
                    },
                },
            },
            "forbidden_calls": [
                "book_reservation",
                "cancel_reservation",
                "send_certificate",
                "update_reservation_baggages",
                "update_reservation_flights",
                "update_reservation_passengers",
            ],
            "db_actions": [],
        },
    },
    # 更改托运行李
    {
        "metadata": {
            "case_id": "CHANGE-BAG-01",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "基础经济舱已有一件付费行李，确认再加一件",
        },
        "inputs": {
            "user": "是，确认加一件托运行李，用尾号 1111 的信用卡付 ¥350。",
            "initial_db": CHANGE_DBS["已有一件付费行李"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。请给这个订单再加一件托运行李。我已经买了一件，用档案里尾号 1111 的信用卡支付。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_1_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "MOD001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_1_get_reservation_details",
                    "content": (
                        '{"reservation_id": "MOD001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "one_way", '
                        '"cabin": "basic_economy", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-16", "price": 800}], '
                        '"passengers": [{"first_name": "晨", "last_name": "张", "dob": "1990-04-05"}], '
                        '"payment_history": [{"payment_id": "credit_card_1111", "amount": 1150}], '
                        '"created_at": "2024-05-10T10:00:00", '
                        '"total_baggages": 1, '
                        '"nonfree_baggages": 1, '
                        '"insurance": "no", '
                        '"status": null}'
                    ),
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_3_get_user_details",
                            "name": "get_user_details",
                            "arguments": {"user_id": "chen_zhang_1001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_3_get_user_details",
                    "content": (
                        '{"user_id": "chen_zhang_1001", '
                        '"name": {"first_name": "晨", "last_name": "张"}, '
                        '"address": {"address1": "测试路 1 号", "address2": null, "city": "杭州", "country": "CN", "state": "浙江", "zip": "310000"}, '
                        '"email": "chen@example.test", '
                        '"dob": "1990-04-05", '
                        '"payment_methods": {"credit_card_1111": {"source": "credit_card", "id": "credit_card_1111", "brand": "visa", "last_four": "1111"}, "credit_card_3333": {"source": "credit_card", "id": "credit_card_3333", "brand": "mastercard", "last_four": "3333"}, "gift_card_2222": {"source": "gift_card", "id": "gift_card_2222", "amount": 500.0}, "certificate_4444": {"source": "certificate", "id": "certificate_4444", "amount": 600.0}}, '
                        '"saved_passengers": [], '
                        '"membership": "regular", '
                        '"reservations": ["MOD001"]}'
                    ),
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "您的基础经济舱订单已有 1 件付费托运行李。再加一件后共 2 件，新增费用 ¥350，用尾号 1111 的信用卡支付。请确认。",
                },
            ],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": [
                "book_reservation",
                "cancel_reservation",
                "send_certificate",
                "update_reservation_flights",
                "update_reservation_passengers",
            ],
            "db_actions": [
                {
                    "name": "update_reservation_baggages",
                    "arguments": {
                        "reservation_id": "MOD001",
                        "total_baggages": 2,
                        "nonfree_baggages": 2,
                        "payment_id": "credit_card_1111",
                    },
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "CHANGE-BAG-02",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "要求删除已购买的托运行李并退费",
        },
        "inputs": {
            "user": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。我不托运行李了，请把订单已经购买的那一件托运行李删掉，退回行李费。",
            "initial_db": CHANGE_DBS["已有一件付费行李"],
        },
        "outputs": {
            "lookups": {
                "get_reservation_details": {
                    "arguments": {"reservation_id": "MOD001"},
                    "result_contains": {
                        "reservation_id": "MOD001",
                        "total_baggages": 1,
                        "nonfree_baggages": 1,
                    },
                },
            },
            "forbidden_calls": [
                "book_reservation",
                "cancel_reservation",
                "send_certificate",
                "update_reservation_baggages",
                "update_reservation_flights",
                "update_reservation_passengers",
            ],
            "db_actions": [],
        },
    },
    # 更改保险
    {
        "metadata": {
            "case_id": "CHANGE-INSURANCE-01",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "已出票的未投保订单要求加购旅行保险",
        },
        "inputs": {
            "user": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。这张票订的时候没买保险，航班还没起飞。我现在想给已经订好的订单补买旅行保险，用档案里尾号 1111 的信用卡。",
            "initial_db": CHANGE_DBS["单程同价"],
        },
        "outputs": {"db_actions": []},
    },
    # 更改乘客
    {
        "metadata": {
            "case_id": "CHANGE-PASSENGER-01",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "双人订单只更正一位乘客的出生日期",
        },
        "inputs": {
            "user": "是，确认只把李敏的出生日期更正为 1992-06-16。其他乘客信息保持不变。",
            "initial_db": CHANGE_DBS["双人订单"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。订单上李敏的出生日期填错了，正确的是 1992-06-16，请帮我更正。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_1_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "MOD001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_1_get_reservation_details",
                    "content": (
                        '{"reservation_id": "MOD001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "one_way", '
                        '"cabin": "economy", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-16", "price": 1000}], '
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
                    "content": "订单有两位乘客。我会把李敏的出生日期从 1992-06-18 改为 1992-06-16，张晨的信息保持原样，仍是两位乘客。请确认。",
                },
            ],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": [
                "book_reservation",
                "cancel_reservation",
                "send_certificate",
                "update_reservation_baggages",
                "update_reservation_flights",
            ],
            "db_actions": [
                {
                    "name": "update_reservation_passengers",
                    "arguments": {
                        "reservation_id": "MOD001",
                        "passengers": [
                            {
                                "first_name": "晨",
                                "last_name": "张",
                                "dob": "1990-04-05",
                            },
                            {
                                "first_name": "敏",
                                "last_name": "李",
                                "dob": "1992-06-16",
                            },
                        ],
                    },
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "CHANGE-PASSENGER-02",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "双人订单要求新增乘客，并让人工兜底办理",
        },
        "inputs": {
            "user": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。这笔订单原本有两个人，我还想把王乐加成第三位乘客，出生日期是 1995-08-12。如果你没权限加，就转人工帮我把第三个人加进这张订单。",
            "initial_db": CHANGE_DBS["双人订单"],
        },
        "outputs": {"db_actions": []},
    },
    # 改签支付与退款
    {
        "metadata": {
            "case_id": "CHANGE-PAYMENT-01",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "改到同路线便宜的航班，退差价到指定的档案礼品卡",
        },
        "inputs": {
            "user": "是，确认改到 5 月 17 日 HAT001 普通经济舱。请把 ¥200 退到我档案里的礼品卡 gift_card_2222。",
            "initial_db": CHANGE_DBS["单程改签退差价"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。请把票改到 5 月 17 日，起降机场和普通经济舱都保持原样。改签退款退到我档案里的礼品卡 gift_card_2222。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_1_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "MOD001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_1_get_reservation_details",
                    "content": (
                        '{"reservation_id": "MOD001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "one_way", '
                        '"cabin": "economy", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-16", "price": 1000}], '
                        '"passengers": [{"first_name": "晨", "last_name": "张", "dob": "1990-04-05"}], '
                        '"payment_history": [{"payment_id": "credit_card_1111", "amount": 1000}], '
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
                            "id": "call_history_3_search_direct_flight",
                            "name": "search_direct_flight",
                            "arguments": {
                                "origin": "HGH",
                                "destination": "WUX",
                                "date": "2024-05-17",
                            },
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_3_search_direct_flight",
                    "content": '[{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "status": "available", "scheduled_departure_time_est": "09:00:00", "scheduled_arrival_time_est": "10:00:00", "date": null, "available_seats": {"basic_economy": 4, "economy": 4, "business": 4}, "prices": {"basic_economy": 800, "economy": 800, "business": 2200}}]',
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_5_get_user_details",
                            "name": "get_user_details",
                            "arguments": {"user_id": "chen_zhang_1001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_5_get_user_details",
                    "content": (
                        '{"user_id": "chen_zhang_1001", '
                        '"name": {"first_name": "晨", "last_name": "张"}, '
                        '"address": {"address1": "测试路 1 号", "address2": null, "city": "杭州", "country": "CN", "state": "浙江", "zip": "310000"}, '
                        '"email": "chen@example.test", '
                        '"dob": "1990-04-05", '
                        '"payment_methods": {"credit_card_1111": {"source": "credit_card", "id": "credit_card_1111", "brand": "visa", "last_four": "1111"}, "credit_card_3333": {"source": "credit_card", "id": "credit_card_3333", "brand": "mastercard", "last_four": "3333"}, "gift_card_2222": {"source": "gift_card", "id": "gift_card_2222", "amount": 500.0}, "certificate_4444": {"source": "certificate", "id": "certificate_4444", "amount": 600.0}}, '
                        '"saved_passengers": [], '
                        '"membership": "regular", '
                        '"reservations": ["MOD001"]}'
                    ),
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "5 月 17 日同航线 HAT001 普通经济舱有票，¥800，比原价少 ¥200。档案里有礼品卡 gift_card_2222，退款将退到这张卡。请确认。",
                },
            ],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": [
                "book_reservation",
                "cancel_reservation",
                "send_certificate",
                "update_reservation_baggages",
                "update_reservation_passengers",
            ],
            "db_actions": [
                {
                    "name": "update_reservation_flights",
                    "arguments": {
                        "reservation_id": "MOD001",
                        "cabin": "economy",
                        "flights": [
                            {"flight_number": "HAT001", "date": "2024-05-17"},
                        ],
                        "payment_id": "gift_card_2222",
                    },
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "CHANGE-PAYMENT-02",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "已同意新航班和差价，档案有多张卡，用户尚未选择",
        },
        "inputs": {
            "user": "是，我确认改到 5 月 17 日的航班，补 ¥400 也没问题。用哪张卡我还没决定。",
            "initial_db": CHANGE_DBS["单程改签补差价"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。请把单程票改到 5 月 17 日同一个航班，还是普通经济舱。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_1_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "MOD001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_1_get_reservation_details",
                    "content": (
                        '{"reservation_id": "MOD001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "one_way", '
                        '"cabin": "economy", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-16", "price": 1000}], '
                        '"passengers": [{"first_name": "晨", "last_name": "张", "dob": "1990-04-05"}], '
                        '"payment_history": [{"payment_id": "credit_card_1111", "amount": 1000}], '
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
                            "id": "call_history_3_search_direct_flight",
                            "name": "search_direct_flight",
                            "arguments": {
                                "origin": "HGH",
                                "destination": "WUX",
                                "date": "2024-05-17",
                            },
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_3_search_direct_flight",
                    "content": '[{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "status": "available", "scheduled_departure_time_est": "09:00:00", "scheduled_arrival_time_est": "10:00:00", "date": null, "available_seats": {"basic_economy": 4, "economy": 4, "business": 4}, "prices": {"basic_economy": 800, "economy": 1400, "business": 2200}}]',
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "5 月 17 日 HAT001 普通经济舱有票，¥1,400，需要补 ¥400。请确认改签，并指定一张档案里的礼品卡或信用卡支付。",
                },
            ],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": [
                "book_reservation",
                "cancel_reservation",
                "send_certificate",
                "update_reservation_baggages",
                "update_reservation_flights",
                "update_reservation_passengers",
            ],
            "db_actions": [],
        },
    },
    {
        "metadata": {
            "case_id": "CHANGE-PAYMENT-03",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "用户指定用档案里的一张礼品卡和一张信用卡各付一半",
        },
        "inputs": {
            "user": "是，我确认改签并补 ¥400。请用档案里的礼品卡 gift_card_2222 和尾号 1111 的信用卡各付 ¥200。",
            "initial_db": CHANGE_DBS["单程改签补差价"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。请把单程票改到 5 月 17 日同一个航班，还是普通经济舱。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_1_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "MOD001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_1_get_reservation_details",
                    "content": (
                        '{"reservation_id": "MOD001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "one_way", '
                        '"cabin": "economy", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-16", "price": 1000}], '
                        '"passengers": [{"first_name": "晨", "last_name": "张", "dob": "1990-04-05"}], '
                        '"payment_history": [{"payment_id": "credit_card_1111", "amount": 1000}], '
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
                            "id": "call_history_3_search_direct_flight",
                            "name": "search_direct_flight",
                            "arguments": {
                                "origin": "HGH",
                                "destination": "WUX",
                                "date": "2024-05-17",
                            },
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_3_search_direct_flight",
                    "content": '[{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "status": "available", "scheduled_departure_time_est": "09:00:00", "scheduled_arrival_time_est": "10:00:00", "date": null, "available_seats": {"basic_economy": 4, "economy": 4, "business": 4}, "prices": {"basic_economy": 800, "economy": 1400, "business": 2200}}]',
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "5 月 17 日 HAT001 普通经济舱有票，¥1,400，需要补 ¥400。请确认改签，并指定一张档案里的礼品卡或信用卡支付。",
                },
            ],
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": [
                "book_reservation",
                "cancel_reservation",
                "send_certificate",
                "update_reservation_baggages",
                "update_reservation_flights",
                "update_reservation_passengers",
            ],
            "db_actions": [],
        },
    },
    {
        "metadata": {
            "case_id": "CHANGE-PAYMENT-04",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "用户指定档案里没有的新信用卡支付差价",
        },
        "inputs": {
            "user": "是，我确认改签并补 ¥400。请只用我的新信用卡，尾号 9999，我不选档案里的其他卡。",
            "initial_db": CHANGE_DBS["单程改签补差价"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。请把单程票改到 5 月 17 日同一个航班，还是普通经济舱。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_1_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "MOD001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_1_get_reservation_details",
                    "content": (
                        '{"reservation_id": "MOD001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "one_way", '
                        '"cabin": "economy", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-16", "price": 1000}], '
                        '"passengers": [{"first_name": "晨", "last_name": "张", "dob": "1990-04-05"}], '
                        '"payment_history": [{"payment_id": "credit_card_1111", "amount": 1000}], '
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
                            "id": "call_history_3_search_direct_flight",
                            "name": "search_direct_flight",
                            "arguments": {
                                "origin": "HGH",
                                "destination": "WUX",
                                "date": "2024-05-17",
                            },
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_3_search_direct_flight",
                    "content": '[{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "status": "available", "scheduled_departure_time_est": "09:00:00", "scheduled_arrival_time_est": "10:00:00", "date": null, "available_seats": {"basic_economy": 4, "economy": 4, "business": 4}, "prices": {"basic_economy": 800, "economy": 1400, "business": 2200}}]',
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "5 月 17 日 HAT001 普通经济舱有票，¥1,400，需要补 ¥400。请确认改签，并指定一张档案里的礼品卡或信用卡支付。",
                },
            ],
        },
        "outputs": {
            "lookups": {
                "get_user_details": {
                    "arguments": {"user_id": "chen_zhang_1001"},
                    "result_contains": {
                        "user_id": "chen_zhang_1001",
                        "payment_methods": {
                            "credit_card_1111": {"last_four": "1111"},
                            "credit_card_3333": {"last_four": "3333"},
                        },
                    },
                },
            },
            "forbidden_calls": [
                "book_reservation",
                "cancel_reservation",
                "send_certificate",
                "update_reservation_baggages",
                "update_reservation_flights",
                "update_reservation_passengers",
            ],
            "db_actions": [],
        },
    },
    {
        "metadata": {
            "case_id": "CHANGE-PAYMENT-05",
            "level": "level1",
            "feature": "修改航班",
            "scenario": "用户指定档案里的旅行代金券支付改签差价",
        },
        "inputs": {
            "user": "是，我确认改签并补 ¥400。我想用档案里的旅行代金券 certificate_4444 全额支付差价。",
            "initial_db": CHANGE_DBS["单程改签补差价"],
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": "我是张晨，用户 ID 是 chen_zhang_1001，订单号是 MOD001。请把单程票改到 5 月 17 日同一个航班，还是普通经济舱。",
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "tool_calls": [
                        {
                            "id": "call_history_1_get_reservation_details",
                            "name": "get_reservation_details",
                            "arguments": {"reservation_id": "MOD001"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_1_get_reservation_details",
                    "content": (
                        '{"reservation_id": "MOD001", '
                        '"user_id": "chen_zhang_1001", '
                        '"origin": "HGH", '
                        '"destination": "WUX", '
                        '"flight_type": "one_way", '
                        '"cabin": "economy", '
                        '"flights": [{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "date": "2024-05-16", "price": 1000}], '
                        '"passengers": [{"first_name": "晨", "last_name": "张", "dob": "1990-04-05"}], '
                        '"payment_history": [{"payment_id": "credit_card_1111", "amount": 1000}], '
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
                            "id": "call_history_3_search_direct_flight",
                            "name": "search_direct_flight",
                            "arguments": {
                                "origin": "HGH",
                                "destination": "WUX",
                                "date": "2024-05-17",
                            },
                        },
                    ],
                },
                {
                    "role": "tool",
                    "id": "call_history_3_search_direct_flight",
                    "content": '[{"flight_number": "HAT001", "origin": "HGH", "destination": "WUX", "status": "available", "scheduled_departure_time_est": "09:00:00", "scheduled_arrival_time_est": "10:00:00", "date": null, "available_seats": {"basic_economy": 4, "economy": 4, "business": 4}, "prices": {"basic_economy": 800, "economy": 1400, "business": 2200}}]',
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "5 月 17 日 HAT001 普通经济舱有票，¥1,400，需要补 ¥400。请确认改签，并指定一张档案里的礼品卡或信用卡支付。",
                },
            ],
        },
        "outputs": {
            "lookups": {
                "get_user_details": {
                    "arguments": {"user_id": "chen_zhang_1001"},
                    "result_contains": {
                        "user_id": "chen_zhang_1001",
                        "payment_methods": {
                            "certificate_4444": {"source": "certificate"},
                        },
                    },
                },
            },
            "forbidden_calls": [
                "book_reservation",
                "cancel_reservation",
                "send_certificate",
                "update_reservation_baggages",
                "update_reservation_flights",
                "update_reservation_passengers",
            ],
            "db_actions": [],
        },
    },
]
