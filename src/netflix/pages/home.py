import calendar

import pandas as pd
import plotly.express as px
import streamlit as st
from netflix.utils.constants import STYLE_PATH
from netflix.utils.helpers import get_global_weekly_df, read_css


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


@st.cache_data
def prepare_home_data() -> pd.DataFrame:
    df = get_global_weekly_df().copy()
    df["week"] = pd.to_datetime(df["week"], errors="coerce")
    df = df.dropna(subset=["week", "weekly_rank", "show_title", "category", "country_name"])
    df["year"] = df["week"].dt.year
    df["month_num"] = df["week"].dt.month
    df["month_name"] = pd.Categorical(
        df["week"].dt.month_name(),
        categories=list(calendar.month_name)[1:],
        ordered=True,
    )
    df["score"] = 11 - pd.to_numeric(df["weekly_rank"], errors="coerce")
    df = df[df["score"].notna() & (df["score"] > 0)]
    return df

def home() -> None:
    read_css(STYLE_PATH / "dashboard.css")

    st.markdown('<div class="home-shell">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="brand-block">
            <p class="brand-name">Streamly</p>
            <p class="brand-subtitle">SHOWS STATISTICS</p>
        </div>
        <div class="hero-card">
            <h1>Netflix Analytics</h1>
            <p>
                Explore the top 10 movies and series across countries. Filter by country, year,
                month, and category to understand what performs best over time.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = prepare_home_data()

    st.markdown('<div class="filter-title">FILTER</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    country_options = sorted(df["country_name"].dropna().unique().tolist())
    selected_country = c1.selectbox("Country", country_options, index=0)

    year_options = sorted(df["year"].dropna().astype(int).unique().tolist())
    selected_year = c2.selectbox("Year", year_options, index=len(year_options) - 1)

    month_options = [m for m in list(calendar.month_name)[1:] if m in df["month_name"].astype(str).unique()]
    selected_month = c3.selectbox("Month", month_options, index=0)

    category_options = ["Films", "TV"]
    selected_category = c4.selectbox("Category", category_options, index=0)

    filtered = df[
        (df["country_name"] == selected_country)
        & (df["year"] == selected_year)
        & (df["month_name"].astype(str) == selected_month)
        & (df["category"] == selected_category)
    ].copy()

    agg = (
        filtered.groupby(["show_title", "category"], as_index=False)["score"]
        .sum()
        .rename(columns={"score": "performance_score"})
        .sort_values("performance_score", ascending=False)
        .head(10)
    )

    left, right = st.columns([3, 1])

    with left:
        st.markdown('<div class="chart-title">Top Chart</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="chart-subtitle">This chart scores each title by combining rank position and time spent in the Top 10. Higher-ranked and longer-lasting titles receive stronger scores.</div>',
            unsafe_allow_html=True,
        )

        if agg.empty:
            st.warning("No data found for the selected filters. Try a different month, year, or category.")
        else:
            chart_df = agg.sort_values("performance_score", ascending=True)
            fig = px.bar(
                chart_df,
                x="performance_score",
                y="show_title",
                color="category",
                orientation="h",
                text="performance_score",
                color_discrete_map={"Films": PAGE_COLORS["yellow"], "TV": PAGE_COLORS["orange"]},
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                margin=dict(l=10, r=30, t=10, b=10),
                paper_bgcolor=PAGE_COLORS["card"],
                plot_bgcolor=PAGE_COLORS["card"],
                font=dict(color=PAGE_COLORS["text"], family="Segoe UI, sans-serif"),
                xaxis=dict(showgrid=False, title=None),
                yaxis=dict(showgrid=False, title=None),
                legend_title_text="",
                legend=dict(orientation="h", y=1.08, x=0.75),
                height=500,
            )
            st.plotly_chart(fig, use_container_width=True)

    with right:
        films_count = int((agg["category"] == "Films").sum()) if not agg.empty else 0
        tv_count = int((agg["category"] == "TV").sum()) if not agg.empty else 0
        st.markdown(
            f"""
            <div class="summary-card">
                <h3>Movies vs Series</h3>
                <p>Of top 10 titles in the chart</p>
                <div class="summary-stat"><span>Films</span><strong>{films_count}</strong></div>
                <div class="summary-stat"><span>TV</span><strong>{tv_count}</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    home()