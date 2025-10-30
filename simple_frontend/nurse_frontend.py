import streamlit as st
import threading
import pandas as pd
from fastapi import FastAPI, Request
import uvicorn

# --- Shared in-memory storage ---
data_store = []

# --- FastAPI setup (for receiving data from n8n) ---
api = FastAPI()

@api.post("/api/data")
async def receive_data(request: Request):
    body = await request.json()
    data_store.append(body)
    print("✅ Received data:", body)
    return {"status": "ok"}

def run_api():
    """Run FastAPI in the background."""
    uvicorn.run(api, host="0.0.0.0", port=8001)

# --- Run FastAPI in background thread ---
thread = threading.Thread(target=run_api, daemon=True)
thread.start()

# --- Streamlit UI ---
st.set_page_config(page_title="Nurse Interface", layout="wide")
st.title("📊 Data Received from n8n")

st.write("Listening for data on **http://localhost:8000/api/data**")

# Option to refresh manually
if st.button("🔄 Refresh Table"):
    st.experimental_rerun()

# --- Display data in a table ---
if data_store:
    df = pd.DataFrame(data_store)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No data received yet. Waiting for n8n to send something...")
