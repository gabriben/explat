import numpy as np
from statsmodels.formula.api import ols

def run_experiment(design_matrix):
    results = design_matrix.copy()
    results['rating'] = np.random.rand(len(results)) * 5
    return results

def analyze_results(results, factors):
    model = ols(f"rating ~ {' + '.join(factors)}", data=results).fit()
    return model.summary()