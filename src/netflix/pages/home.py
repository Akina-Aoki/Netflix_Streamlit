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

TUDUM_SOURCE_URL = "https://www.netflix.com/tudum/top10/most-popular"

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


def inject_home_styles() -> None:
    """Inject Home page styling for Streamly KPI cards, about section, and filters."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@400;500;600;700;800&display=swap');

        .home-kpi-grid {{
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.9rem;
            margin: 1.4rem 0 1.4rem 0;
        }}

        .home-kpi-card {{
            background:
                radial-gradient(circle at top right, rgba(247, 185, 82, 0.15), transparent 42%),
                linear-gradient(180deg, {PAGE_COLORS["card"]} 0%, #17120E 100%);
            border: 1px solid {PAGE_COLORS["border"]};
            border-radius: 16px;
            padding: 1rem 1.05rem;
            min-height: 125px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
        }}

        .home-kpi-card:hover {{
            border-color: {PAGE_COLORS["yellow"]};
            transform: translateY(-1px);
            transition: 0.18s ease;
        }}

        .home-kpi-label {{
            color: {PAGE_COLORS["amber"]};
            font-family: "Inter", Arial, sans-serif;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.65rem;
        }}

        .home-kpi-value {{
            color: {PAGE_COLORS["text"]};
            font-family: "Inter", Arial, sans-serif;
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.05;
            margin-bottom: 0.45rem;
        }}

        .home-kpi-note {{
            color: {PAGE_COLORS["muted"]};
            font-family: "Inter", Arial, sans-serif;
            font-size: 0.82rem;
            line-height: 1.35;
        }}

        .home-about-card {{
            background:
                linear-gradient(135deg, rgba(247, 185, 82, 0.10), rgba(232, 98, 42, 0.04)),
                {PAGE_COLORS["card"]};
            border: 1px solid {PAGE_COLORS["border"]};
            border-left: 4px solid {PAGE_COLORS["orange"]};
            border-radius: 18px;
            padding: 1.25rem 1.35rem;
            margin: 1.3rem 0 1.6rem 0;
        }}

        .home-about-eyebrow {{
            color: {PAGE_COLORS["amber"]};
            font-family: "Inter", Arial, sans-serif;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }}

        .home-about-title {{
            color: {PAGE_COLORS["text"]};
            font-family: "Cormorant Garamond", Georgia, serif;
            font-size: 2.2rem;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 0.65rem;
        }}

        .home-about-body {{
            color: {PAGE_COLORS["muted"]};
            font-family: "Inter", Arial, sans-serif;
            font-size: 1rem;
            line-height: 1.55;
            max-width: 980px;
        }}

        .home-about-body a {{
            color: {PAGE_COLORS["yellow"]};
            font-weight: 800;
            text-decoration: none;
            border-bottom: 1px solid rgba(247, 185, 82, 0.55);
        }}

        .home-section-title {{
            color: {PAGE_COLORS["yellow"]};
            font-family: "Cormorant Garamond", Georgia, serif;
            font-size: 2.6rem;
            font-weight: 700;
            line-height: 1;
            margin: 1.4rem 0 0.35rem 0;
        }}

        .home-section-subtitle {{
            color: {PAGE_COLORS["text"]};
            font-family: "Inter", Arial, sans-serif;
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 0.35rem;
        }}

        .home-disclaimer {{
            color: {PAGE_COLORS["muted"]};
            font-family: "Inter", Arial, sans-serif;
            font-size: 0.9rem;
            margin-bottom: 1.25rem;
        }}

        .home-filter-section {{
            margin-top: 1.8rem;
            margin-bottom: 1.25rem;
        }}

        .home-filter-label {{
            font-family: "Inter", Arial, sans-serif;
            font-size: 0.82rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: {PAGE_COLORS["orange"]};
            margin-bottom: 0.45rem;
        }}

        div[data-testid="stSelectbox"] label {{
            display: none;
        }}

        div[data-baseweb="select"] > div {{
            background: linear-gradient(180deg, #2A2118 0%, #1A1612 100%) !important;
            border: 1px solid #3A2B1D !important;
            border-radius: 999px !important;
            min-height: 44px !important;
            color: {PAGE_COLORS["text"]} !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.04),
                0 0 0 1px rgba(247,185,82,0.06) !important;
        }}

        div[data-baseweb="select"] > div:hover {{
            border-color: {PAGE_COLORS["yellow"]} !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.04),
                0 0 0 1px rgba(247,185,82,0.25) !important;
        }}

        div[data-baseweb="select"] span {{
            color: {PAGE_COLORS["text"]} !important;
            font-family: "Inter", Arial, sans-serif !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
        }}

        div[data-baseweb="select"] svg {{
            color: {PAGE_COLORS["amber"]} !important;
            fill: {PAGE_COLORS["amber"]} !important;
        }}

        @media (max-width: 1100px) {{
            .home-kpi-grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_header() -> None:
    """Render branded Home section: logo, KPI cards, and about text."""
    kpis = load_home_kpis()

    total_films = f"{kpis['total_films']:,}"
    total_series = f"{kpis['total_series']:,}"
    total_countries = f"{kpis['total_countries']:,}"
    weeks_tracked = f"{kpis['weeks_tracked']:,}"
    total_hours_b = f"{kpis['total_hours'] / 1_000_000_000:.1f}B"

    st.image(str(IMAGE_PATH / "Logga_Streamly.png"), width=200)
    st.caption("Global Netflix viewing statistics")
    st.divider()

    st.markdown(
        f"""
        <div class="home-kpi-grid">
            <div class="home-kpi-card">
                <div class="home-kpi-label">Total Films</div>
                <div class="home-kpi-value">{total_films}</div>
                <div class="home-kpi-note">Unique film titles across Netflix viewing datasets.</div>
            </div>

            <div class="home-kpi-card">
                <div class="home-kpi-label">Total Series</div>
                <div class="home-kpi-value">{total_series}</div>
                <div class="home-kpi-note">Unique TV titles tracked across weekly and country data.</div>
            </div>

            <div class="home-kpi-card">
                <div class="home-kpi-label">Countries</div>
                <div class="home-kpi-value">{total_countries}</div>
                <div class="home-kpi-note">Markets represented in the country-level Top 10 data.</div>
            </div>

            <div class="home-kpi-card">
                <div class="home-kpi-label">Weeks Tracked</div>
                <div class="home-kpi-value">{weeks_tracked}</div>
                <div class="home-kpi-note">Weekly snapshots available for trend exploration.</div>
            </div>

            <div class="home-kpi-card">
                <div class="home-kpi-label">Hours Viewed</div>
                <div class="home-kpi-value">{total_hours_b}</div>
                <div class="home-kpi-note">Total global weekly viewing hours captured in the data.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="home-about-card">
            <div class="home-about-eyebrow">About this app</div>
            <div class="home-about-title">A visual pulse check on Netflix viewing behavior.</div>
            <div class="home-about-body">
                Streamly visualizes Netflix global viewing data across weekly and all-time datasets.
                Use the dashboard to explore what audiences watch, compare films and TV series,
                and understand how popularity shifts across countries and time.
                <br><br>
                The dataset is sourced from Netflix Tudum Top 10 data:
                <a href="{TUDUM_SOURCE_URL}" target="_blank">Netflix Tudum — Most Popular</a>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_analytics_section() -> None:
    """Render old Netflix analytics dashboard section below Home overview."""
    weekly_df = prepare_home_chart_data()

    st.markdown('<div class="home-section-title">Netflix Analytics</div>', unsafe_allow_html=True)
    st.markdown(
            """
    <div class="home-section-subtitle">
        Explore the top 10 films and series across countries, months, and categories.
    </div>
    """,
    unsafe_allow_html=True,
    )

    st.markdown(
    '<div class="home-disclaimer">Data is based on Netflix weekly Top 10 rankings.</div>',
    unsafe_allow_html=True,
    )

    st.markdown('<div class="home-filter-section">', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    countries = sorted(weekly_df["country_name"].dropna().unique().tolist())
    years = sorted(weekly_df["year"].dropna().unique().tolist())
    latest_year_idx = len(years) - 1 if years else 0

    with c1:
        st.markdown('<div class="home-filter-label">Country</div>', unsafe_allow_html=True)
        selected_country = st.selectbox(
            "Country",
            countries,
            label_visibility="collapsed",
        )

    with c2:
        st.markdown('<div class="home-filter-label">Year</div>', unsafe_allow_html=True)
        selected_year = st.selectbox(
            "Year",
            years,
            index=latest_year_idx,
            label_visibility="collapsed",
        )

    months_in_data = weekly_df.loc[
        (weekly_df["country_name"] == selected_country)
        & (weekly_df["year"] == selected_year),
        "month_name",
    ].dropna()

    month_order = list(calendar.month_name)[1:]
    available_months = [m for m in month_order if m in set(months_in_data.astype(str))]

    with c3:
        st.markdown('<div class="home-filter-label">Month</div>', unsafe_allow_html=True)
        selected_month = st.selectbox(
            "Month",
            available_months,
            label_visibility="collapsed",
        )

    with c4:
        st.markdown('<div class="home-filter-label">Category</div>', unsafe_allow_html=True)
        selected_category = st.selectbox(
            "Category",
            ["All", "Films", "TV"],
            label_visibility="collapsed",
        )

    st.markdown("</div>", unsafe_allow_html=True)

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

    inject_home_styles()

    render_kpi_header()
    render_analytics_section()


if __name__ == "__main__":
    home()
