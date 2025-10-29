import json
import re
import streamlit as st

import json
import re
import streamlit as st


simulated_data = [{'output': '[{\'output\': \'{\\n  "patient_id": 123456,\\n  "age": 29,\\n  "arrival_time": "16:39:18",\\n  "chief_complaint_and_reported_symptoms": "Severe chest pain and shortness of breath"\\n}\'}]'}]



import json
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





parsed = extract_patient_data(simulated_data)
print(parsed)
print(parsed.get("patient_id"))