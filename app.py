import streamlit as st

from agent import FareDisputeAgent
from database import get_history, init_db, save_override
from data_store import DataStore

st.set_page_config(
    page_title="Fare Dispute Resolution Agent",
    layout="wide",
)

init_db()
agent = FareDisputeAgent()
store = DataStore()

st.title("Fare Dispute Resolution Agent")
st.caption(
    "LLM interpretation → tool lookups → evidence validation → "
    "policy → action → persistence"
)

requests = store.list_requests()

if not requests:
    st.error(
        "No requests found. Put the three challenge CSV files under data/."
    )
    st.stop()

request_labels = {
    f"{r['request_id']} — {r['rider_name']} — {r['trip_id']}":
        r["request_id"]
    for r in requests
}

selected_label = st.selectbox(
    "Select a dispute request",
    list(request_labels),
)
selected_id = request_labels[selected_label]

if st.button("Run agent", type="primary"):
    try:
        st.session_state["last_result"] = agent.process(selected_id)
    except Exception as exc:
        st.exception(exc)

result = st.session_state.get("last_result")

if result:
    st.divider()

    request = result["request"]
    interpreted = result["interpreted"]
    trip = result.get("trip")
    decision = result["decision"]
    action = result.get("action")

    c1, c2, c3 = st.columns(3)
    c1.metric("Request", request["request_id"])
    c2.metric("Trip", request["trip_id"])
    c3.metric("Rider", request["rider_name"])

    st.subheader("Rider request")
    st.write(request["request_text"])

    st.subheader("LLM interpretation")
    st.json(interpreted)

    st.subheader("Authoritative trip record")
    if trip:
        st.json(trip)
    else:
        st.error("Trip not found.")

    if "history" in result:
        st.subheader("Replacement-credit history")
        st.json(result["history"])

    st.subheader("Agent decision")
    st.json(decision)

    if action:
        st.success(
            f"Action: {action['status']} — {action['details']}"
        )
    else:
        st.info(
            "No autonomous action taken; human review is required."
        )

    st.subheader("Human review / override")
    reviewer = st.text_input("Reviewer", value="human-reviewer")
    override_status = st.selectbox(
        "Override status",
        ["APPROVED", "REJECTED", "MANUAL_REVIEW"],
    )
    note = st.text_area("Override note")

    if st.button("Save override"):
        if not note.strip():
            st.warning("Enter an override note.")
        else:
            save_override(
                selected_id,
                reviewer,
                override_status,
                note,
            )
            st.success("Override persisted to SQLite.")

st.divider()
st.subheader("Persisted audit history")

history = get_history()
if history:
    st.dataframe(history, use_container_width=True)
else:
    st.info("No processed requests yet.")
