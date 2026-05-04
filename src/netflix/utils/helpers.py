import pandas as pd
import streamlit as st
from netflix.utils.constants import DATA_PATH


@st.cache_data  # to avoid to reload all the rows each time
def get_df()->pd.DataFrame:
        df = pd.read_csv(DATA_PATH / "global_weekly_st.csv")
        df["week"] = pd.to_datetime(df["week"], dayfirst=True)
        return df