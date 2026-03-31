"""
Feedback Review page for the Admin panel.

Reads from the orchestrator's unified feedback endpoint so all feedback —
from the accelerator chat and any other future source — is visible in one place.

Required env var:
    ORCHESTRATOR_API_URL   Base URL of the orchestrator FastAPI service
                           (default: http://localhost:8000)
"""

import os
import sys
import logging
import requests
import streamlit as st
import pandas as pd
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
logger = logging.getLogger(__name__)

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_API_URL", "http://localhost:8001")

st.set_page_config(
    page_title="Feedback Review",
    page_icon=os.path.join(os.path.dirname(__file__), "..", "images", "favicon.ico"),
    layout="wide",
    menu_items=None,
)


def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css(os.path.join(os.path.dirname(__file__), "common.css"))

st.title("Feedback Review")
st.caption(f"Data source: {ORCHESTRATOR_URL}/feedback")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fetch_stats() -> dict:
    try:
        r = requests.get(f"{ORCHESTRATOR_URL}/feedback/stats", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Could not fetch stats: {e}")
        return {}


def fetch_feedback(
    source_app: str | None,
    feedback_type: str | None,
    limit: int,
    skip: int,
) -> dict:
    params: dict = {"limit": limit, "skip": skip}
    if source_app:
        params["source_app"] = source_app
    if feedback_type:
        params["feedback_type"] = feedback_type
    try:
        r = requests.get(f"{ORCHESTRATOR_URL}/feedback", params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Could not fetch feedback records: {e}")
        return {}


def ts_to_str(ts) -> str:
    """Convert a millisecond timestamp to a human-readable string."""
    try:
        return datetime.utcfromtimestamp(int(ts) / 1000).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return str(ts)


# ---------------------------------------------------------------------------
# Metrics header
# ---------------------------------------------------------------------------

stats = fetch_stats()

if stats:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total feedback", stats.get("total_feedback", 0))
    col2.metric("Positive", stats.get("thumbs_up", 0))
    col3.metric("Negative", stats.get("thumbs_down", 0))
    satisfaction = stats.get("satisfaction_rate", 0)
    col4.metric("Satisfaction", f"{satisfaction}%")

    by_intent = stats.get("by_intent", {})
    if by_intent:
        with st.expander("Breakdown by intent"):
            intent_rows = [
                {
                    "Intent": intent,
                    "Total": v["total"],
                    "Positive": v["thumbs_up"],
                    "Negative": v["thumbs_down"],
                    "Satisfaction %": (
                        round(v["thumbs_up"] / v["total"] * 100, 1) if v["total"] else 0
                    ),
                }
                for intent, v in by_intent.items()
            ]
            st.dataframe(
                pd.DataFrame(intent_rows).sort_values("Total", ascending=False),
                use_container_width=True,
                hide_index=True,
            )

st.divider()

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

col_a, col_b, col_c = st.columns([2, 2, 1])

with col_a:
    source_filter = st.selectbox(
        "Source app",
        options=["All", "accelerator", "orchestrator"],
        index=0,
    )

with col_b:
    type_filter = st.selectbox(
        "Feedback type",
        options=["All", "thumbs_up", "thumbs_down"],
        index=0,
    )

with col_c:
    page_size = st.selectbox("Rows per page", options=[25, 50, 100], index=0)

if "feedback_skip" not in st.session_state:
    st.session_state.feedback_skip = 0

col_prev, col_next, _ = st.columns([1, 1, 8])
with col_prev:
    if st.button("Previous", use_container_width=True) and st.session_state.feedback_skip >= page_size:
        st.session_state.feedback_skip -= page_size
with col_next:
    if st.button("Next", use_container_width=True):
        st.session_state.feedback_skip += page_size

# Reset pagination when filters change
filter_key = f"{source_filter}|{type_filter}|{page_size}"
if "last_filter_key" not in st.session_state or st.session_state.last_filter_key != filter_key:
    st.session_state.feedback_skip = 0
    st.session_state.last_filter_key = filter_key

# ---------------------------------------------------------------------------
# Feedback table
# ---------------------------------------------------------------------------

data = fetch_feedback(
    source_app=None if source_filter == "All" else source_filter,
    feedback_type=None if type_filter == "All" else type_filter,
    limit=page_size,
    skip=st.session_state.feedback_skip,
)

records = data.get("feedback", [])
total = data.get("total", 0)
current_page = st.session_state.feedback_skip // page_size + 1
total_pages = max(1, -(-total // page_size))  # ceiling division

st.caption(
    f"Showing {st.session_state.feedback_skip + 1}–"
    f"{min(st.session_state.feedback_skip + page_size, total)} of {total} records  "
    f"(page {current_page}/{total_pages})"
)

if records:
    rows = []
    for r in records:
        fb_type = r.get("feedback_type", "")
        rows.append(
            {
                "Time": ts_to_str(r.get("timestamp", 0)),
                "Feedback": "Good" if fb_type == "thumbs_up" else "Bad",
                "Source": r.get("source_app", "—"),
                "Intent": r.get("intent") or "—",
                "Session ID": r.get("session_id", ""),
                "User message": (r.get("user_message") or "")[:120],
                "Assistant message": (r.get("assistant_message") or "")[:200],
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("No feedback records found for the selected filters.")
