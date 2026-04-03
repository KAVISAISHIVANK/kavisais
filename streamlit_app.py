import streamlit as st
import pandas as pd

st.title("📊 Swing Trading Dashboard")

# Signals
st.subheader("📈 Latest Signals")
try:
    signals = pd.read_csv("signals.csv")
    st.dataframe(signals.tail(10))
except:
    st.write("No signals yet")

# Portfolio
st.subheader("💼 Portfolio")
try:
    portfolio = pd.read_csv("portfolio.csv")
    st.dataframe(portfolio)
except:
    st.write("No portfolio yet")
