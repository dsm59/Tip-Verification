# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 15:39:55 2026

@author: Daniel
"""

# app.py
import streamlit as st
import pandas as pd
from backend import (
    find_tare_weight_irregularities, 
    upload_opsportal_export, 
    find_load_weight_irregularities
)

# Configure the Streamlit page
st.set_page_config(page_title="Weight Irregularities Detector", layout="wide")

st.title("Truck Weight Irregularities Detector")
st.write("Upload your OpsPortal product export to detect tare and load weight anomalies.")

# -----------
# USER INPUTS

# 1. File Upload interface
uploaded_file = st.file_uploader("Upload Tip and Product Report (.tsv)", type=['tsv', 'txt', 'csv'])

# 2. Number input for days
num_days_ago = st.number_input(
    "Number of days ago to check", 
    min_value=1, 
    value=31, 
    step=1,
    help="How far back results should show (e.g., 31 for the last month)."
)

# ------------
# EXECUTION

if st.button("Find Irregularities", type="primary"):
    if uploaded_file is not None:
        with st.spinner("Processing data..."):
            try:
                # The Streamlit UploadedFile object acts like a file path, 
                # so it works seamlessly with your backend's pd.read_csv()
                opsportal_df = upload_opsportal_export(uploaded_file)
                
                # Find irregularities
                excess_tare_weight = find_tare_weight_irregularities(opsportal_df, num_days_ago)
                excess_load_weight = find_load_weight_irregularities(opsportal_df, num_days_ago)
                
                # Display Tare Weight Results
                st.subheader("Excess Tare Weight")
                st.write("Tare weight is at least 400 kg above the total dataset average for the truck.")
                # We check isinstance to gracefully handle if the backend returns pd.dataframe (the class itself) instead of a DataFrame instance
                if isinstance(excess_tare_weight, pd.DataFrame) and not excess_tare_weight.empty:
                    st.dataframe(excess_tare_weight, use_container_width=True)
                else:
                    st.success("No tare weight irregularities detected.")
                
                st.divider()
                
                # Display Load Weight Results
                st.subheader("Excess Load Weight")
                st.write("Load weight is at least 1000 kg above the monthly average for the specific day and run.")
                if isinstance(excess_load_weight, pd.DataFrame) and not excess_load_weight.empty:
                    st.dataframe(excess_load_weight, use_container_width=True)
                else:
                    st.success("No load weight irregularities detected.")
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload an OpsPortal export file to begin.")