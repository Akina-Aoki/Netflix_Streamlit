import streamlit as st
from netflix.components.visuals import russia_line_chart

st.markdown(
    "<h1 style='text-align: center'>Russia data against rest of the world's data since 2021</h1>",
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    russia_line_chart()