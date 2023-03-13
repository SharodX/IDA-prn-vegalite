# -*- coding: utf-8 -*-

import os
import sys
import streamlit as st
import pandas as pd

import altair as alt
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

#%% function definitions
def get_file_paths(path, extension = ".prn"):
    valid_paths = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                 valid_paths.append(os.path.join(root, file))
    return valid_paths

def merge_prn(paths):
    dfs = []
    for value, path in enumerate(paths):
        # DELETE #-SIGN IN TEXT FILE AND PREPARE STRING FOR READING IN DATAFRAME
        with open(path,'r') as file:
            data = file.read()
        data = data.replace("#", "")
        data = StringIO(data)
        #READ IN DATAFRAME, DROP USELESS COLUMN
        df = pd.read_csv(data, delim_whitespace = True)
        if value == 0:
            df = df.drop("order", axis = 1)
        else:
            df = df.drop(["order", "time"], axis = 1)
        dfs.append(df)
    df_out = pd.concat(dfs, axis = 1)
    return df_out

#%% df import
path = r"C:\Users\villu\Documents\ida_prns_python"

valid_paths = get_file_paths(path)
merged_prn = merge_prn(valid_paths)
df = merged_prn.loc[:,~merged_prn.columns.duplicated()]

with st.sidebar:
    active_series = st.multiselect(label = "active_time_series", options = df.columns)


#%% altair charts


brush = alt.selection(type='interval', encodings=['x'])

base =  alt.Chart(df).mark_line().encode(
        x = 'time:T',
        y = 'tair:Q').properties(
        width = 600,
        height = 200)

charts = []
        
for series in active_series:
    upper = base.encode(
        alt.Y(f'{series}:Q', scale=alt.Scale(domain=brush))
    ).transform_filter(brush)
    line = alt.Chart().mark_rule(color='firebrick').encode(
        y=f'mean({series}):Q',
        size=alt.SizeValue(3)
    ).transform_filter(
        brush
    )
    charts.append(alt.layer(upper, line, data = df))

lower = base.properties(
    height=60
).add_selection(brush)

n = alt.vconcat(*charts, lower)
n
