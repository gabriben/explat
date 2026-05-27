import streamlit as st
import pandas as pd
import numpy as np
from data_management import initialize_session_state, add_column, update_column_range, calculate_max_runs
from doe import create_d_optimal_design
from visualization import plot_current_variables, plot_main_effects
from utils import run_experiment, analyze_results

def main():
    initialize_session_state()

    # Sidebar for adding new columns and specifying ranges
    with st.sidebar:
        st.header("Add New Column")
        new_col_name = st.text_input("Column Name")
        new_col_type = st.selectbox("Column Type", ['text', 'number', 'boolean'])
        if st.button("Add Column"):
            if new_col_name and new_col_name not in st.session_state.data.columns:
                st.session_state.data = add_column(st.session_state.data, new_col_name, new_col_type)
                st.session_state.added_columns.append((new_col_name, new_col_type))
                st.success(f"Added column: {new_col_name}")
            else:
                st.error("Invalid column name or column already exists")

        st.header("Column Range Specification")
        for col in st.session_state.data.columns:
            if col != 'rating':
                st.subheader(f"{col} Range")
                col_type = st.session_state.data[col].dtype
                min_val, max_val = update_column_range(col, col_type)
                if st.button(f"Set {col} Range"):
                    st.session_state.column_ranges[col] = (min_val, max_val)

        st.write("Current Ranges:")
        st.write(st.session_state.column_ranges)

    # Main app layout
    st.title("Experimental Design App")

    # Display the main editable dataframe
    st.header("Data Editor")
    edited_df = st.data_editor(st.session_state.data, num_rows="dynamic")
    st.session_state.data = edited_df

    # Plot current variables
    # st.header("Current Variables Overview")
    # plot_current_variables(st.session_state.data)

    # DOE section
    st.header("Design of Experiments")
    factors = [col for col in st.session_state.data.columns if col != 'rating']
    max_runs = calculate_max_runs(factors)
    num_runs = st.number_input("Number of runs", min_value=2, max_value=max_runs, value=min(15, max_runs))

    if st.button("Generate D-Optimal Design"):
        design_matrix = create_d_optimal_design(factors, num_runs)
        st.subheader("D-Optimal Design Matrix")
        st.dataframe(design_matrix)

        if st.button("Run Experiment"):
            results = run_experiment(design_matrix)
            st.subheader("Experiment Results")
            st.dataframe(results)

            analysis_results = analyze_results(results, factors)
            st.subheader("Analysis Results")
            st.write(analysis_results)

            st.subheader("Main Effects Plot")
            plot_main_effects(results, factors)

if __name__ == "__main__":
    main()