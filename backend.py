# -*- coding: utf-8 -*-
"""
DIFFERENT COMPANIES
    - OJI (paper)
    - VISY (glass)
    - Envirofert
    - WM Selwood
    - WM Rosedale
    - WM Neales
    - WM Southdown

1. Upload invoice csv
2. Upload OpsPortal product csv
3. Math trucks
4. Verify are same:
    a) Use tare weight to determine if truck weight is exagerated [Thien method]
    b) Detect total weight (trash) irregularities [Siang method]
5. Return results to user

@author: Daniel
"""
import pandas as pd

def upload_opsportal_export(opsportal_tsv_path):
    opsportal_df = pd.read_csv(opsportal_tsv_path, sep='\t',index_col=False)
    # Set timestamp to datetime
    opsportal_df['Timestamp'] = pd.to_datetime(opsportal_df['Timestamp'], format='%d/%m/%Y %H:%M:%S')
    # Set Tare, Gross, Common weight to int
    opsportal_df['Gross Weight'] = pd.to_numeric(opsportal_df['Gross Weight'].str.replace(',',''))
    opsportal_df['Tare Weight'] = pd.to_numeric(opsportal_df['Tare Weight'].str.replace(',',''))
    opsportal_df['Weight'] = pd.to_numeric(opsportal_df['Weight'].str.replace(',',''))
    return opsportal_df

def find_tare_weight_irregularities(opsportal_df, num_days_ago):
    trucks = opsportal_df['Truck'].unique() 
    excess_tare_weight_list = []
    for i in range(len(trucks)):
        selected_truck = opsportal_df[opsportal_df['Truck'] == trucks[i]]
        selected_truck = selected_truck[selected_truck['Tare Weight'] != 0]
        median_tare = selected_truck['Tare Weight'].median(skipna=True)
        # Find tare weights where more than 400 kg above average
        excess_tare_weight = selected_truck[(selected_truck['Tare Weight'] >= (median_tare+400)) & (selected_truck['Timestamp'] > pd.Timestamp.now().normalize() - pd.Timedelta(days=num_days_ago))].copy().reset_index()
        if not excess_tare_weight.empty:
            for j in range(len(excess_tare_weight)):
                tare_weight = excess_tare_weight.loc[j,'Tare Weight']
                excess_tare_weight.loc[j,'Problem'] = f"High tare weight detected: {tare_weight - median_tare} kg above median"
            
            excess_tare_weight.loc[:,'Median Tare Weight'] = median_tare
        
        excess_tare_weight_list.append(excess_tare_weight)
    
    if len(excess_tare_weight_list) > 0:
        excess_tare_weight_df = pd.concat(excess_tare_weight_list)
        return excess_tare_weight_df.drop(columns=['Product','Avg Bin Weight','Total Bins','Card Bins','index'])
    else:
        return pd.dataframe
        

def find_load_weight_irregularities(opsportal_df, num_days_ago):
    opsportal_df['Day'] = opsportal_df['Timestamp'].dt.day_name()
    
    # Remove gantry runs
    opsportal_df = opsportal_df[opsportal_df['Run'].str.contains('Gantry',case=False,na=False) == False]
    runs = opsportal_df['Run'].unique()
    
    excess_load_list =[]
    week = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    for i in range(len(runs)):
        for day in week:
            selected_run_day   = opsportal_df[(opsportal_df['Run'] == runs[i]) & (opsportal_df['Day'] == day)]
            selected_run_day   = selected_run_day[selected_run_day['Weight'] != 0]
            selected_run_day   = selected_run_day[selected_run_day['Timestamp'] > pd.Timestamp.now().normalize() - pd.Timedelta(days=30)]
            median_load_weight = selected_run_day['Weight'].median(skipna=True)
            
            # Find load weights where more than 500 kg above average
            excess_load_weight = selected_run_day[(selected_run_day['Weight'] >= (median_load_weight+1000)) & (selected_run_day['Timestamp'] > pd.Timestamp.now().normalize() - pd.Timedelta(days=num_days_ago))].copy().reset_index()
            
            if not excess_load_weight.empty:
                for j in range(len(excess_load_weight)):
                    load_weight = excess_load_weight.loc[j,'Weight']
                    excess_load_weight.loc[j,'Problem'] = f"High load weight detected: {load_weight - median_load_weight} kg above median on {day}, {runs[i]}"
                
                excess_load_weight.loc[:,'Median Load Weight'] = median_load_weight
            
            excess_load_list.append(excess_load_weight)
    
    if len (excess_load_list) > 0:
        excess_load_weight_df = pd.concat(excess_load_list)
        return excess_load_weight_df.drop(columns=['Product','Avg Bin Weight','Total Bins','Card Bins','index'])
    else:
        return pd.dataframe