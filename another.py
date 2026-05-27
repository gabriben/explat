import streamlit as st
import pandas as pd
import numpy as np
from pyDOE3 import ff2n, lhs
from scipy.linalg import det
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import OneHotEncoder
from typing import Dict, Tuple, Union

# Initialize session state for added columns and column ranges
if 'added_columns' not in st.session_state:
    st.session_state.added_columns = []

if 'column_ranges' not in st.session_state:
    st.session_state.column_ranges = {}

# Initial data
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'bean': ["arabica", "hip", "arabica"],
        'rating': [4, 5, 3],
        'pre-ground': [True, False, True]
    })

# Function to add a new column
def add_column(df, col_name, col_type):
    if col_type == 'text':
        df[col_name] = pd.Series(dtype='object')
    elif col_type == 'number':
        df[col_name] = pd.Series(dtype='float64')
    elif col_type == 'boolean':
        df[col_name] = pd.Series(dtype='bool')
    return df

# Function to add or update column range
def update_column_range(column: str, min_value: Union[float, str], max_value: Union[float, str]):
    st.session_state.column_ranges[column] = (min_value, max_value)

# Sidebar for adding new columns
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
        if col != 'rating':  # Exclude rating column
            st.subheader(f"{col} Range")
            col_type = st.session_state.data[col].dtype
            
            if np.issubdtype(col_type, np.number):
                col1, col2 = st.columns(2)
                with col1:
                    min_val = st.number_input(f"Min {col}", value=float(st.session_state.data[col].min()))
                with col2:
                    max_val = st.number_input(f"Max {col}", value=float(st.session_state.data[col].max()))
            elif col_type == 'bool':
                min_val, max_val = False, True
                st.write(f"Boolean column: range is False to True")
            else:  # categorical
                unique_values = st.session_state.data[col].unique().tolist()
                min_val = st.selectbox(f"Min {col}", unique_values, index=0)
                max_val = st.selectbox(f"Max {col}", unique_values, index=len(unique_values)-1)
            
            if st.button(f"Set {col} Range"):
                update_column_range(col, min_val, max_val)

    st.write("Current Ranges:")
    st.write(st.session_state.column_ranges)

# Split the dataframe
main_df = st.session_state.data.drop(columns=['rating'])
rating_df = st.session_state.data[['rating']]

# Dynamic column configuration
main_column_config = {}
rating_column_config = {
    "rating": st.column_config.NumberColumn(
        "Your rating",
        help="How much do you like this (1-5)?",
        min_value=1,
        max_value=5,
        step=1,
        format="%d ⭐",
    )
}

# Add configuration for all columns in main_df
for col in main_df.columns:
    if main_df[col].dtype == 'object':
        main_column_config[col] = st.column_config.TextColumn(col)
    elif main_df[col].dtype in ['int64', 'float64']:
        main_column_config[col] = st.column_config.NumberColumn(col)
    elif main_df[col].dtype == 'bool':
        main_column_config[col] = st.column_config.CheckboxColumn(col)

# Create two columns for layout with adjusted widths
col1, col2 = st.columns([4, 1])  # Adjust the ratio here

# Display the main editable dataframe
with col1:
    edited_main_df = st.data_editor(
        main_df,
        column_config=main_column_config,
        hide_index=True,
        num_rows='dynamic'
    )

# Ensure data types are preserved in edited_main_df
for col in main_df.columns:
    edited_main_df[col] = edited_main_df[col].astype(main_df[col].dtype)

# Ensure rating_df has the same number of rows as edited_main_df
num_rows = len(edited_main_df)
if len(rating_df) < num_rows:
    rating_df = rating_df.reindex(range(num_rows), fill_value=np.nan)
elif len(rating_df) > num_rows:
    rating_df = rating_df.iloc[:num_rows]

# Display the rating dataframe
with col2:
    edited_rating_df = st.data_editor(
        rating_df,
        column_config=rating_column_config,
        hide_index=True,
        num_rows=num_rows
    )

# Combine the edited dataframes and update the session state
st.session_state.data = pd.concat([edited_main_df, edited_rating_df], axis=1)

