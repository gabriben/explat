import numpy as np
from pyDOE3 import ff2n, lhs
from scipy.linalg import det
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
import streamlit as st


# Function to create D-optimal design
def create_d_optimal_design(factors, num_runs=15):
    # Step 1: Define factors
    binary_factors = []
    continuous_factors = []
    categorical_factors = []
    categorical_columns = []
    
    for factor in factors:
        if factor in st.session_state.column_ranges:
            min_val, max_val = st.session_state.column_ranges[factor]
            if isinstance(min_val, bool):
                binary_factors.append(ff2n(1))
            elif isinstance(min_val, (int, float)):
                continuous_factors.append(lhs(1, samples=10) * (max_val - min_val) + min_val)
            else:
                unique_values = st.session_state.data[factor].unique()
                categorical_factors.append(np.array([[v] for v in unique_values]))
                categorical_columns.append(factor)
    
    # Step 2: Create a candidate set
    candidates = []
    for b in (binary_factors if binary_factors else [[]]):
        for c in (continuous_factors if continuous_factors else [[]]):
            for cat in (categorical_factors if categorical_factors else [[]]):
                candidates.append(np.hstack([b, c, cat]))
    
    candidates = np.array(candidates)
    
    if candidates.size == 0:
        st.warning("No valid candidates could be generated. Please check your factor ranges.")
        st.warning(factors)
        st.warning(st.session_state.column_ranges)
        
        return pd.DataFrame(columns=factors)

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
    
    # Convert the design back to original factor space
    final_design = pd.DataFrame(best_design, columns=factors)
    
    # Handle categorical variables
    cat_start = len(binary_factors) + len(continuous_factors)
    for i, factor in enumerate(categorical_columns):
        cat_values = st.session_state.data[factor].unique()
        cat_indices = best_design[:, cat_start + i].astype(int)
        final_design[factor] = cat_values[cat_indices]
    
    return final_design

# Explicitly export the functions
__all__ = ['create_d_optimal_design']