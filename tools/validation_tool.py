from datetime import datetime


def validate_refund(customer):
    """
    Returns (decision_dict, checks_list).
    checks_list logs each rule evaluated.
    """
    checks = []
    today = datetime.now()

    try:
        purchase_date = datetime.strptime(customer["purchase_date"], "%Y-%m-%d")
        days = (today - purchase_date).days
    except Exception:
        return (
            {"decision": "DENIED", "reason": "Invalid purchase date."},
            ["❌ Could not parse purchase date"]
        )

    checks.append(f"Days since purchase: {days} (limit: 30)")

    # Rule 7: Already refunded
    if customer.get("refund_requested"):
        checks.append("❌ Order already has a refund requested/processed")
        return (
            {"decision": "DENIED", "reason": "Order has already been refunded."},
            checks
        )
    checks.append("✔ No prior refund on this order")

    # Rule 2: Must be delivered
    if customer.get("delivery_status") != "Delivered":
        checks.append(f"❌ Delivery status is '{customer.get('delivery_status')}' — must be Delivered")
        return (
            {"decision": "DENIED", "reason": f"Order has not been delivered (status: {customer.get('delivery_status')})."},
            checks
        )
    checks.append("✔ Delivery status: Delivered")

    # Rule 9: Cancelled orders
    if customer.get("delivery_status") == "Cancelled":
        checks.append("❌ Order is cancelled")
        return (
            {"decision": "DENIED", "reason": "Cancelled orders are not eligible for refunds."},
            checks
        )

    # Rule 3: Digital products
    if customer.get("product_type") == "Digital":
        checks.append("❌ Product type is Digital — non-refundable")
        return (
            {"decision": "DENIED", "reason": "Digital products are non-refundable per policy."},
            checks
        )
    checks.append(f"✔ Product type: {customer.get('product_type')} (refundable category)")

    # Rule 4: Subscriptions
    if customer.get("product_type") == "Subscription":
        checks.append("❌ Product type is Subscription — non-refundable")
        return (
            {"decision": "DENIED", "reason": "Subscription products are non-refundable per policy."},
            checks
        )

    # Rule 1: 30-day window
    if days > 30:
        checks.append(f"❌ Refund window exceeded by {days - 30} days")
        return (
            {"decision": "DENIED", "reason": f"Refund window exceeded — purchase was {days} days ago (limit: 30 days)."},
            checks
        )
    checks.append(f"✔ Within refund window ({days} of 30 days)")

    # Rule 5: Damaged — manual review
    if customer.get("damaged"):
        checks.append("⚠️  Product reported as damaged — escalating to manual review")
        return (
            {"decision": "MANUAL_REVIEW", "reason": "Damaged product requires manual inspection before refund can be processed."},
            checks
        )
    checks.append("✔ Product condition: Not damaged")

    # Rule 6: High value — manual review
    if customer.get("price", 0) > 1000:
        checks.append(f"⚠️  Order value ${customer.get('price')} exceeds $1000 threshold — manager approval required")
        return (
            {"decision": "MANUAL_REVIEW", "reason": f"High-value order (${customer.get('price')}) requires manager approval."},
            checks
        )
    checks.append(f"✔ Order value ${customer.get('price')} within auto-approval limit")

    # Rule 8: Too many previous refunds
    if customer.get("previous_refunds", 0) > 3:
        checks.append(f"⚠️  Customer has {customer.get('previous_refunds')} previous refunds (limit: 3) — flagged for review")
        return (
            {"decision": "MANUAL_REVIEW", "reason": f"Customer has {customer.get('previous_refunds')} prior refunds — requires manual review."},
            checks
        )
    checks.append(f"✔ Previous refund count: {customer.get('previous_refunds', 0)} (within limit)")

    checks.append("✔ All policy rules satisfied — APPROVED")
    return (
        {"decision": "APPROVED", "reason": "Refund approved — all policy rules satisfied."},
        checks
    )
