from typing import TypedDict


class RefundState(TypedDict):
    query: str
    order_id: str
    customer: dict
    policy: str
    decision: dict
    response: str
    logs: list