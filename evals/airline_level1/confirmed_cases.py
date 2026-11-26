"""固定下单前历史，只评测用户确认后的这一轮。"""

import json

from tau2.domains.airline.data_model import User

from .cases import BASE_DB, GIFT_DB, SOLD_OUT_DB


def _recorded_lookup(name: str, arguments: dict, result: dict | list) -> list[dict]:
    call_id = f"call_history_{name}"
    return [
        {
            "role": "assistant",
            "cost": 0,
            "tool_calls": [{"id": call_id, "name": name, "arguments": arguments}],
        },
        {
            "role": "tool",
            "id": call_id,
            "content": json.dumps(result, ensure_ascii=False),
        },
    ]


def _flight_history(economy_seats: int) -> list[dict]:
    """Record the HAT001 lookup for the chosen fixture's economy inventory."""
    return _recorded_lookup(
        "search_direct_flight",
        {"origin": "HGH", "destination": "WUX", "date": "2024-05-16"},
        [
            {
                "flight_number": "HAT001",
                "origin": "HGH",
                "destination": "WUX",
                "status": "available",
                "scheduled_departure_time_est": "09:00:00",
                "scheduled_arrival_time_est": "10:00:00",
                "date": None,
                "available_seats": {
                    "economy": economy_seats,
                    "business": 0,
                    "basic_economy": 4,
                },
                "prices": {"economy": 1000, "business": 2200, "basic_economy": 800},
            }
        ],
    )


def _profile_history(db: dict) -> list[dict]:
    """Record the saved payment methods using the airline tool's response schema."""
    return _recorded_lookup(
        "get_user_details",
        {"user_id": "chen_zhang_1001"},
        User.model_validate(db["users"]["chen_zhang_1001"]).model_dump(mode="json"),
    )


