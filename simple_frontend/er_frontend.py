from pandas.core.missing import F
import streamlit as st
import requests
import datetime

# ---- CONFIG ----
API_URL = "https://lujein.app.n8n.cloud/webhook-test/reception"  

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
            # Show that the simulation request was accepted by n8n
            st.success(f"✅ Simulated data requested! (Status: {response.status_code})")

            # Parse and apply simulated data
            try:
                simulated_data = response.json()
            except ValueError:
                st.error("❌ Failed to parse JSON from simulation response.")
            else:
                for key in ["patient_id", "age", "arrival_time", "chief_complaint_and_reported_symptoms"]:
                    if key in simulated_data:
                        st.session_state[key] = simulated_data[key]

                # Only show success if any of the fields are non-empty
                has_non_empty = any([
                    bool(simulated_data.get("patient_id")),
                    bool(simulated_data.get("age")),
                    bool(simulated_data.get("arrival_time")),
                    bool(simulated_data.get("chief_complaint_and_reported_symptoms")),
                ])
                if has_non_empty:
                    st.success(f"✅ Received simulated patient data from n8n! (Status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Failed to send simulation request: {e}")

# --- Refresh button ---
with col3:
    if st.button("Refresh"):
        for key in list(defaults.keys()):
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()



       #    st.success(f"✅ Simulated data requested! (Status: {response.status_code})")

       # st.json(empty_data) # Renders the empty_data dict as formatted JSON in the Streamlit app (i.e., shows that JSON on the screen).

            # simulated_data = response.json()
            # print(simulated_data)
            
            # for key in ["patient_id", "age", "arrival_time", "chief_complaint_and_reported_symptoms"]:
            #     if key in simulated_data:
            #         st.session_state[key] = simulated_data[key]

            # st.success("✅ Received simulated patient data from n8n!")
            # st.json(simulated_data)

                        
            # # ✅ Clear fields safely
            # for key in list(defaults.keys()):
            #     if key in st.session_state:
            #         del st.session_state[key]
            # st.rerun()