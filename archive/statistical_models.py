import itertools
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats


def design_experiment(factors, responses):
    """
    Create a simple 2^k factorial design.
    
    :param factors: List of dictionaries, each containing 'name', 'low', and 'high' values
    :param responses: List of response variable names
    :return: List of dictionaries representing the experimental runs
    """
    n_factors = len(factors)
    n_runs = 2**n_factors
    
    # Create design matrix
    design_matrix = np.array(list(itertools.product([-1, 1], repeat=n_factors)))
    
    experiment_design = []
    for run in range(n_runs):
        run_factors = []
        for i, factor in enumerate(factors):
            value = factor['low'] if design_matrix[run, i] == -1 else factor['high']
            run_factors.append({'name': factor['name'], 'value': value})
        
        run_responses = [{'name': resp, 'value': None} for resp in responses]
        
        experiment_design.append({
            'run': run + 1,
            'factors': run_factors,
            'responses': run_responses
        })
    
    return experiment_design

def analyze_results(design, results):
    """
    Perform basic analysis on the experimental results.
    
    :param design: The experimental design (output from design_experiment)
    :param results: List of dictionaries with 'run', 'response', and 'value' keys
    :return: Dictionary containing summary statistics, ANOVA results, and effects
    """
    # Prepare data
    df = pd.DataFrame(results)
    pivot_df = df.pivot(index='run', columns='response', values='value')
    
    # Summary statistics
    summary_stats = pivot_df.describe()
    
    # Prepare design matrix
    X = np.array([[-1 if f['value'] == factors[i]['low'] else 1 
                   for i, f in enumerate(run['factors'])] 
                  for run in design])
    
    # ANOVA and effects calculation
    anova_results = {}
    effects = {'factors': [], 'values': []}
    
    for response in pivot_df.columns:
        y = pivot_df[response].values
        
        # Main effects
        effects_values = np.mean(y[X == 1], axis=0) - np.mean(y[X == -1], axis=0)
        
        for i, factor in enumerate(factors):
            effects['factors'].append(factor['name'])
            effects['values'].append(effects_values[i])
        
        # ANOVA
        model = sm.OLS(y, X).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        anova_results[response] = anova_table
    
    return {
        'summary_stats': summary_stats,
        'anova': anova_results,
        'effects': effects
    }
