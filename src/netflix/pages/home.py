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

    df = df.dropna(
        subset=["week", "weekly_rank", "show_title", "category", "country_name"]
    )

    df["year"] = df["week"].dt.year
    df["month_num"] = df["week"].dt.month

    df["month_name"] = pd.Categorical(
        df["week"].dt.month_name(),
        categories=list(calendar.month_name)[1:],
        ordered=True,
    )

    # Performance score (same logic as your project)
    df["score"] = 11 - pd.to_numeric(df["weekly_rank"], errors="coerce")
    df = df[df["score"].notna() & (df["score"] > 0)]

    return df


def home() -> None:
    read_css(STYLE_PATH / "dashboard.css")

    st.markdown('<div class="home-shell">', unsafe_allow_html=True)

    # -------------------------
    # HERO
    # -------------------------
    st.markdown(
        """
        <div class="brand-block">
            <p class="brand-name">Streamly</p>
            <p class="brand-subtitle">SHOWS STATISTICS</p>
        </div>

        <div class="hero-card">
            <h1>Netflix Analytics</h1>
            <p>
                Explore the top 10 movies and series across countries. 
                Filter by country, year, month, and category to understand what performs best over time.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = prepare_home_data()

    # -------------------------
    # DISCLAIMER
    # -------------------------
    st.markdown(
        '<div class="disclaimer">Data from Netflix Tudum is available from July 2021 to March 2026. Filters outside this range will return no results.</div>',
        unsafe_allow_html=True,
    )

    # -------------------------
    # FILTERS
    # -------------------------
    st.markdown('<div class="filter-title">FILTER</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    country_options = sorted(df["country_name"].dropna().unique().tolist())
    selected_country = c1.selectbox("Country", country_options, index=0)

    year_options = sorted(df["year"].dropna().astype(int).unique().tolist())
    selected_year = c2.selectbox("Year", year_options, index=len(year_options) - 1)

    month_options = [
        m
        for m in list(calendar.month_name)[1:]
        if m in df["month_name"].astype(str).unique()
    ]
    selected_month = c3.selectbox("Month", month_options, index=0)

    category_options = ["All", "Films", "TV"]
    selected_category = c4.selectbox("Category", category_options, index=0)

    # -------------------------
    # FILTER DATA
    # -------------------------
    filtered = df[
        (df["country_name"] == selected_country)
        & (df["year"] == selected_year)
        & (df["month_name"].astype(str) == selected_month)
    ].copy()

    if selected_category != "All":
        filtered = filtered[filtered["category"] == selected_category].copy()

    # -------------------------
    # AGGREGATION (FIXED LOGIC)
    # -------------------------
    if selected_category == "All":
        agg = (
            filtered.groupby("show_title", as_index=False)
            .agg(
                performance_score=("score", "sum"),
                category=("category", "first"),  # only for color
            )
        )
    else:
        agg = (
            filtered.groupby(["show_title", "category"], as_index=False)["score"]
            .sum()
            .rename(columns={"score": "performance_score"})
        )

    # Top 10 (correct global ranking)
    chart_df = (
        agg.sort_values("performance_score", ascending=False)
        .head(10)
        .sort_values("performance_score", ascending=True)
    )

    left, right = st.columns([3, 1])

    # -------------------------
    # LEFT → BAR CHART
    # -------------------------
    with left:
        st.markdown('<div class="chart-title">Top Chart</div>', unsafe_allow_html=True)

        st.markdown(
            '<div class="chart-subtitle">This chart scores each title by combining rank position and time spent in the Top 10. Higher-ranked and longer-lasting titles receive stronger scores.</div>',
            unsafe_allow_html=True,
        )

        if chart_df.empty:
            st.warning("No data found for the selected filters.")
        else:
            fig = px.bar(
                chart_df,
                x="performance_score",
                y="show_title",
                color="category",
                orientation="h",
                text="performance_score",
                color_discrete_map={
                    "Films": PAGE_COLORS["yellow"],
                    "TV": PAGE_COLORS["orange"],
                },
            )

            fig.update_traces(textposition="outside")

            fig.update_layout(
                margin=dict(l=10, r=30, t=10, b=10),
                paper_bgcolor=PAGE_COLORS["card"],
                plot_bgcolor=PAGE_COLORS["card"],
                font=dict(color=PAGE_COLORS["text"], family="Segoe UI"),
                xaxis=dict(showgrid=False, title=None),
                yaxis=dict(showgrid=False, title=None),
                legend_title_text="",
                legend=dict(
                    orientation="h",
                    y=1.08,
                    x=0.0,
                    font=dict(size=14),
                    bgcolor="rgba(0,0,0,0)",
                ),
                height=500,
            )

            st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # RIGHT → DONUT + COUNTS (SINGLE CARD)
    # -------------------------
    with right:
        films_count = int((chart_df["category"] == "Films").sum()) if not chart_df.empty else 0
        tv_count = int((chart_df["category"] == "TV").sum()) if not chart_df.empty else 0

        st.markdown('<div class="summary-card">', unsafe_allow_html=True)

        st.markdown("<h3>Films vs TV</h3>", unsafe_allow_html=True)

        donut_fig = px.pie(
            names=["Films", "TV"],
            values=[films_count, tv_count],
            hole=0.6,
        )

        donut_fig.update_traces(
            marker=dict(colors=[PAGE_COLORS["yellow"], PAGE_COLORS["orange"]]),
            textinfo="percent+label",
        )

        donut_fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=10),
            paper_bgcolor=PAGE_COLORS["card"],
            plot_bgcolor=PAGE_COLORS["card"],
            font=dict(color=PAGE_COLORS["text"]),
            showlegend=False,
            height=260,
        )

        st.plotly_chart(donut_fig, use_container_width=True)

        st.markdown(
            f"""
            <p>Of top 10 titles in the chart</p>
            <div class="summary-stat"><span>Films</span><strong>{films_count}</strong></div>
            <div class="summary-stat"><span>TV</span><strong>{tv_count}</strong></div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    home()