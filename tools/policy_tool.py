def load_policy():
    """
    Load refund policy document.
    """

    with open("data/refund_policy.txt","r") as file:
        policy = file.read()
    return policy