# Function to create D-optimal design
def create_d_optimal_design(factors, num_runs=15):
    # Step 1: Define factors
    binary_factors = []
    continuous_factors = []
    categorical_factors = []
    
    for factor, (min_val, max_val) in st.session_state.column_ranges.items():
        if factor in factors:
            if isinstance(min_val, bool):
                binary_factors.append(ff2n(1))
            elif isinstance(min_val, (int, float)):
                continuous_factors.append(lhs(1, samples=10) * (max_val - min_val) + min_val)
            else:
                unique_values = st.session_state.data[factor].unique()
                categorical_factors.append(np.array([[v] for v in unique_values]))
    
    # Step 2: Create a candidate set
    candidates = []
    for b in (binary_factors[0] if binary_factors else [[]]):
        for c in (continuous_factors[0] if continuous_factors else [[]]):
            for cat in (categorical_factors[0] if categorical_factors else [[]]):
                candidates.append(np.hstack([b, c, cat]))
    
    candidates = np.array(candidates)
    
    # Adjust num_runs if it exceeds the number of candidates
    num_runs = min(num_runs, len(candidates))

    # Step 3: Define D-optimality function
    def d_optimality(X):
        XtX = X.T @ X
        return det(XtX)
    
    # Step 4: Select an initial random design
    np.random.seed(42)
    initial_design_indices = np.random.choice(len(candidates), num_runs, replace=False)
    design = candidates[initial_design_indices]
    
    # Step 5: Create a model matrix for linear regression
    def model_matrix(design):
        return np.hstack((np.ones((design.shape[0], 1)), design))
    
    # Step 6: Iteratively optimize the design
    best_design = design
    best_optimality = d_optimality(model_matrix(best_design))
    
    for _ in range(100):
        for i in range(num_runs):
            candidate_index = np.random.randint(len(candidates))
            new_design = np.copy(best_design)
            new_design[i] = candidates[candidate_index]
            new_optimality = d_optimality(model_matrix(new_design))
            if new_optimality > best_optimality:
                best_design = new_design
                best_optimality = new_optimality
    
    return pd.DataFrame(best_design, columns=factors)

# After the main data editor and before the DOE section, add this:

st.header("Current Variables Overview")

# Create a pair plot of the current variables
fig, ax = plt.subplots(figsize=(10, 10))
sns.pairplot(st.session_state.data, diag_kind='kde')
st.pyplot(fig)

# If you want to show correlation heatmap as well
st.subheader("Correlation Heatmap")
numeric_data = st.session_state.data.select_dtypes(include=[np.number])
if not numeric_data.empty:
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(numeric_data.corr(), annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)
else:
    st.write("No numeric data available for correlation heatmap.")

# DOE section
st.header("Design of Experiments")

# Get all factors except 'rating'
factors = [col for col in st.session_state.data.columns if col != 'rating']

# Calculate the maximum number of possible runs
max_runs = 1
for factor in factors:
    if factor in st.session_state.column_ranges:
        min_val, max_val = st.session_state.column_ranges[factor]
        if isinstance(min_val, bool):
            max_runs *= 2
        elif isinstance(min_val, (int, float)):
            max_runs *= 10  # We're using 10 samples for continuous factors
        else:
            max_runs *= len(st.session_state.data[factor].unique())

# Ensure max_runs is at least 2
max_runs = max(2, max_runs)

# Create D-optimal design
num_runs = st.number_input("Number of runs", min_value=2, max_value=max_runs, value=min(15, max_runs))

if st.button("Generate D-Optimal Design"):
    design_matrix = create_d_optimal_design(factors, num_runs)
    
    st.subheader("D-Optimal Design Matrix")
    st.dataframe(design_matrix)

    # Run experiment button
    if st.button("Run Experiment"):
        # Assuming 'rating' is the response variable
        response_variable = 'rating'
        
        # Simulate experiment results (replace this with actual experiment results if available)
        results = design_matrix.copy()
        results[response_variable] = np.random.rand(len(results)) * 5  # Random ratings between 0 and 5
        
        st.subheader("Experiment Results")
        st.dataframe(results)

        # Analyze results
        model = ols(f"{response_variable} ~ {' + '.join(factors)}", data=results).fit()
        
        st.subheader("Analysis Results")
        st.write(model.summary())

        # Plot main effects
        st.subheader("Main Effects Plot")
        fig, axes = plt.subplots(1, len(factors), figsize=(5*len(factors), 4))
        for i, factor in enumerate(factors):
            if len(factors) > 1:
                ax = axes[i]
            else:
                ax = axes
            ax.scatter(results[factor], results[response_variable])
            ax.set_xlabel(factor)
            ax.set_ylabel(response_variable)
            ax.set_title(f"Main Effect of {factor}")
        st.pyplot(fig)
