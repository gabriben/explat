import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_current_variables(data):
    fig, ax = plt.subplots(figsize=(10, 10))
    sns.pairplot(data, diag_kind='kde')
    st.pyplot(fig)

    st.subheader("Correlation Heatmap")
    numeric_data = data.select_dtypes(include=[np.number])
    if not numeric_data.empty:
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(numeric_data.corr(), annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)
    else:
        st.write("No numeric data available for correlation heatmap.")

def plot_main_effects(results, factors):
    fig, axes = plt.subplots(1, len(factors), figsize=(5*len(factors), 4))
    for i, factor in enumerate(factors):
        if len(factors) > 1:
            ax = axes[i]
        else:
            ax = axes
        ax.scatter(results[factor], results['rating'])
        ax.set_xlabel(factor)
        ax.set_ylabel('rating')
        ax.set_title(f"Main Effect of {factor}")
    st.pyplot(fig)