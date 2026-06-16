from graph.workflow import refund_graph


state = {
    "query": "Refund order ORD005",
    "order_id": "",
    "customer": {},
    "policy": "",
    "decision": {},
    "response": "",
    "logs": []
}


result = refund_graph.invoke(
    state
)

print("\nResponse:")
print(result["response"])

print("\nLogs:")
for log in result["logs"]:
    print(log)