import streamlit as st
from netflix.components.visualizations import russia_line_chart, df

def dashboard_layout():
    st.markdown("<h1 style='text-align: center'>Russia data against rest of the world's data since 2021</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        russia_line_chart()

# --- Change of plans: better with Maarcus' version ---
    #st.markdown("# Search for a title")
    #search = st.text_input("Type a film or serie title")


    #if search:
        results = df["show_title"].str.contains(search, case=False, na=False)

    #    if results.empty:
    #        st.warning("No result found")
    #    else: 
    #        st.dataframe(results[["show_title", "country_name", "week", "weekly_rank", "cumulative_weeks_in_top_10"]].sort_values("week", ascending=False))


if __name__ == "__main__":
    dashboard_layout()