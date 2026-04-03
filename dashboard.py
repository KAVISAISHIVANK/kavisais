import streamlit as st
import pandas as pd

st.title("📊 Swing Trading Dashboard")

try:
    df = pd.read_csv("signals.csv")
    st.dataframe(df)
except:
    st.write("No signals yet")
