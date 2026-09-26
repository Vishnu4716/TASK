# Submission Manifest

## Files

- `app.py` — Streamlit review interface.
- `agent.py` — multi-step agent/orchestrator.
- `llm.py` — in-house OpenAI-compatible chat-completions client.
- `data_store.py` — CSV loading and lookup tools.
- `policy.py` — deterministic evidence and auto-resolution policy.
- `database.py` — SQLite persistence and audit trail.
- `tools/trip_tools.py` — request/trip lookup tools.
- `tools/credit_tools.py` — replacement-credit history tool.
- `tools/resolution_tools.py` — refund/credit/scheduling action tools.
- `config.py` — environment configuration.
- `README.md` — setup and usage.
- `MANIFEST.md` — submission manifest.

## Agent flow

LLM interpretation → authoritative tool lookup → evidence validation → policy decision → resolution tool → database audit.

## Deliberate design decisions

- The LLM interprets natural language but does not get to invent authoritative trip facts.
- The dataset's trip ID is treated as authoritative.
- Resolution amount comes from the trip record.
- Auto-resolution is disabled when evidence does not support the complaint.
- Auto-resolution is restricted by a configurable value threshold.
- Replacement-credit requests use a separate history lookup before scheduling.
- All autonomous actions and overrides are persisted.
- Human review is available in the UI.

## Under-specified item

The brief specifies a "reasonable value threshold" without a number. The implementation uses `$50.00` as a configurable default. If the challenge environment provides a more specific policy, change only the environment/config value and document the change.
