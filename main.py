# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 10:41:24 2026

@author: Daniel
"""
from backend import find_tare_weight_irregularities, upload_opsportal_export,find_load_weight_irregularities

# -----------
# USER INPUTS
opsportal_tsv_path = "C:/Users/Daniel/Downloads/Tip_and_Product_Report-16-04-2025-16-04-2026.tsv"
num_days_ago = 31 # How far back results should show, eg. if 31 is put in all irregularities for last 31 days will be found (assuming Opsportl export covers this far back)

# ------------
# UPLOAD FILES
opsportal_df      = upload_opsportal_export(opsportal_tsv_path)

# -------------------
# FIND IRREGULARITIES

# Shows if tare weight is at least 400 kg above total dataset average
excess_tare_weight = find_tare_weight_irregularities(opsportal_df, num_days_ago)

# Shows if load weight is at least 1000 kg above last 31 day (monthly) average
excess_load_weight = find_load_weight_irregularities(opsportal_df, num_days_ago)

