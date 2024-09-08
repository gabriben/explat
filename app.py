import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go

# Assuming you have these functions implemented
from statistical_models import design_experiment, analyze_results

def main():
    st.title("Modern Experimental Design SaaS")

    # Sidebar for navigation
    page = st.sidebar.selectbox("Choose a page", ["Design Experiment", "Analyze Results"])

    if page == "Design Experiment":
        design_experiment_page()
    elif page == "Analyze Results":
        analyze_results_page()

def design_experiment_page():
    st.header("Design Your Experiment")

    # Input for experiment name
    experiment_name = st.text_input("Experiment Name")

    # Input for factors
    num_factors = st.number_input("Number of Factors", min_value=1, max_value=10, value=2)
    factors = []
    for i in range(num_factors):
        factor = st.text_input(f"Factor {i+1} Name")
        low = st.number_input(f"Factor {i+1} Low Level")
        high = st.number_input(f"Factor {i+1} High Level")
        factors.append({"name": factor, "low": low, "high": high})

    # Input for responses
    num_responses = st.number_input("Number of Responses", min_value=1, max_value=5, value=1)
    responses = [st.text_input(f"Response {i+1} Name") for i in range(num_responses)]

    if st.button("Generate Experiment Design"):
        design = design_experiment(factors, responses)
        st.session_state['current_design'] = design
        st.dataframe(pd.DataFrame(design))
        st.success("Experiment design generated successfully!")

def analyze_results_page():
    st.header("Analyze Experiment Results")

    if 'current_design' not in st.session_state:
        st.warning("Please design an experiment first.")
        return

    design = st.session_state['current_design']
    
    # Allow user to input results
    results = []
    for i, run in enumerate(design):
        st.subheader(f"Run {i+1}")
        for factor in run['factors']:
            st.write(f"{factor['name']}: {factor['value']}")
        for response in run['responses']:
            value = st.number_input(f"{response} Value", key=f"run_{i}_{response}")
            results.append({"run": i, "response": response, "value": value})

    if st.button("Analyze Results"):
        analysis = analyze_results(design, results)
        display_analysis(analysis)

def display_analysis(analysis):
    st.subheader("Analysis Results")
    
    # Display summary statistics
    st.write("Summary Statistics:")
    st.dataframe(pd.DataFrame(analysis['summary_stats']))

    # Display ANOVA results
    st.write("ANOVA Results:")
    st.dataframe(pd.DataFrame(analysis['anova']))

    # Display effects plot
    fig = go.Figure(data=[go.Bar(x=analysis['effects']['factors'], y=analysis['effects']['values'])])
    fig.update_layout(title="Factor Effects", xaxis_title="Factors", yaxis_title="Effect Size")
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
