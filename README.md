# Fare Dispute Resolution Agent

A 24-hour challenge implementation for autonomous fare-dispute handling.

## Architecture

1. Read the three challenge CSV datasets.
2. Use the in-house LLM to interpret each rider request.
3. Use deterministic tools to retrieve the authoritative trip record.
4. Validate the interpreted reason against `verified_category`.
5. Apply an explicit auto-resolution threshold.
6. Execute refund/fare-credit actions through tools when eligible.
7. For replacement ride credit, retrieve recent rider history before scheduling.
8. Persist requests, decisions, actions, and human overrides in SQLite.
9. Provide a Streamlit UI for execution and human review.

## Setup

Use Python 3.11+.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set a fresh company API key.

Put the challenge datasets here:

```text
data/fare_dispute_requests.csv
data/trip_records.csv
data/reride_credit_history.csv
```

## Test the LLM gateway

```bash
python llm_smoke_test.py
```

## Process one request

```bash
python agent.py --request-id FD-9031
```

Use an ID that exists in your CSV.

## Process all requests

```bash
python agent.py --all
```

## Run the UI

```bash
streamlit run app.py
```

## Policy note

The challenge brief says auto-resolution should be restricted to a reasonable value threshold but does not specify a numeric threshold in the supplied brief. The implementation therefore uses `$50.00` as a configurable default in `.env`.

The authoritative trip record is used for the resolution amount rather than blindly trusting a rider's requested amount.

## Security

Never commit `.env` or an API key. If a key was exposed in a screenshot or repository, revoke/rotate it immediately.
