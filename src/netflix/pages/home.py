import streamlit as st
from netflix.utils.helpers import read_textfile
from netflix.utils.constants import MARKDOWN_PATH


def home():
    st.title("🎬 Netflix Analytics")

    st.markdown(
        "This dashboard explores Netflix insights across countries."
    )

    st.markdown(read_textfile(MARKDOWN_PATH / "introduction.md"))


if __name__ == "__main__":
    home()