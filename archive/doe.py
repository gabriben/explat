import numpy as np
from pyDOE3 import ff2n, lhs
from scipy.linalg import det

# Step 1: Define factors
# Two binary factors (can take values 0 and 1)
binary_factors = ff2n(2)  # Full factorial for 2 binary factors

# One continuous factor (use Latin Hypercube Sampling to spread out values)
continuous_factors = lhs(1, samples=10) * (100 - 0) + 0  # Range from 0 to 100

# One categorical factor with 5 levels
categorical_factors = np.array([[1], [2], [3], [4], [5]])

# Step 2: Create a candidate set
# Create a Cartesian product of binary, continuous, and categorical factors
candidates = []
for b in binary_factors:
    for c in continuous_factors:
        for cat in categorical_factors:
            candidates.append(np.hstack([b, c, cat]))

candidates = np.array(candidates)

# Step 3: Define a function to calculate the D-optimal criterion
def d_optimality(X):
    """Calculate the determinant of X'X (information matrix)."""
    XtX = X.T @ X
    return det(XtX)

# Step 4: Select an initial random design
num_runs = 15
np.random.seed(42)  # For reproducibility
initial_design_indices = np.random.choice(len(candidates), num_runs, replace=False)
design = candidates[initial_design_indices]

# Step 5: Create a model matrix for linear regression
def model_matrix(design):
    """Create the design matrix (X) for linear regression (main effects only)."""
    return np.hstack((np.ones((design.shape[0], 1)), design))  # Add intercept

# Step 6: Iteratively optimize the design by swapping points
best_design = design
best_optimality = d_optimality(model_matrix(best_design))

for iteration in range(100):  # Limit the number of iterations
    for i in range(num_runs):
        # Try replacing one row in the design with a random candidate
        candidate_index = np.random.randint(len(candidates))
        new_design = np.copy(best_design)
        new_design[i] = candidates[candidate_index]
        
        # Calculate D-optimality for the new design
        new_optimality = d_optimality(model_matrix(new_design))
        
        if new_optimality > best_optimality:
            best_design = new_design
            best_optimality = new_optimality

# Output the optimized design
print("Optimized D-optimal design:")
print(best_design)
