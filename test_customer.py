# from tools.customer_tool import get_customer

# customer = get_customer("ORD001")

# print(customer)
# ------------------------------
# from tools.policy_tool import load_policy

# print(load_policy())
# ------------------------------


from tools.customer_tool import get_customer
from tools.validation_tool import validate_refund

customer = get_customer("ORD003")

result = validate_refund(customer)

print(result)