import streamlit as st
import pandas as pd
import numpy as np

def initialize_session_state():
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame({
            'bean': ["arabica", "hip", "arabica"],
            'rating': [4, 5, 3],
            'pre-ground': [True, False, True]
        })
    if 'added_columns' not in st.session_state:
        st.session_state.added_columns = []
    if 'column_ranges' not in st.session_state:
        st.session_state.column_ranges = {}

def add_column(df, col_name, col_type):
    if col_type == 'text':
        df[col_name] = pd.Series(dtype='object')
    elif col_type == 'number':
        df[col_name] = pd.Series(dtype='float64')
    elif col_type == 'boolean':
        df[col_name] = pd.Series(dtype='bool')
    return df

def update_column_range(col, col_type):
    if np.issubdtype(col_type, np.number):
        min_val = st.number_input(f"Min {col}", value=float(st.session_state.data[col].min()))
        max_val = st.number_input(f"Max {col}", value=float(st.session_state.data[col].max()))
    elif col_type == 'bool':
        min_val, max_val = False, True
        st.write(f"Boolean column: range is False to True")
    else:  # categorical
        unique_values = st.session_state.data[col].unique().tolist()
        min_val = st.selectbox(f"Min {col}", unique_values, index=0)
        max_val = st.selectbox(f"Max {col}", unique_values, index=len(unique_values)-1)
    return min_val, max_val

def calculate_max_runs(factors):
    max_runs = 1
    for factor in factors:
        if factor in st.session_state.column_ranges:
            min_val, max_val = st.session_state.column_ranges[factor]
            if isinstance(min_val, bool):
                max_runs *= 2
            elif isinstance(min_val, (int, float)):
                max_runs *= 10
            else:
                max_runs *= len(st.session_state.data[factor].unique())
    return max(2, max_runs)

# Explicitly export the functions
__all__ = ['initialize_session_state', 'add_column', 'update_column_range', 'calculate_max_runs']