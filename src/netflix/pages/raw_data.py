import streamlit as st
from netflix.utils.helpers import get_global_weekly_df


def raw_data():
    st.title("📄 Raw Data")

    df = get_global_weekly_df()
    st.dataframe(df)


if __name__ == "__main__":
    raw_data()