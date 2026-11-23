"""航空预订 Level 1 单轮用例，评测范围截至下单前。

每条用例写明要查询的工具、其返回的预期字段，以及禁止调用的工具。
"""

import json
from copy import deepcopy
from pathlib import Path

BASE_DB = json.loads((Path(__file__).parent / "fixtures/booking_db.json").read_text())

SOLD_OUT_DB = deepcopy(BASE_DB)
SOLD_OUT_DB["flights"]["HAT001"]["dates"]["2024-05-16"]["available_seats"][
    "economy"
] = 0

GIFT_DB = deepcopy(BASE_DB)
GIFT_DB["users"]["chen_zhang_1001"]["payment_methods"]["gift_card_2222"] = {
    "id": "gift_card_2222",
    "source": "gift_card",
    "amount": 300,
}

EXAMPLES = [
    {
        "metadata": {
            "case_id": "BOOK-01",
            "level": "level1",
            "feature": "预订航班",
            "scenario": "预订信息齐全，下单前查票价和档案里的信用卡",
        },
        "inputs": {
            "user": (
                "我是张晨，用户 ID 是 chen_zhang_1001。我的出生日期是 1990-04-05。"
                "请帮我订2024年5月16日杭州萧山（HGH）到无锡硕放（WUX）的单程直飞 HAT001 普通经济舱，"
                "就我一个人，无托运行李，不买保险。用档案里尾号1111的信用卡付款。"
            ),
            "initial_db": BASE_DB,
        },
        "outputs": {
            "lookups": {
                "search_direct_flight": {
                    "arguments": {
                        "origin": "HGH",
                        "destination": "WUX",
                        "date": "2024-05-16",
                    },
                    "result_contains": {
                        "flight_number": "HAT001",
                        "prices": {"economy": 1000},
                    },
                },
                "get_user_details": {
                    "arguments": {"user_id": "chen_zhang_1001"},
                    "result_contains": {
                        "payment_methods": {
                            "credit_card_1111": {
                                "source": "credit_card",
                                "last_four": "1111",
                            },
                        },
                    },
                },
            },
            "forbidden_calls": ["book_reservation"],
        },
    },
    {
        "metadata": {
            "case_id": "BOOK-02",
            "level": "level1",
            "feature": "预订航班",
            "scenario": "只询价，暂不预订",
        },
        "inputs": {
            "user": (
                "我是张晨，用户 ID 是 chen_zhang_1001。"
                "帮我查下2024年5月16日杭州萧山（HGH）到无锡硕放（WUX）的单程直飞 HAT001 普通经济舱"
                "多少钱，我先看看价格，别下单。"
            ),
            "initial_db": BASE_DB,
        },
        "outputs": {
            "lookups": {
                "search_direct_flight": {
                    "arguments": {
                        "origin": "HGH",
                        "destination": "WUX",
                        "date": "2024-05-16",
                    },
                    "result_contains": {
                        "flight_number": "HAT001",
                        "prices": {"economy": 1000},
                    },
                },
            },
            "forbidden_calls": ["book_reservation"],
        },
    },
    {
        "metadata": {
            "case_id": "BOOK-03",
            "level": "level1",
            "feature": "预订航班",
            "scenario": "同行人缺出生日期时禁止下单",
        },
        "inputs": {
            "user": (
                "我是张晨，用户 ID 是 chen_zhang_1001。我的出生日期是 1990-04-05。"
                "我和李小雨两个人要订2024年5月16日杭州萧山（HGH）到无锡硕放（WUX）的"
                "单程直飞 HAT001 普通经济舱，都不托运行李，不买保险。"
                "全部用档案里尾号1111的信用卡。"
            ),
            "initial_db": BASE_DB,
        },
        "outputs": {
            "lookups": {},
            "forbidden_calls": ["book_reservation"],
        },
    },
    {
        "metadata": {
            "case_id": "BOOK-04",
            "level": "level1",
            "feature": "预订航班",
            "scenario": "普通经济舱售罄，用户拒绝替代舱等",
        },
        "inputs": {
            "user": (
                "我是张晨，用户 ID 是 chen_zhang_1001。"
                "帮我查下2024年5月16日杭州萧山（HGH）到无锡硕放（WUX）的单程直飞 HAT001 普通经济舱"
                "还有没有票。我只要这个舱等，没票就先不订。"
            ),
            "initial_db": SOLD_OUT_DB,  # HAT001 普通经济舱剩余 0 个座位。
        },
        "outputs": {
            "lookups": {
                "search_direct_flight": {
                    "arguments": {
                        "origin": "HGH",
                        "destination": "WUX",
                        "date": "2024-05-16",
                    },
                    "result_contains": {
                        "flight_number": "HAT001",
                        "available_seats": {"economy": 0},
                    },
                },
            },
            "forbidden_calls": ["book_reservation"],
        },
    },
    {
        "metadata": {
            "case_id": "BOOK-05",
            "level": "level1",
            "feature": "预订航班",
            "scenario": "拆分付款前核对票价、礼品卡余额和信用卡",
        },
        "inputs": {
            "user": (
                "我是张晨，用户 ID 是 chen_zhang_1001。我的出生日期是 1990-04-05。"
                "请帮我订2024年5月16日杭州萧山（HGH）到无锡硕放（WUX）的单程直飞 HAT001 普通经济舱，"
                "就我一个人，无托运行李，不买保险。"
                "档案里尾号2222的礼品卡用完，剩下的刷尾号1111的信用卡。"
            ),
            "initial_db": GIFT_DB,  # 票价 1000 元，礼品卡余额 300 元。
        },
        "outputs": {
            "lookups": {
                "search_direct_flight": {
                    "arguments": {
                        "origin": "HGH",
                        "destination": "WUX",
                        "date": "2024-05-16",
                    },
                    "result_contains": {
                        "flight_number": "HAT001",
                        "prices": {"economy": 1000},
                    },
                },
                "get_user_details": {
                    "arguments": {"user_id": "chen_zhang_1001"},
                    "result_contains": {
                        "payment_methods": {
                            "gift_card_2222": {"source": "gift_card", "amount": 300},
                            "credit_card_1111": {
                                "source": "credit_card",
                                "last_four": "1111",
                            },
                        },
                    },
                },
            },
            "forbidden_calls": ["book_reservation"],
        },
    },
]
