from langgraph.graph import (
    StateGraph,
    START,
    END
)

from graph.state import RefundState
from graph.nodes import (
    extract_order_node,
    customer_node,
    policy_node,
    validation_node,
    response_node
)


builder = StateGraph(
    RefundState
)

builder.add_node(
    "extract_order",
    extract_order_node
)

builder.add_node(
    "get_customer",
    customer_node
)

builder.add_node(
    "load_policy",
    policy_node
)

builder.add_node(
    "validate_refund",
    validation_node
)

builder.add_node(
    "generate_response",
    response_node
)

builder.add_edge(
    START,
    "extract_order"
)

builder.add_edge(
    "extract_order",
    "get_customer"
)

builder.add_edge(
    "get_customer",
    "load_policy"
)

builder.add_edge(
    "load_policy",
    "validate_refund"
)

builder.add_edge(
    "validate_refund",
    "generate_response"
)

builder.add_edge(
    "generate_response",
    END
)

refund_graph = builder.compile()