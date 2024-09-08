import streamlit as st
import pandas as pd

# Initial data
d = pd.DataFrame({
    'bean': ["arabica", "hip", "arabica"],
    'rating': [4, 5, 3],
    'pre-ground': [True, False, True]
})

# Function to add a new column
def add_column(df, col_name, col_type):
    if col_type == 'text':
        df[col_name] = ''
    elif col_type == 'number':
        df[col_name] = 0
    elif col_type == 'boolean':
        df[col_name] = False
    return df

# Sidebar for adding new columns
with st.sidebar:
    st.header("Add New Column")
    new_col_name = st.text_input("Column Name")
    new_col_type = st.selectbox("Column Type", ['text', 'number', 'boolean'])
    if st.button("Add Column"):
        if new_col_name and new_col_name not in d.columns:
            d = add_column(d, new_col_name, new_col_type)
            st.success(f"Added column: {new_col_name}")
        else:
            st.error("Invalid column name or column already exists")

# Dynamic column configuration
column_config = {
    "rating": st.column_config.NumberColumn(
        "Your rating",
        help="How much do you like this command (1-5)?",
        min_value=1,
        max_value=5,
        step=1,
        format="%d ⭐",
    )
}

# Add configuration for new columns
for col in d.columns:
    if col not in column_config:
        if d[col].dtype == 'object':
            column_config[col] = st.column_config.TextColumn(col)
        elif d[col].dtype in ['int64', 'float64']:
            column_config[col] = st.column_config.NumberColumn(col)
        elif d[col].dtype == 'bool':
            column_config[col] = st.column_config.CheckboxColumn(col)

# Display the editable dataframe
edited_df = st.data_editor(
    d,
    column_config=column_config,
    hide_index=True,
    num_rows='dynamic'
)

# Display the resulting dataframe
st.write("Resulting DataFrame:", edited_df)
