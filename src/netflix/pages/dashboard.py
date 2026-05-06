import streamlit as st
from netflix.components.visuals import russia_line_chart
from netflix.utils.helpers import show_banner
from netflix.utils.helpers import get_russia_kpi, get_country_df



show_banner()

st.divider()


st.subheader("A data anomaly that reveals a geopolitical event.")

st.markdown("""
    <p class='disclaimer'>
        This dashboard explores Netflix viewing data up to February 2022 only visible after exploratory data analysis (EDA). <br>
        The chart line and metrics below show what Netflix looked like in Russia until the events.
    </p>
""", unsafe_allow_html=True)

st.divider()


st.markdown(
    "<h1 style='text-align: center; font-family: Segoe UI, sans-serif;font-weight: bold;color= #F5F0E8'>Russia data against rest of the world's data since 2021</h1>",
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    russia_line_chart()


# --- Trying to separate this part from the onlione chart ---
st.divider()

# Values in the center of the cards
st.markdown("""
    <style>
        [data-testid="stMetric"] {
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        [data-testid="stMetricValue"] {
            justify-content: center;
            text-align: center;
        }
        [data-testid="stMetricLabel"] {
            text-align: center;
            width: 100%;
        }
        [data-testid="stMetricDelta"] {
            justify-content: center;
        }
    </style>
""", unsafe_allow_html=True)


# Getting all the calculated numbers
kpi = get_russia_kpi()  
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Unique shows at the start (Jul 2021)", value=kpi["start_2021"])

with col2:
    st.metric(label="Unique shows end 2021", value=kpi["end_2021"],
        delta=f"{kpi['diff_2021']:+d} ({kpi['pct_2021']:+.1f}%)")

with col3:
    st.metric(label="Peak in Jan 2022", value=kpi["start_2022"])

with col4:
    st.metric(label="Last data from Feb 2022", value=kpi["end_2022"],
        delta=f"{kpi['both_years']:+.0f} ({kpi['both_years_pct']:+.1f}%) vs Jul 2021")

