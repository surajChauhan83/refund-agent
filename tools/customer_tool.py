import json


def get_customer(order_id: str):
    """
    Retrieve customer information
    using order id.
    """

    with open("data/customers.json","r") as file:
        customers = json.load(file)
        
    for customer in customers:
        if customer["order_id"] == order_id:
            return customer

    return None