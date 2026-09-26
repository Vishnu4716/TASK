from data_store import DataStore

_store = None


def get_store():
    global _store
    if _store is None:
        _store = DataStore()
    return _store


def lookup_trip(trip_id):
    """Tool: retrieve the authoritative trip record."""
    return get_store().lookup_trip(trip_id)


def lookup_request(request_id):
    """Tool: retrieve an incoming dispute request."""
    return get_store().get_request(request_id)
