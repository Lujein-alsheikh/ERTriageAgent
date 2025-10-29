from pandas.core.missing import F
import streamlit as st
import requests
import datetime
import json
import re
import ast


def extract_patient_data(data):
    """
    Parses the specific n8n output format like:
    [{'output': '[{\'output\': \'{\\n  "patient_id": 123456, ... }\'}]'}]

    Returns a clean Python dict, e.g.:
    {'patient_id': 123456, 'age': 29, ...}
    """
    try:
        # 1️⃣ Outer list
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        else:
            raise ValueError("Unexpected data format (not a list).")

        # 2️⃣ Get 'output' key (string containing list-like text)
        output_str = data.get("output")
        if not isinstance(output_str, str):
            raise ValueError("Missing or invalid 'output' key.")

        # 3️⃣ Convert the inner list-like string to a Python object
        # Use ast.literal_eval because it's not valid JSON (single quotes)
        inner_list = ast.literal_eval(output_str)
        if not inner_list or not isinstance(inner_list, list):
            raise ValueError("Inner 'output' is not a list.")

        inner_dict = inner_list[0]
        if not isinstance(inner_dict, dict) or "output" not in inner_dict:
            raise ValueError("Inner list item missing 'output' key.")

        # 4️⃣ Parse the final JSON string inside
        patient_json_str = inner_dict["output"]
        patient_data = json.loads(patient_json_str)

        return patient_data

    except Exception as e:
        print(f"❌ Failed to parse patient data: {e}")
        return {}


# ---- CONFIG ----
API_URL = "https://lujein.app.n8n.cloud/webhook/reception"  

st.set_page_config(page_title="ER Receptionist Prototype", page_icon="🏥", layout="centered")
st.title("🏥 ER Receptionist Interface")

# --- Ensure session_state keys exist ---
defaults = {
    "patient_id": "",
    "age": 0,
    "arrival_time": datetime.datetime.now().time(),
    "chief_complaint_and_reported_symptoms": "",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- Inputs bound to keys ---
st.text_input("Patient ID", key="patient_id")
st.number_input("Age", min_value=0, max_value=120, step=1, key="age")
# st.time_input("Time of Arrival", value=st.session_state.arrival_time, key="arrival_time")
st.text_area("Chief Complaint and Reported Symptoms", key="chief_complaint_and_reported_symptoms")

col1, col2, col3 = st.columns(3)

# --- Submit button ---
with col1:
    if st.button("Submit"):
        data = {
            "patient_id": st.session_state.patient_id,
            "age": st.session_state.age,
            "arrival_time": str(st.session_state.arrival_time),
            "chief_complaint_and_reported_symptoms": st.session_state.chief_complaint_and_reported_symptoms,
            "simulate": False,
        }
        try:
            response = requests.post(API_URL, json=data)
            response.raise_for_status()
            st.success(f"✅ Data sent successfully! (Status: {response.status_code})")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Failed to send data: {e}")

# --- Simulate button ---
with col2:
    if st.button("Simulate Data"):
        empty_data = {
            "patient_id": "",
            "age": 0,
            "arrival_time": str(st.session_state.arrival_time),
            "chief_complaint_and_reported_symptoms": "",
            "simulate": True,
        }
        try:
            response = requests.post(API_URL, json=empty_data)
            response.raise_for_status()
            st.success(f"✅ Simulated data requested! (Status: {response.status_code})")

            # Parse and apply simulated data
            try:
                simulated_data = response.json()
                print(f"simulated data {simulated_data}")
            except ValueError:
                st.error("❌ Failed to parse JSON from simulation response.")
            else:
                parsed = extract_patient_data(simulated_data)
                print(f"parsing result: {parsed}")
                patient_id = parsed.get("patient_id")

                if patient_id:
                    print("patient id extracted!")
                    st.success(f"✅ Received simulated patient data from n8n! (Status: {response.status_code})")
                    # Populate bound fields if available
                    for key in ["patient_id", "age", "arrival_time", "chief_complaint_and_reported_symptoms"]:
                        if key in parsed and parsed[key] is not None:
                            st.session_state[key] = parsed[key]

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Failed to send simulation request: {e}")

# --- Refresh button ---
with col3:
    if st.button("Refresh"):
        for key in list(defaults.keys()):
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

                # for key in ["patient_id", "age", "arrival_time", "chief_complaint_and_reported_symptoms"]:
                #     if key in simulated_data:
                #         st.session_state[key] = simulated_data[key]

                # If patient_id is non-empty (which means that the data record is not empty.)
                # if bool(simulated_data.get("patient_id")):
                #     st.success(f"✅ Received simulated patient data from n8n! (Status: {response.status_code})")
