import calendar
import pandas as pd
import plotly.express as px
import streamlit as st

from netflix.utils.constants import IMAGE_PATH, STYLES_PATH
from netflix.utils.helpers import get_country_df, get_global_df, get_weekly_df, read_css

PAGE_COLORS = {
    "bg": "#0F0D0B",
    "card": "#1A1612",
    "border": "#2A2118",
    "yellow": "#F7B952",
    "orange": "#E8622A",
    "amber": "#FFB84D",
    "text": "#F5F0E8",
    "muted": "#9E9689",
}

STYLE_PATH = STYLES_PATH


def get_global_weekly_df() -> pd.DataFrame:
    """Compatibility wrapper for older dashboard naming."""
    return get_weekly_df()


@st.cache_data
def load_home_kpis() -> dict:
    """Load and compute KPI values shown at the top of Home."""
    df_global = get_global_df().copy()
    df_country = get_country_df().copy()

    df_combined = pd.concat(
        [df_global[["category", "show_title"]], df_country[["category", "show_title"]]],
        ignore_index=True,
    )

    film_categories = {"Movie", "Movies", "Film", "Films"}
    series_categories = {"Serie", "Series", "TV"}

    total_films = df_combined[df_combined["category"].isin(film_categories)][
        "show_title"
    ].nunique()
    total_series = df_combined[df_combined["category"].isin(series_categories)][
        "show_title"
    ].nunique()

    return {
        "total_films": int(total_films),
        "total_series": int(total_series),
        "total_hours": float(df_global["weekly_hours_viewed"].sum()),
        "total_countries": int(df_country["country_name"].nunique()),
        "weeks_tracked": int(df_global["week"].nunique()),
    }


@st.cache_data
def prepare_home_chart_data() -> pd.DataFrame:
    """Prepare old Netflix analytics section data with normalized categories."""
    df = get_global_weekly_df().copy()

    df["week"] = pd.to_datetime(df["week"], errors="coerce")
    df["weekly_rank"] = pd.to_numeric(df["weekly_rank"], errors="coerce")

    df = df.dropna(subset=["week", "weekly_rank", "show_title", "category", "country_name"])

    df["year"] = df["week"].dt.year
    df["month_num"] = df["week"].dt.month

    month_labels = list(calendar.month_name)[1:]
    df["month_name"] = pd.Categorical(
        df["week"].dt.month_name(), categories=month_labels, ordered=True
    )

    df["score"] = 11 - df["weekly_rank"]
    df = df[df["score"].notna() & (df["score"] > 0)].copy()

    category_map = {
        "Movie": "Films",
        "Movies": "Films",
        "Film": "Films",
        "Films": "Films",
        "Serie": "TV",
        "Series": "TV",
        "TV": "TV",
    }
    df["category"] = df["category"].map(category_map).fillna(df["category"])

    return df


def render_kpi_header() -> None:
    """Render current top Home section: logo, caption, KPIs, about text."""
    kpis = load_home_kpis()

    st.image(str(IMAGE_PATH / "Logga_Streamly.png"), width=200)
    st.caption("Global Netflix viewing statistics")
    st.divider()

    col1, col2, col3, col4, col5, _ = st.columns([1, 1, 1, 1, 1, 3], gap="small")

    with col1:
        st.metric(label="Total Movies", value=f"{kpis['total_films']:,}")
    with col2:
        st.metric(label="Total Series", value=f"{kpis['total_series']:,}")
    with col3:
        st.metric(label="Countries", value=f"{kpis['total_countries']:,}")
    with col4:
        st.metric(label="Weeks tracked", value=f"{kpis['weeks_tracked']:,}")
    with col5:
        st.metric(label="Total hours viewed", value=f"{kpis['total_hours'] / 1_000_000_000:.1f}B")

    st.divider()
    st.subheader("About this app")
    st.write(
        "Streamly visualizes Netflix global viewing data across weekly and "
        "all-time datasets. Use the sidebar to navigate between the dashboard, "
        "trend analysis, country breakdowns, and raw data explorer."
    )


