import pandas as pd
import streamlit as st

df = pd.DataFrame(
    [
        {"command": "arabica", "rating": 4, "is_widget": True},
        {"command": "hip", "rating": 5, "is_widget": False},
        {"command": "arabica", "rating": 3, "is_widget": True},
    ]
)
edited_df = st.data_editor(
    df,
    column_config={
        "command": "bean",
        "rating": st.column_config.NumberColumn(
            "Your rating",
            help="How much do you like this command (1-5)?",
            min_value=1,
            max_value=5,
            step=1,
            format="%d ⭐",
        ),
        "is_widget": "Widget ?",
    },
    disabled=["command", "is_widget"],
    hide_index=True,
)

favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
st.markdown(f"Your favorite command is **{favorite_command}** 🎈")