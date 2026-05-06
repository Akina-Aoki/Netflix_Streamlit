import streamlit as st


def render_labeled_selectbox(
    label: str,
    options: list,
    index: int = 0,
    key: str | None = None,
):
    """Render a Streamly-styled label and collapsed Streamlit selectbox."""
    st.markdown(
        f'<div class="streamly-filter-label">{label}</div>',
        unsafe_allow_html=True,
    )
    return st.selectbox(
        label,
        options,
        index=index,
        key=key,
        label_visibility="collapsed",
    )

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