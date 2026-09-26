from data_store import DataStore
from policy import replacement_credit_eligible

_store = None


def get_store():
    global _store
    if _store is None:
        _store = DataStore()
    return _store


def get_reride_history(rider_name):
    """Tool: retrieve recent replacement-credit history."""
    history = get_store().get_reride_history(rider_name)
    history["eligible_for_new_credit"] = replacement_credit_eligible(history)
    return history
