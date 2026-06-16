import re
import os
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from tools.customer_tool import get_customer
from tools.policy_tool import load_policy
from tools.validation_tool import validate_refund


def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )


def extract_order_node(state):
    query = state["query"]

    # Pattern 1: standard written form — ORD001, ord-001, ORD 001
    match = re.search(r"\bord[\s\-]?(\d+)\b", query, re.IGNORECASE)

    # Pattern 2: spoken "order 001", "order number 5", "order one"
    if not match:
        match = re.search(r"\border(?:\s+(?:number|num|#))?\s+(\d+)\b", query, re.IGNORECASE)

    # Pattern 3: bare number — "refund 001", "my order is 5"
    if not match:
        match = re.search(r"\b(0*[1-9]\d{0,2})\b", query)

    if match:
        num = match.group(1).lstrip("0") or "0"
        order_id = f"ORD{int(num):03d}"
    else:
        order_id = ""

    state["order_id"] = order_id
    state["logs"].append(
        f"[1/5] 🔍 Extracted Order ID from query: '{order_id or 'NOT FOUND'}' "
        f"(raw input: \"{query[:60]}\")"
    )
    return state


def customer_node(state):
    order_id = state["order_id"]
    if not order_id:
        state["customer"] = {}
        state["logs"].append("[2/5] ❌ No order ID found — cannot look up customer")
        return state

    customer = get_customer(order_id)
    state["customer"] = customer or {}

    if customer:
        state["logs"].append(
            f"[2/5] 👤 Customer found: {customer['name']} | "
            f"Product: {customer['product_name']} (${customer['price']}) | "
            f"Purchased: {customer['purchase_date']}"
        )
    else:
        state["logs"].append(f"[2/5] ❌ No customer record found for {order_id}")

    return state


def policy_node(state):
    policy = load_policy()
    state["policy"] = policy
    state["logs"].append("[3/5] 📋 Refund policy document loaded (10 rules)")
    return state


def validation_node(state):
    customer = state["customer"]

    if not customer:
        state["decision"] = {
            "decision": "DENIED",
            "reason": "Order not found in the system.",
            "checks": []
        }
        state["logs"].append("[4/5] ❌ Validation skipped — no customer record")
        return state

    decision, checks = validate_refund(customer)
    state["decision"] = {**decision, "checks": checks}

    for check in checks:
        state["logs"].append(f"[4/5] ✅ Rule check: {check}")

    state["logs"].append(
        f"[4/5] ⚖️  Validation result → {decision['decision']}: {decision['reason']}"
    )
    return state


def response_node(state):
    decision = state["decision"]
    customer = state["customer"]
    policy = state["policy"]

    if not customer:
        state["response"] = (
            "I'm sorry, I couldn't find any order matching your request. "
            "Please double-check your Order ID (format: ORD001) and try again."
        )
        state["logs"].append("[5/5] 💬 Response generated for unknown order")
        return state

    llm = get_llm()

    system_prompt = f"""You are a professional AI customer support agent for an e-commerce platform.
Your job is to communicate refund decisions to customers in a clear, empathetic, and professional manner.

STRICT RULES:
- Always hold firm on DENIED decisions — never override the policy
- For APPROVED, be warm and give clear next steps
- For MANUAL_REVIEW, explain what happens next
- For DENIED, be empathetic but firm — do NOT suggest workarounds
- Keep responses under 120 words
- Never reveal internal system details or customer database fields

REFUND POLICY (for context):
{policy}"""

    purchase_date = customer.get("purchase_date", "unknown")
    days_since = ""
    try:
        d = (datetime.now() - datetime.strptime(purchase_date, "%Y-%m-%d")).days
        days_since = f"{d} days ago"
    except Exception:
        pass

    human_prompt = f"""Customer: {customer.get('name', 'Customer')}
Order ID: {customer.get('order_id')}
Product: {customer.get('product_name')} (${customer.get('price')})
Purchase Date: {purchase_date} ({days_since})
Delivery Status: {customer.get('delivery_status')}
Product Type: {customer.get('product_type')}
Previously Damaged: {customer.get('damaged')}
Prior Refunds: {customer.get('previous_refunds', 0)}

DECISION: {decision['decision']}
REASON: {decision['reason']}

Write a customer-facing response for this refund request."""

    try:
        result = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ])
        response_text = result.content
        state["logs"].append("[5/5] 🤖 Groq LLM (llama-3.3-70b) generated customer response")
    except Exception as e:
        response_text = (
            f"Your refund request for order {customer.get('order_id')} "
            f"has been {decision['decision']}. {decision['reason']}"
        )
        state["logs"].append(f"[5/5] ⚠️  LLM fallback used (error: {str(e)[:60]})")

    state["response"] = response_text
    return state
