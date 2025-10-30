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


# --- Display data in a table ---
if data_store:
    # print("data stor recognized")
    df = pd.DataFrame(data_store)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    # print("data not recognized!")
    st.info("No patients yet!")

# --- Auto-refresh (poll for new data) ---
# Always refresh every 2 seconds without user interaction
time.sleep(2)
st.rerun()
