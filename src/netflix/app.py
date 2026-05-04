
# --- run cd: streamlit run src/netflix/app.py ---
import streamlit as st

st.set_page_config(page_title="Netflix data ends with the Russian invasion of Ukraine", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebarNav"] a {
            font-size: 20px !important;
            padding: 10px !important;
        }
    </style>
""", unsafe_allow_html=True)

pages = [
    st.Page("pages/dashboard.py", title="Dashboard"),
    st.Page("pages/search.py", title="Search"),
]

pg = st.navigation(pages)
pg.run()