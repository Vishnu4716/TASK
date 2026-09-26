# Fare Dispute Resolution Agent — Submission Manifest

## Solution files

The solution is organized as follows:

```text
APP-RIDE-LVL3/
├── app.py
├── agent.py
├── llm.py
├── data_store.py
├── policy.py
├── database.py
├── config.py
├── test_agent.py
├── README.md
├── MANIFEST.md
└── tools/
    ├── __init__.py
    ├── trip_tools.py
    ├── credit_tools.py
    └── resolution_tools.py
```

### File responsibilities

- `app.py` — Streamlit review interface, agent execution, audit history, and human-review/override UI.
- `agent.py` — multi-step agent/orchestrator coordinating LLM interpretation, authoritative lookup, evidence validation, policy decision, resolution action, and persistence.
- `llm.py` — OpenAI-compatible chat-completions client used for natural-language dispute interpretation.
- `data_store.py` — loading and lookup of authoritative dispute requests and trip records.
- `policy.py` — deterministic evidence validation, resolution amount calculation, auto-resolution threshold, and replacement-credit eligibility checks.
- `database.py` — SQLite persistence and audit trail.
- `tools/trip_tools.py` — request and authoritative trip lookup tools.
- `tools/credit_tools.py` — replacement-credit history lookup tool.
- `tools/resolution_tools.py` — refund, fare-credit, and resolution/scheduling action tools.
- `tools/__init__.py` — Python package marker for the tools module.
- `config.py` — environment configuration and configurable policy thresholds.
- `test_agent.py` — unit tests covering supported/unsupported disputes, auto-resolution threshold behavior, and resolution amount logic.
- `README.md` — setup, configuration, and usage instructions.
- `MANIFEST.md` — submission manifest and design rationale.

## Data files

The challenge-provided data files are used as authoritative inputs:

- `fare_dispute_requests.csv` — rider dispute requests.
- `trip_records.csv` — authoritative trip records and verified dispute categories.
- `reride_credit_history.csv` — recent replacement-credit history.

These are challenge-provided data files and are not duplicated as solution source files.

## Agent flow

LLM interpretation
→ authoritative request/trip lookup
→ evidence validation
→ deterministic policy decision
→ resolution tool
→ database audit

## Resolution behavior

- The LLM interprets the rider's natural-language request but does not invent authoritative trip facts.
- The request's trip ID is used to retrieve the authoritative trip record.
- The verified trip category is treated as the source of truth when validating the interpreted intent.
- Resolution amounts are derived from authoritative trip data rather than blindly using the rider's requested amount.
- Supported disputes can be auto-resolved only when the resolution amount is within the configured autonomous-resolution threshold.
- The challenge default autonomous-resolution threshold is `$50.00`, exposed as a configurable value in `config.py`.
- Unsupported or evidence-mismatched disputes do not trigger autonomous actions and are routed to human review.
- Refund and fare-credit resolutions are handled through dedicated resolution tools.
- Already-executed actions are detected and are not executed again.
- Replacement-credit requests perform a separate recent-credit history check before issuing/scheduling credit.
- Autonomous actions and human overrides are persisted in the audit trail.

## Human review

The Streamlit UI exposes:

- Rider request and interpreted intent.
- Authoritative trip evidence.
- Agent decision and rationale.
- Action status, including already-executed actions.
- Human review/override controls for cases that are not eligible for autonomous resolution.

## Validation and tests

The implementation includes deterministic unit tests for:

- Supported surge-overcharge validation.
- Unsupported rider-cancellation validation.
- Autonomous-resolution threshold behavior.
- Resolution amount selection from authoritative trip data.

The final test suite passes with all four tests successful.

## Under-specified item

The brief describes a “reasonable value threshold” without specifying a number. The implementation uses `$50.00` as the challenge default and keeps the threshold configurable through `config.py`, so the policy logic can remain unchanged if the challenge environment specifies a different value.
