# Fare Dispute Resolution Agent

An agentic fare-dispute resolution system that combines LLM-based request interpretation with authoritative trip evidence, deterministic policy validation, resolution tools, persistence, and a Streamlit review interface.

## Architecture

```text
Rider dispute
    ↓
LLM interpretation
    ↓
Authoritative request/trip lookup
    ↓
Evidence validation
    ↓
Deterministic policy decision
    ↓
Resolution action
    ↓
SQLite audit persistence
```

The LLM is used to interpret the rider's natural-language request. Authoritative trip data and deterministic policy logic control whether an action is supported and whether it can be executed autonomously.

## Project structure

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
├── llm_smoke_test.py
├── README.md
├── MANIFEST.md
└── tools/
    ├── trip_tools.py
    ├── credit_tools.py
    └── resolution_tools.py
```

## Main components

- `app.py` — Streamlit UI for selecting disputes, running the agent, viewing evidence/decisions/actions, audit history, and human review/override.
- `agent.py` — orchestrates the end-to-end dispute-resolution flow.
- `llm.py` — OpenAI-compatible chat-completions client for natural-language interpretation.
- `data_store.py` — loads and retrieves authoritative request and trip data.
- `policy.py` — deterministic evidence validation, resolution amount, auto-resolution threshold, and replacement-credit eligibility logic.
- `database.py` — SQLite persistence and audit history.
- `tools/trip_tools.py` — request/trip lookup tools.
- `tools/credit_tools.py` — replacement-credit history lookup.
- `tools/resolution_tools.py` — refund, fare-credit, and resolution action tools.
- `config.py` — configurable environment settings and policy thresholds.
- `test_agent.py` — deterministic unit tests.
- `llm_smoke_test.py` — lightweight LLM connectivity/smoke test.
- `MANIFEST.md` — submission structure and design rationale.

## Data

The challenge provides these data files:

- `fare_dispute_requests.csv`
- `trip_records.csv`
- `reride_credit_history.csv`

The trip record is treated as authoritative for verified dispute category and resolution value.

## Policy behavior

### Supported disputes

When the interpreted intent matches the authoritative trip category, the dispute can be supported.

For supported cases:

- The resolution amount is derived from authoritative trip data.
- Autonomous resolution is allowed only when the amount is within the configured threshold.
- Refund and fare-credit actions are executed through dedicated resolution tools.

### Unsupported disputes

If the rider's interpreted intent does not match the authoritative trip category:

- `supported` is `false`.
- `auto_resolve` is `false`.
- No autonomous action is taken.
- The case is available for human review/override.

### Already-executed actions

The resolution layer checks for previously executed actions. If an action has already been completed, it returns an `ALREADY_EXECUTED` status instead of performing the action again.

### Replacement credits

Replacement-credit requests use a separate recent-credit history lookup before issuing/scheduling credit.

## Autonomous-resolution threshold

The challenge default is `$50.00`.

The threshold is configurable through `config.py` / environment configuration rather than being embedded in the policy logic.

## Human review

The Streamlit interface provides a human-review/override section for cases that cannot be autonomously resolved. Decisions and overrides are persisted to the audit trail.

## Running locally

Create and activate a virtual environment, then install the required dependencies from the project environment.

Start the Streamlit application:

```bash
streamlit run app.py
```

The application opens a local Streamlit URL, normally:

```text
http://localhost:8501
```

## Command-line agent

A dispute can also be processed directly through the agent:

```bash
python agent.py --request-id FD-XXXX
```

Replace `FD-XXXX` with a request ID from the provided dispute-request data.

## Testing

Run the deterministic policy/unit tests:

```bash
python -m unittest test_agent.py
```

The implemented test suite covers:

- supported surge-overcharge validation
- unsupported rider-cancellation validation
- autonomous-resolution threshold behavior
- resolution amount selection from authoritative trip data

The LLM smoke test can be run separately when the configured LLM endpoint/credentials are available:

```bash
python llm_smoke_test.py
```

## Design principles

1. **Authoritative evidence over LLM assumptions** — the LLM interprets language but does not invent trip facts.
2. **Deterministic policy enforcement** — support and autonomous-resolution decisions are made by explicit policy logic.
3. **Safe autonomous actions** — unsupported cases and cases outside the autonomous threshold do not trigger autonomous resolution.
4. **Idempotent resolution behavior** — already-executed actions are detected to avoid duplicate actions.
5. **Auditability** — autonomous actions and human overrides are persisted.
6. **Human-in-the-loop** — unsupported or non-autonomous cases remain available for human review.

## Under-specified requirement

The brief refers to a “reasonable value threshold” without specifying an exact number. The implementation uses `$50.00` as the challenge default and keeps it configurable so the policy can be changed without modifying the core decision logic.
