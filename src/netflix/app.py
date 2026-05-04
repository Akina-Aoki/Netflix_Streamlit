
# --- run cd: streamlit run src/netflix/app.py ---
import streamlit as st

st.set_page_config(page_title="Netflix data ends with the Russian invasion of Ukraine", page_icon="🎬", layout="wide")

pages = [
    st.Page("pages/dashboard.py", title="Dashboard"),
]

pg = st.navigation(pages)
pg.run()