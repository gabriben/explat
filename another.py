import streamlit as st
import pandas as pd

d = pd.DataFrame({
    'bean': ["arabica", "hip", "arabica"],
    'rating': [4, 5, 3],
    'pre-ground': [True, False, True]
})


edited_df = st.data_editor(
    d,
    column_config={
        "rating": st.column_config.NumberColumn(
            "Your rating",
            help="How much do you like this command (1-5)?",
            min_value=1,
            max_value=5,
            step=1,
            format="%d ⭐",
        )
    },
    disabled=["command", "is_widget"],
    hide_index=True,
    num_rows='dynamic'
)

# favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
# st.markdown(f"Your favorite command is **{favorite_command}** 🎈")
