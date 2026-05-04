import streamlit as st

from netflix.utils.constants import STYLE_PATH
from netflix.utils.helpers import read_css


def success_profile():
    read_css(STYLE_PATH / "dashboard.css")

    st.title("What does a successful show look like?")

    st.write(
        "This page will compare Netflix shows by hype and longevity."
    )


if __name__ == "__main__":
    success_profile()