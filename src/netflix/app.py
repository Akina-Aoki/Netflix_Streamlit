# app.py
import streamlit as st

st.set_page_config(
    page_title="Netflix Streamlit Dashboard",
    page_icon="🎬",
    layout="wide",
)

pages = [
    st.Page("pages/home.py", title="Home", icon="🏠"),
    st.Page("pages/success_profile.py", title="Success Profile"),
    st.Page("pages/dashboard.py", title="Dashboard", icon="📊"),
    st.Page("pages/raw_data.py", title="Raw Data", icon="🧾"),
]

pg = st.navigation(pages)
pg.run()