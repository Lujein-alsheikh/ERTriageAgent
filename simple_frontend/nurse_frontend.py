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
if "triage_override" not in st.session_state:
    st.session_state["triage_override"] = {}

# --- Configuration for confirm webhook ---
# Prefer setting in .streamlit/secrets.toml as:
# [general]\nN8N_CONFIRM_WEBHOOK_URL = "https://..."
# CONFIRM_WEBHOOK_URL = st.secrets.get("N8N_CONFIRM_WEBHOOK_URL", "")
# if not CONFIRM_WEBHOOK_URL:
    # Optional: allow hardcoding here if secrets not used
CONFIRM_WEBHOOK_URL = "https://lujein.app.n8n.cloud/webhook/triage-confirmation"

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

TRIAGE_COLUMN_NAME = "triage level"

def _send_confirm(row: dict):
    if not CONFIRM_WEBHOOK_URL:
        return
    payload = {
        "patient_id": _extract_field(row, ["patient_id", "patient id", "id"]),
        "triage_level": row.get("triage level"),
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
    triage_col = TRIAGE_COLUMN_NAME if TRIAGE_COLUMN_NAME in df.columns else None
    header_cols = st.columns(len(df.columns) + 1)
    for i, col_name in enumerate(df.columns):
        label = f"**{col_name}**" if col_name != triage_col else f"**{col_name}**"
        header_cols[i].markdown(label)
    header_cols[-1].markdown("**Confirm?**")

    # Rows
    for idx, row in df.iterrows():
        row_cols = st.columns(len(df.columns) + 1)
        for i, col_name in enumerate(df.columns):
            if col_name == triage_col:
                # Editable triage level control
                current_val = st.session_state["triage_override"].get(idx, row[col_name])
                # Accept common ESI levels 1-5 as strings or ints
                options = ["1", "2", "3", "3 - Vital Signs Needed", "4", "5"]
                default_str = str(current_val) if current_val is not None else ""
                selected = row_cols[i].selectbox(
                    "Triage Level",  # Non-empty label for accessibility,
                    options,
                    index=options.index(default_str) if default_str in options else 0,
                    key=f"triage_sel_{idx}",
                    label_visibility="collapsed",  # Hides the label in the UI
                )
                st.session_state["triage_override"][idx] = selected
            else:
                row_cols[i].write(row[col_name])
        label = "done" if idx in st.session_state["confirmed_rows"] else "✅"
        if row_cols[-1].button(label, key=f"row_action_{idx}"):
            if idx not in st.session_state["confirmed_rows"]:
                # Send confirmation webhook once per row, using override if present
                row_dict = row.to_dict()
                override = st.session_state["triage_override"].get(idx)
                if override is not None and triage_col is not None:
                    row_dict[triage_col] = override
                _send_confirm(row_dict)
                st.session_state["confirmed_rows"].append(idx)
            st.rerun()
else:
    st.info("No patients yet!")

# --- Auto-refresh (poll for new data) ---
# Always refresh every 2 seconds without user interaction
time.sleep(2)
st.rerun()
