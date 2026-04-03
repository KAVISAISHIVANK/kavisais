import streamlit as st
import pandas as pd

st.title("📊 Swing Trading Dashboard")

# Load signals
try:
    df = pd.read_csv("signals.csv")
    
    st.subheader("📈 Latest Signals")
    st.dataframe(df.tail(10))

except:
    st.write("No signals yet")

# Portfolio placeholder
st.subheader("💼 Portfolio (coming soon)")