CONFIRMED_EXAMPLES = [
    {
        "metadata": {
            "case_id": "BOOK-06",
            "level": "level1",
            "feature": "预定航班",
            "scenario": "用户确认后，按已确认的方案创建一次订单",
        },
        "inputs": {
            "initial_db": BASE_DB,
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": (
                        "我是张晨，用户 ID 是 chen_zhang_1001。我的出生日期是 1990-04-05。"
                        "请帮我订2024年5月16日杭州萧山（HGH）到无锡硕放（WUX）的单程直飞 HAT001 普通经济舱，"
                        "就我一个人，无托运行李，不买保险。用档案里尾号1111的信用卡付款。"
                    ),
                },
                *_flight_history(economy_seats=4),
                *_profile_history(BASE_DB),
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": (
                        "已查到 2024 年 5 月 16 日杭州萧山 HGH 到无锡硕放 WUX 的单程直飞航班 "
                        "HAT001，09:00 起飞、10:00 到达，普通经济舱有票。"
                        "乘客 1 位，姓张、名晨，出生日期 1990-04-05，托运行李 0 件，不购买保险。"
                        "总价 1000 元，用档案里尾号 1111 的信用卡全额付款。请回复「是」确认预订。"
                    ),
                },
            ],
            "user": "是，确认按上面的方案预订。",
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": [],
            "db_actions": [
                {
                    "name": "book_reservation",
                    "arguments": {
                        "user_id": "chen_zhang_1001",
                        "origin": "HGH",
                        "destination": "WUX",
                        "flight_type": "one_way",
                        "cabin": "economy",
                        "flights": [{"flight_number": "HAT001", "date": "2024-05-16"}],
                        "passengers": [
                            {
                                "first_name": "晨",
                                "last_name": "张",
                                "dob": "1990-04-05",
                            },
                        ],
                        "payment_methods": [
                            {"payment_id": "credit_card_1111", "amount": 1000},
                        ],
                        "total_baggages": 0,
                        "nonfree_baggages": 0,
                        "insurance": "no",
                    },
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "BOOK-08",
            "level": "level1",
            "feature": "预定航班",
            "scenario": "补齐同行人出生日期并确认后，为两位乘客下单",
        },
        "inputs": {
            "initial_db": BASE_DB,
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": (
                        "我是张晨，用户 ID 是 chen_zhang_1001。我的出生日期是 1990-04-05。"
                        "我和李小雨两个人要订2024年5月16日杭州萧山（HGH）到无锡硕放（WUX）的"
                        "单程直飞 HAT001 普通经济舱，都不托运行李，不买保险。"
                        "全部用档案里尾号1111的信用卡。"
                    ),
                },
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "请提供同行乘客李小雨的出生日期。",
                },
                {
                    "role": "user",
                    "cost": 0,
                    "content": "她姓李、名小雨，出生日期是 1992-08-12。",
                },
                *_flight_history(economy_seats=4),
                *_profile_history(BASE_DB),
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": (
                        "2024 年 5 月 16 日杭州萧山 HGH 到无锡硕放 WUX 的 HAT001 单程直飞，普通经济舱有座。"
                        "乘客两位，姓张、名晨，出生日期 1990-04-05；"
                        "姓李、名小雨，出生日期 1992-08-12。托运行李共 0 件，不买保险。"
                        "票价每人 1000 元，总计 2000 元，用档案尾号 1111 的信用卡付款。请回复「是」确认预订。"
                    ),
                },
            ],
            "user": "是，确认给我们两个人订。",
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": [],
            "db_actions": [
                {
                    "name": "book_reservation",
                    "arguments": {
                        "user_id": "chen_zhang_1001",
                        "origin": "HGH",
                        "destination": "WUX",
                        "flight_type": "one_way",
                        "cabin": "economy",
                        "flights": [{"flight_number": "HAT001", "date": "2024-05-16"}],
                        "passengers": [
                            {
                                "first_name": "晨",
                                "last_name": "张",
                                "dob": "1990-04-05",
                            },
                            {
                                "first_name": "小雨",
                                "last_name": "李",
                                "dob": "1992-08-12",
                            },
                        ],
                        "payment_methods": [
                            {"payment_id": "credit_card_1111", "amount": 2000},
                        ],
                        "total_baggages": 0,
                        "nonfree_baggages": 0,
                        "insurance": "no",
                    },
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "BOOK-09",
            "level": "level1",
            "feature": "预定航班",
            "scenario": "普通经济舱售罄，改选基础经济舱并确认后下单",
        },
        "inputs": {
            "initial_db": SOLD_OUT_DB,
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": (
                        "我是张晨，用户 ID 是 chen_zhang_1001。"
                        "帮我查下2024年5月16日杭州萧山（HGH）到无锡硕放（WUX）的单程直飞 HAT001 普通经济舱"
                        "还有没有票。我只要这个舱等，没票就先不订。"
                    ),
                },
                *_flight_history(economy_seats=0),
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": "普通经济舱余票为 0，先不订。这个航班的基础经济舱还有 4 个座位，票价 800 元。",
                },
                {
                    "role": "user",
                    "cost": 0,
                    "content": (
                        "我改主意了，给我查一下改订基础经济舱的方案。就我一人，姓张、名晨，"
                        "出生日期 1990-04-05，无托运行李，不买保险，用档案里尾号1111的信用卡。"
                    ),
                },
                *_profile_history(SOLD_OUT_DB),
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": (
                        "替代方案是 2024 年 5 月 16 日杭州萧山 HGH 到无锡硕放 WUX 的 HAT001 单程直飞，"
                        "基础经济舱。乘客一位，姓张、名晨，出生日期 1990-04-05。"
                        "托运行李 0 件，不买保险。总价 800 元，用档案尾号 1111 的信用卡付款。"
                        "请回复「是」确认这个替代方案。"
                    ),
                },
            ],
            "user": "是，确认订基础经济舱。",
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": [],
            "db_actions": [
                {
                    "name": "book_reservation",
                    "arguments": {
                        "user_id": "chen_zhang_1001",
                        "origin": "HGH",
                        "destination": "WUX",
                        "flight_type": "one_way",
                        "cabin": "basic_economy",
                        "flights": [{"flight_number": "HAT001", "date": "2024-05-16"}],
                        "passengers": [
                            {
                                "first_name": "晨",
                                "last_name": "张",
                                "dob": "1990-04-05",
                            },
                        ],
                        "payment_methods": [
                            {"payment_id": "credit_card_1111", "amount": 800},
                        ],
                        "total_baggages": 0,
                        "nonfree_baggages": 0,
                        "insurance": "no",
                    },
                },
            ],
        },
    },
    {
        "metadata": {
            "case_id": "BOOK-10",
            "level": "level1",
            "feature": "预定航班",
            "scenario": "确认礼品卡和信用卡的拆分付款后下单",
        },
        "inputs": {
            "initial_db": GIFT_DB,
            "history": [
                {
                    "role": "user",
                    "cost": 0,
                    "content": (
                        "我是张晨，用户 ID 是 chen_zhang_1001。我的出生日期是 1990-04-05。"
                        "请帮我订2024年5月16日杭州萧山（HGH）到无锡硕放（WUX）的单程直飞 HAT001 普通经济舱，"
                        "就我一个人，无托运行李，不买保险。"
                        "档案里尾号2222的礼品卡用完，剩下的刷尾号1111的信用卡。"
                    ),
                },
                *_flight_history(economy_seats=4),
                *_profile_history(GIFT_DB),
                {
                    "role": "assistant",
                    "cost": 0,
                    "content": (
                        "2024 年 5 月 16 日杭州萧山 HGH 到无锡硕放 WUX 的 HAT001 单程直飞普通经济舱有票。"
                        "乘客一位，姓张、名晨，出生日期 1990-04-05，托运行李 0 件，不买保险。"
                        "总价 1000 元，先用尾号 2222 的礼品卡支付全部余额 300 元，"
                        "剩余 700 元用尾号 1111 的信用卡支付。请回复「是」确认这个预订和付款方案。"
                    ),
                },
            ],
            "user": "是，按这个付款方案订。",
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": [],
            "db_actions": [
                {
                    "name": "book_reservation",
                    "arguments": {
                        "user_id": "chen_zhang_1001",
                        "origin": "HGH",
                        "destination": "WUX",
                        "flight_type": "one_way",
                        "cabin": "economy",
                        "flights": [{"flight_number": "HAT001", "date": "2024-05-16"}],
                        "passengers": [
                            {
                                "first_name": "晨",
                                "last_name": "张",
                                "dob": "1990-04-05",
                            },
                        ],
                        "payment_methods": [
                            {"payment_id": "gift_card_2222", "amount": 300},
                            {"payment_id": "credit_card_1111", "amount": 700},
                        ],
                        "total_baggages": 0,
                        "nonfree_baggages": 0,
                        "insurance": "no",
                    },
                },
            ],
        },
    },
]
