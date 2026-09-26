from pathlib import Path
import pandas as pd

REQUEST_COLUMNS = [
    "request_id", "rider_name", "rider_tier", "trip_id", "submitted_at", "request_text"
]
TRIP_COLUMNS = [
    "trip_id", "rider_name", "route", "verified_category",
    "fare_value", "credit_eligible", "credit_value"
]
HISTORY_COLUMNS = ["rider_name", "reride_credits_last_30_days"]


def _check_columns(df, required, name):
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{name} is missing columns: {missing}")


class DataStore:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.requests = pd.read_csv(self.data_dir / "fare_dispute_requests.csv")
        self.trips = pd.read_csv(self.data_dir / "trip_records.csv")
        self.history = pd.read_csv(self.data_dir / "reride_credit_history.csv")

        _check_columns(self.requests, REQUEST_COLUMNS, "fare_dispute_requests.csv")
        _check_columns(self.trips, TRIP_COLUMNS, "trip_records.csv")
        _check_columns(self.history, HISTORY_COLUMNS, "reride_credit_history.csv")

        self.trips["credit_eligible"] = (
            self.trips["credit_eligible"].astype(str).str.upper().eq("TRUE")
        )
        self.trips["fare_value"] = pd.to_numeric(
            self.trips["fare_value"], errors="coerce"
        )
        self.trips["credit_value"] = pd.to_numeric(
            self.trips["credit_value"], errors="coerce"
        )
        self.history["reride_credits_last_30_days"] = pd.to_numeric(
            self.history["reride_credits_last_30_days"], errors="coerce"
        ).fillna(0).astype(int)

    def get_request(self, request_id):
        rows = self.requests[
            self.requests["request_id"].astype(str) == str(request_id)
        ]
        return None if rows.empty else rows.iloc[0].to_dict()

    def list_requests(self):
        return self.requests.to_dict(orient="records")

    def lookup_trip(self, trip_id):
        rows = self.trips[
            self.trips["trip_id"].astype(str) == str(trip_id)
        ]
        return None if rows.empty else rows.iloc[0].to_dict()

    def get_reride_history(self, rider_name):
        rows = self.history[
            self.history["rider_name"].astype(str).str.casefold()
            == str(rider_name).casefold()
        ]
        if rows.empty:
            return {"rider_name": rider_name, "reride_credits_last_30_days": 0}
        return rows.iloc[0].to_dict()
