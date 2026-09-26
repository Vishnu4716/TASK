from config import AUTO_RESOLUTION_THRESHOLD, MAX_RERIDE_CREDITS_30D

# Conservative mapping from natural-language reason to challenge categories.
SUPPORTED_CATEGORIES = {
    "OVERCHARGE": {"SURGE_OVERCHARGE_CONFIRMED"},
    "SURGE_OVERCHARGE": {"SURGE_OVERCHARGE_CONFIRMED"},
    "ROUTE_DEVIATION": {"INCORRECT_DROPOFF_LOCATION"},
    "INCORRECT_DROPOFF": {"INCORRECT_DROPOFF_LOCATION"},
    "DRIVER_CANCELLED": {"DRIVER_CANCELLED_MIDTRIP"},
    "RIDER_CANCELLED": set(),
    "OTHER": set(),
}


def validate_dispute(intent, trip):
    if not trip:
        return {
            "supported": False,
            "reason": "Referenced trip was not found."
        }

    category = str(trip.get("verified_category", "")).upper()

    category_map = {
        "OVERCHARGE": {"SURGE_OVERCHARGE_CONFIRMED"},
        "SURGE_OVERCHARGE": {"SURGE_OVERCHARGE_CONFIRMED"},
        "ROUTE_DEVIATION": {"INCORRECT_DROPOFF_LOCATION"},
        "INCORRECT_DROPOFF": {"INCORRECT_DROPOFF_LOCATION"},
        "DRIVER_CANCELLED": {"DRIVER_CANCELLED_MIDTRIP"},
        "RIDER_CANCELLED": {"RIDER_INITIATED_CANCELLATION"},
    }

    supported_categories = category_map.get(intent, set())

    if category in supported_categories:
        return {
            "supported": True,
            "reason": (
                f"Trip category {category} supports "
                f"the interpreted reason."
            )
        }

    return {
        "supported": False,
        "reason": (
            f"Trip category {category} does not support "
            f"interpreted intent {intent}."
        )
    }


def resolution_amount(trip):
    try:
        credit_value = float(trip.get("credit_value"))
    except (TypeError, ValueError):
        credit_value = 0.0

    try:
        fare_value = float(trip.get("fare_value"))
    except (TypeError, ValueError):
        fare_value = 0.0

    # Positive challenge-provided credit_value is authoritative.
    # Otherwise use the trip fare.
    return credit_value if credit_value > 0 else max(fare_value, 0.0)


def can_auto_resolve(amount, supported):
    return bool(
        supported
        and amount > 0
        and amount <= AUTO_RESOLUTION_THRESHOLD
    )


def replacement_credit_eligible(history):
    count = int(history.get("reride_credits_last_30_days", 0))
    return count < MAX_RERIDE_CREDITS_30D
