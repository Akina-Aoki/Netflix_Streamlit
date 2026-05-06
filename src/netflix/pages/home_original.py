# ------------------------------------------------------------
# home.py
# Syfte: Appens startsida med logga, KPI-kort och beskrivning
# ------------------------------------------------------------
import pandas as pd
import streamlit as st
from netflix.utils.helpers import get_global_df, get_country_df
from netflix.utils.constants import IMAGE_PATH

# --- Läser in data ---
df_global = get_global_df()
df_country = get_country_df()


# slå ihop dataframes för att få fran unika totalt unika titlar
df_combined = pd.concat(
    [df_global[["category", "show_title"]], df_country[["category", "show_title"]]]
)

# Beräkningar

total_films = df_combined[df_combined["category"] == "Movie"]["show_title"].nunique()
total_series = df_combined[df_combined["category"] == "Serie"]["show_title"].nunique()
total_hours = df_global["weekly_hours_viewed"].sum()
total_countries = df_country["country_name"].nunique()
weeks_tracked = df_global["week"].nunique()


st.image(str(IMAGE_PATH / "Logga_Streamly.png"), width=200)
st.caption("Global Netflix viewing statistics")
st.divider()


# KPI-KORT
col1, col2, col3, col4, col5, _ = st.columns([1, 1, 1, 1, 1, 3], gap="small")

with col1:
    st.metric(label="Total Movies", value=f"{total_films:,}")

with col2:
    st.metric(label="Total Series", value=f"{total_series:,}")

with col3:
    st.metric(label="Countries", value=f"{total_countries:,}")

with col4:
    st.metric(label="Weeks tracked", value=f"{weeks_tracked:,}")

with col5:
    st.metric(label="Total hours viewed", value=f"{total_hours / 1_000_000_000:.1f}B")


# Om appen
st.divider()
st.subheader("About this app")
st.write(
    "Streamly visualizes Netflix global viewing data across weekly and "
    "all-time datasets. Use the sidebar to navigate between the dashboard, "
    "trend analysis, country breakdowns, and raw data explorer."
)
