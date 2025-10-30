import streamlit as st
import threading
import pandas as pd
from fastapi import FastAPI, Request
import uvicorn
import time
import requests

# Must be the first Streamlit command
st.set_page_config(page_title="Nurse Interface", page_icon="🚑", layout="centered")

# Provide a single shared state across Streamlit reruns and the API thread
@st.cache_resource
def get_shared_state():
    return {"data_store": []}

shared_state = get_shared_state()

def _noop(*args, **kwargs):
    return None

# Track which rows have been confirmed (by index)
if "confirmed_rows" not in st.session_state:
    st.session_state["confirmed_rows"] = []

# --- Configuration for confirm webhook ---
# Prefer setting in .streamlit/secrets.toml as:
# [general]\nN8N_CONFIRM_WEBHOOK_URL = "https://..."
# CONFIRM_WEBHOOK_URL = st.secrets.get("N8N_CONFIRM_WEBHOOK_URL", "")
# if not CONFIRM_WEBHOOK_URL:
    # Optional: allow hardcoding here if secrets not used
CONFIRM_WEBHOOK_URL = "https://lujein.app.n8n.cloud/webhook-test/triage-confirmation"

def _normalize_key(name: str):
    return name.replace("_", "").replace(" ", "").lower()

def _extract_field(row: dict, candidate_names):
    # Try exact, case-insensitive, and normalized matches
    for name in candidate_names:
        if name in row:
            return row.get(name)
    lower_map = {k.lower(): v for k, v in row.items()}
    for name in candidate_names:
        if name.lower() in lower_map:
            return lower_map[name.lower()]
    norm_map = {_normalize_key(k): v for k, v in row.items()}
    for name in candidate_names:
        if _normalize_key(name) in norm_map:
            return norm_map[_normalize_key(name)]
    return None

def _send_confirm(row: dict):
    if not CONFIRM_WEBHOOK_URL:
        return
    payload = {
        "patient_id": _extract_field(row, ["patient_id", "patient id", "id"]),
        "ai_triage_level": _extract_field(row, ["ai_triage_level", "ai triage level", "triage", "esi", "esi_level", "triage_level"]),
    }
    try:
        requests.post(CONFIRM_WEBHOOK_URL, json=payload, timeout=5)
    except Exception:
        pass

# --- Shared in-memory storage (lives in shared_state) ---
data_store = shared_state["data_store"]

# --- FastAPI setup (for receiving data from n8n) ---
api = FastAPI()

@api.post("/api/data")
async def receive_data(request: Request):
    body = await request.json()
    data_store.append(body)
    print("✅ Received data:", body)
    print( "datastore", data_store)
    return {"status": "ok"}

def run_api():
    """Run FastAPI in the background."""
    uvicorn.run(api, host="0.0.0.0", port=8000)

# --- Run FastAPI in background thread (only once) ---
if "_api_thread" not in st.session_state:
    st.session_state["_api_thread"] = threading.Thread(target=run_api, daemon=True)
    st.session_state["_api_thread"].start()

# --- Streamlit UI ---
st.title("🚑 Nurse Interface")

# Listening for data on http://localhost:8000/api/data


def _handle_row_action(row_index: int):
    try:
        row = pd.DataFrame(data_store).iloc[row_index].to_dict()
    except Exception:
        row = {}
    st.session_state["last_row_clicked"] = row

# --- Display data in a table ---
if data_store:
    df = pd.DataFrame(data_store)

    # Render a lightweight table with a last-column button per row
    # Header
    header_cols = st.columns(len(df.columns) + 1)
    for i, col_name in enumerate(df.columns):
        header_cols[i].markdown(f"**{col_name}**")
    header_cols[-1].markdown("**Confirm?**")

    # Rows
    for idx, row in df.iterrows():
        row_cols = st.columns(len(df.columns) + 1)
        for i, col_name in enumerate(df.columns):
            row_cols[i].write(row[col_name])
        label = "done" if idx in st.session_state["confirmed_rows"] else "✅"
        if row_cols[-1].button(label, key=f"row_action_{idx}"):
            if idx not in st.session_state["confirmed_rows"]:
                # Send confirmation webhook once per row
                _send_confirm(row.to_dict())
                st.session_state["confirmed_rows"].append(idx)
            st.rerun()
else:
    st.info("No patients yet!")

# --- Auto-refresh (poll for new data) ---
# Always refresh every 2 seconds without user interaction
time.sleep(2)
st.rerun()
