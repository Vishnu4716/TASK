import json

from database import init_db, save_decision, save_request
from llm import interpret_request
from policy import can_auto_resolve, resolution_amount, validate_dispute
from tools.trip_tools import lookup_request, lookup_trip
from tools.credit_tools import get_reride_history
from tools.resolution_tools import (
    issue_credit,
    issue_refund,
    schedule_replacement_credit,
)


class FareDisputeAgent:
    """Multi-step agent orchestration.

    LLM = interpretation.
    Tools = authoritative retrieval, validation and execution.
    SQLite = audit/persistence.
    """

    def __init__(self):
        init_db()

    def process(self, request_id):
        # 1. Get request.
        request = lookup_request(request_id)
        if not request:
            raise ValueError(f"Request not found: {request_id}")

        # 2. Interpret natural language with the in-house LLM.
        interpreted = interpret_request(request)
        save_request(request, interpreted)

        # The dataset's trip_id is authoritative.
        trip_id = str(request["trip_id"])

        # 3. Tool: authoritative trip lookup.
        trip = lookup_trip(trip_id)

        if not trip:
            rationale = "Trip lookup failed; manual review required."
            save_decision(
                request_id, False, False, "UNKNOWN", 0.0, rationale
            )
            return {
                "request": request,
                "interpreted": interpreted,
                "trip": None,
                "decision": {
                    "supported": False,
                    "auto_resolve": False,
                    "resolution_type": "UNKNOWN",
                    "amount": 0.0,
                    "rationale": rationale,
                },
                "action": None,
            }

        # 4. Tool/policy: validate complaint against verified trip category.
        validation = validate_dispute(interpreted["intent"], trip)

        # 5. Determine authoritative resolution amount.
        amount = resolution_amount(trip)

        requested_resolution = interpreted.get(
            "requested_resolution", "UNKNOWN"
        )

        # 6. Separate replacement-credit workflow.
        if requested_resolution == "REPLACEMENT_RIDE_CREDIT":
            history = get_reride_history(request["rider_name"])
            supported = validation["supported"]
            auto = bool(
                supported and history["eligible_for_new_credit"]
            )

            rationale = (
                f"{validation['reason']} "
                f"Recent replacement credits: "
                f"{history['reride_credits_last_30_days']}. "
                f"New replacement credit eligible: "
                f"{history['eligible_for_new_credit']}."
            )

            save_decision(
                request_id,
                supported,
                auto,
                "REPLACEMENT_RIDE_CREDIT",
                0.0,
                rationale,
            )

            action = schedule_replacement_credit(request_id) if auto else None

            return {
                "request": request,
                "interpreted": interpreted,
                "trip": trip,
                "history": history,
                "decision": {
                    "supported": supported,
                    "auto_resolve": auto,
                    "resolution_type": "REPLACEMENT_RIDE_CREDIT",
                    "amount": 0.0,
                    "rationale": rationale,
                },
                "action": action,
            }

        # 7. Refund / fare-credit workflow.
        auto = can_auto_resolve(amount, validation["supported"])

        requested_amount = interpreted.get("requested_amount")
        mismatch_note = ""
        if requested_amount is not None and requested_amount > amount + 0.01:
            mismatch_note = (
                f" Rider requested ${requested_amount:.2f}, but the "
                f"authoritative trip record supports ${amount:.2f}; "
                f"resolution is capped at the trip-record amount."
            )

        rationale = f"{validation['reason']}{mismatch_note}".strip()

        resolution_type = (
            "REFUND"
            if requested_resolution == "REFUND"
            else "FARE_CREDIT"
            if requested_resolution == "CREDIT"
            else requested_resolution
        )

        # Unknown resolution type should go to review rather than execute.
        if resolution_type not in {"REFUND", "FARE_CREDIT"}:
            auto = False

        save_decision(
            request_id,
            validation["supported"],
            auto,
            resolution_type,
            amount,
            rationale,
        )

        action = None
        if auto and resolution_type == "REFUND":
            action = issue_refund(request_id, amount)
        elif auto and resolution_type == "FARE_CREDIT":
            action = issue_credit(request_id, amount)

        return {
            "request": request,
            "interpreted": interpreted,
            "trip": trip,
            "decision": {
                "supported": validation["supported"],
                "auto_resolve": auto,
                "resolution_type": resolution_type,
                "amount": amount,
                "rationale": rationale,
            },
            "action": action,
        }


def process_all():
    agent = FareDisputeAgent()
    from data_store import DataStore

    store = DataStore()
    results = []

    for row in store.list_requests():
        try:
            results.append(agent.process(row["request_id"]))
        except Exception as exc:
            results.append({
                "request_id": row["request_id"],
                "error": str(exc),
            })

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--request-id")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    agent = FareDisputeAgent()

    if args.request_id:
        print(json.dumps(agent.process(args.request_id), indent=2, default=str))
    elif args.all:
        print(json.dumps(process_all(), indent=2, default=str))
    else:
        parser.error("Use --request-id REQUEST_ID or --all")
