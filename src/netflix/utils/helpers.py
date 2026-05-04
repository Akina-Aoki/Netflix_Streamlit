import pandas as pd
import streamlit as st
from netflix.utils.constants import DATA_PATH


def read_textfile(path):
    with open(path, encoding="utf-8") as file:
        return file.read()


def read_css(path):
    css = read_textfile(path)
    st.write(f"<style>{css}</style>", unsafe_allow_html=True)


@st.cache_data
def get_global_weekly_df():
    df = pd.read_excel(DATA_PATH / "global_weekly.xlsx")
    df["week"] = pd.to_datetime(df["week"])
    return df


@st.cache_data
def get_global_alltime_df():
    df = pd.read_excel(DATA_PATH / "global_alltime.xlsx")
    return df

@st.cache_data
def get_global_weekly_df():
    df = pd.read_excel(DATA_PATH / "global_weekly.xlsx")

    df["week"] = pd.to_datetime(df["week"])
    df["year"] = df["week"].dt.year
    df["month"] = df["week"].dt.month
    df["month_name"] = df["week"].dt.strftime("%B")

    return df