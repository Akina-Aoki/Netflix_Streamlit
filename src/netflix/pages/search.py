# --- Needed to crate a separate page for search ---

import streamlit as st
from netflix.components.visualizations import df

def search_field():
    st.markdown("# Search a title")
    
    search = st.text_input("Type a film or a serie title")

    if search:
        results = df[df["show_title"].str.contains(search, case=False, na=False)]
        if results.empty:
            st.warning("No result found")
        else:
            st.dataframe(results[["show_title", "country_name", "week", "weekly_rank"]].sort_values("week", ascending=False))

if __name__ == "__main__":
    search_field()