def render_analytics_section() -> None:
    """Render old Netflix analytics dashboard section below Home overview."""
    weekly_df = prepare_home_chart_data()

    st.markdown("## Netflix Analytics")
    st.markdown(
        "Explore the top 10 movies and series across countries. Filter by country, "
        "year, month, and category to understand what performs best over time."
    )
    st.markdown('<p class="disclaimer">Data is based on Netflix weekly Top 10 rankings.</p>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    countries = sorted(weekly_df["country_name"].dropna().unique().tolist())
    years = sorted(weekly_df["year"].dropna().unique().tolist())
    latest_year_idx = len(years) - 1 if years else 0

    selected_country = c1.selectbox("Country", countries)
    selected_year = c2.selectbox("Year", years, index=latest_year_idx)

    months_in_data = weekly_df.loc[
        (weekly_df["country_name"] == selected_country) & (weekly_df["year"] == selected_year),
        "month_name",
    ].dropna()
    month_order = list(calendar.month_name)[1:]
    available_months = [m for m in month_order if m in set(months_in_data.astype(str))]
    selected_month = c3.selectbox("Month", available_months)

    selected_category = c4.selectbox("Category", ["All", "Films", "TV"])

    filtered = weekly_df[
        (weekly_df["country_name"] == selected_country)
        & (weekly_df["year"] == selected_year)
        & (weekly_df["month_name"].astype(str) == selected_month)
    ].copy()

    agg = (
        filtered.groupby(["show_title", "category"], as_index=False)["score"]
        .sum()
        .rename(columns={"score": "performance_score"})
    )

    if selected_category != "All":
        agg = agg[agg["category"] == selected_category].copy()

    chart_df = (
        agg.sort_values("performance_score", ascending=False)
        .head(10)
        .sort_values("performance_score", ascending=True)
    )

    if chart_df.empty:
        st.warning("No data found for the selected filters.")
        return

    left, right = st.columns([3, 1])

    with left:
        bar_fig = px.bar(
            chart_df,
            x="performance_score",
            y="show_title",
            color="category",
            orientation="h",
            text="performance_score",
            color_discrete_map={"Films": PAGE_COLORS["yellow"], "TV": PAGE_COLORS["orange"]},
        )
        bar_fig.update_layout(
            height=500,
            paper_bgcolor=PAGE_COLORS["card"],
            plot_bgcolor=PAGE_COLORS["card"],
            font_color=PAGE_COLORS["text"],
            xaxis_title="",
            yaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        )
        bar_fig.update_traces(textposition="outside")
        st.plotly_chart(bar_fig, use_container_width=True)

    with right:
        films_count = int((chart_df["category"] == "Films").sum())
        tv_count = int((chart_df["category"] == "TV").sum())

        donut_fig = px.pie(
            names=["Films", "TV"],
            values=[films_count, tv_count],
            hole=0.6,
            color=["Films", "TV"],
            color_discrete_map={"Films": PAGE_COLORS["yellow"], "TV": PAGE_COLORS["orange"]},
        )
        donut_fig.update_traces(textinfo="percent+label")
        donut_fig.update_layout(
            showlegend=False,
            height=260,
            paper_bgcolor=PAGE_COLORS["card"],
            font_color=PAGE_COLORS["text"],
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(donut_fig, use_container_width=True)
        st.caption("Of top 10 titles in the chart")
        st.write(f"**Films:** {films_count}")
        st.write(f"**TV:** {tv_count}")


def home() -> None:
    if STYLE_PATH is not None and (STYLE_PATH / "dashboard.css").exists():
        read_css(STYLE_PATH / "dashboard.css")

    render_kpi_header()
    st.divider()
    render_analytics_section()


if __name__ == "__main__":
    home()
