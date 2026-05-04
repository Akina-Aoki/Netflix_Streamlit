import streamlit as st
from netflix.utils.helpers import read_textfile, read_css
from netflix.utils.constants import MARKDOWN_PATH, STYLE_PATH


def dashboard_layout():
    st.title("📊 Netflix Dashboard")

    st.markdown(
        "Explore how shows perform globally using weekly Top 10 data."
    )

    st.info("🚧 Dashboard under construction — charts coming next")

    # Load CSS (optional)
    read_css(STYLE_PATH / "dashboard.css")


if __name__ == "__main__":
    dashboard_layout()