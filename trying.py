import streamlit as st
import pandas as pd

numVar = 2

numVar = st.sidebar.slider('number of variables', min_value=1, value = 1)
numExp = st.sidebar.slider('number of experiments', min_value=1, value = 1)

cols = st.columns(numVar + 1)

for i, c in enumerate(cols):
    if i == 0:
        c.write("exp mum")
        for e in range(numExp):
           c.write(str(e))
    else:
        c.write("variable " + str(i))
        for e in range(numExp):
            c.text_input("", key = str(e) + "_" + str(i))

