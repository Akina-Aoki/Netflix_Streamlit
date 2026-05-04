import streamlit as st

def filters_ui(df):

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        country = st.selectbox(
            "Country",
            sorted(df["country_name"].unique())
        )

    with col2:
        year = st.selectbox(
            "Year",
            sorted(df["year"].unique())
        )

    with col3:
        month = st.selectbox(
            "Month",
            df["month_name"].unique()
        )

    with col4:
        category = st.selectbox(
            "Category",
            df["category"].unique()
        )

    return country, year, month, category