from database import save_action


def issue_refund(request_id, amount):
    """Tool: persist a refund action."""
    details = f"Refund issued for ${amount:.2f}."
    save_action(request_id, "REFUND", amount, "EXECUTED", details)
    return {
        "action_type": "REFUND",
        "amount": round(amount, 2),
        "status": "EXECUTED",
        "details": details,
    }


def issue_credit(request_id, amount):
    """Tool: persist a fare-credit action."""
    details = f"Fare credit issued for ${amount:.2f}."
    save_action(request_id, "FARE_CREDIT", amount, "EXECUTED", details)
    return {
        "action_type": "FARE_CREDIT",
        "amount": round(amount, 2),
        "status": "EXECUTED",
        "details": details,
    }


def schedule_replacement_credit(request_id):
    """Tool: persist a scheduled replacement ride credit."""
    details = "Replacement ride credit scheduled."
    save_action(
        request_id,
        "REPLACEMENT_RIDE_CREDIT",
        0.0,
        "SCHEDULED",
        details,
    )
    return {
        "action_type": "REPLACEMENT_RIDE_CREDIT",
        "amount": 0.0,
        "status": "SCHEDULED",
        "details": details,
    }
