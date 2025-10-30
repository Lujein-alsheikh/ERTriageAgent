import streamlit as st
import threading
import pandas as pd
from fastapi import FastAPI, Request
import uvicorn
import time

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
                st.session_state["confirmed_rows"].append(idx)
            st.rerun()
else:
    st.info("No patients yet!")

# --- Auto-refresh (poll for new data) ---
# Always refresh every 2 seconds without user interaction
time.sleep(2)
st.rerun()
