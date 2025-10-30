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
    print( "datastore", data_store)
    return {"status": "ok"}

def run_api():
    """Run FastAPI in the background."""
    uvicorn.run(api, host="0.0.0.0", port=8000)

# --- Run FastAPI in background thread ---
thread = threading.Thread(target=run_api, daemon=True)
thread.start()

# --- Streamlit UI ---
st.set_page_config(page_title="Nurse Interface", page_icon="🚑", layout="centered")
st.title("🚑 Nurse Interface")

# Listening for data on http://localhost:8000/api/data


# --- Display data in a table ---
if data_store:
    print("data stor recognized")
    df = pd.DataFrame(data_store)
    st.dataframe(df, use_container_width=True)
else:
    print("data not recognized!")
    st.info("No patients yet!")
