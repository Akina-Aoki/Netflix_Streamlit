import calendar
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from netflix.utils.constants import STYLES_PATH
from netflix.utils.helpers import get_weekly_df, read_css


SEGMENT_COLORS = {
    "Hype": "#E63946",
    "Balanced": "#F4A261",
    "High Retention": "#2A9D8F",
}

BRAND_COLORS = {
    "bg": "#0F0D0B",
    "card": "#1A1612",
    "surface": "#2A2118",
    "amber": "#F7B952",
    "orange": "#E8622A",
    "amber_dark": "#FFB84D",
    "text": "#F5F0E8",
    "muted": "#9E9689",
    "green": "#2A9D8F",
    "red": "#E63946",
}

CHART_COLORS = {
    "background": "#F5F0E8",
    "text": "#111111",
    "muted_text": "#4A4A4A",
    "axis": "#222222",
    "vertical_guide": "#E8C87E",
}

BASE_DIR = Path(__file__).resolve().parents[1]
LOGO_PATH = BASE_DIR / "assets" / "image" / "Logga_Streamly.png"

MONTH_ORDER = list(calendar.month_name)[1:]

REQUIRED_COLUMNS = {
    "country_name",
    "week",
    "weekly_rank",
    "show_title",
    "category",
}


def get_global_weekly_df() -> pd.DataFrame:
    """Compatibility wrapper for the older Success Profile page naming."""
    return get_weekly_df()


def _inject_success_profile_styles() -> None:
    """Inject local page styles for the branded Streamly header and cards."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');

        .sp-header {{
            margin-top: 0.2rem;
            margin-bottom: 0.4rem;
        }}

        .sp-title {{
            font-family: "Cormorant Garamond", Georgia, "Times New Roman", serif;
            font-size: 3.25rem;
            line-height: 0.95;
            font-weight: 700;
            color: {BRAND_COLORS["amber"]};
            letter-spacing: -0.02em;
            margin: 0;
        }}

        .sp-subtitle {{
            font-family: "Inter", Arial, sans-serif;
            font-size: 1.05rem;
            font-weight: 500;
            color: {BRAND_COLORS["text"]};
            margin-top: 0.55rem;
            margin-bottom: 1rem;
        }}

        .sp-card {{
            background: linear-gradient(180deg, {BRAND_COLORS["card"]} 0%, #17120E 100%);
            border: 1px solid {BRAND_COLORS["surface"]};
            border-radius: 14px;
            padding: 0.95rem 1rem 1rem 1rem;
            min-height: 140px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
        }}

        .sp-card-title {{
            font-family: "Inter", Arial, sans-serif;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.55rem;
        }}

        .sp-card-body {{
            font-family: "Inter", Arial, sans-serif;
            font-size: 0.95rem;
            line-height: 1.55;
            color: {BRAND_COLORS["text"]};
        }}

        .sp-card-metric {{
            border-top: 4px solid {BRAND_COLORS["amber"]};
        }}

        .sp-card-retention {{
            border-top: 4px solid {BRAND_COLORS["green"]};
        }}

        .sp-card-balanced {{
            border-top: 4px solid {BRAND_COLORS["amber_dark"]};
        }}

        .sp-card-hype {{
            border-top: 4px solid {BRAND_COLORS["red"]};
        }}

        .sp-metric-title {{
            color: {BRAND_COLORS["amber"]};
        }}

        .sp-retention-title {{
            color: {BRAND_COLORS["green"]};
        }}

        .sp-balanced-title {{
            color: {BRAND_COLORS["amber_dark"]};
        }}

        .sp-hype-title {{
            color: {BRAND_COLORS["red"]};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_success_profile_header() -> None:
    """Render the branded page header."""
    st.markdown(
        """
        <div class="sp-header">
            <div class="sp-title">What does a successful show look like?</div>
            <div class="sp-subtitle">Compare top shows by longevity and popularity.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def prepare_success_profile_data() -> pd.DataFrame:
    """Load and clean weekly data for the Success Profile page."""
    df = get_global_weekly_df().copy()

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        return pd.DataFrame({"_missing_columns": [", ".join(sorted(missing_columns))]})

    df["week"] = pd.to_datetime(df["week"], errors="coerce")
    df["weekly_rank"] = pd.to_numeric(df["weekly_rank"], errors="coerce")

    df = df.dropna(
        subset=[
            "country_name",
            "week",
            "weekly_rank",
            "show_title",
            "category",
        ]
    ).copy()

    df["year"] = df["week"].dt.year
    df["month_name"] = df["week"].dt.month_name()

    df["month_name"] = pd.Categorical(
        df["month_name"],
        categories=MONTH_ORDER,
        ordered=True,
    )

    return df


@st.cache_data
def _aggregate_success_profile(filtered_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate filtered weekly rows into robust storytelling segments.

    This version tries to pick three archetypes:
    - Hype = strongest popularity score
    - High Retention = strongest longevity
    - Balanced = strongest combined longevity + popularity
    """
    if filtered_df.empty:
        return pd.DataFrame()

    profile_df = (
        filtered_df.groupby(["show_title", "category"], as_index=False)
        .agg(
            longevity=("week", "count"),
            performance_score=("weekly_rank", lambda ranks: (11 - ranks).sum()),
        )
        .copy()
    )

    if profile_df.empty:
        return pd.DataFrame()

    profile_df["longevity"] = pd.to_numeric(profile_df["longevity"], errors="coerce")
    profile_df["performance_score"] = pd.to_numeric(
        profile_df["performance_score"],
        errors="coerce",
    )

    profile_df = profile_df.dropna(
        subset=[
            "show_title",
            "category",
            "longevity",
            "performance_score",
        ]
    ).copy()

    if profile_df.empty:
        return pd.DataFrame()

    selected_rows = []
    used_titles = set()

    def pick_first_available(candidate_df: pd.DataFrame, segment_name: str) -> None:
        """Pick the first candidate that has not already been used."""
        for _, row in candidate_df.iterrows():
            title = row["show_title"]
            if title not in used_titles:
                selected = row.copy()
                selected["segment"] = segment_name
                selected_rows.append(selected)
                used_titles.add(title)
                return

    # 1. Hype = strongest popularity / highest performance score
    hype_candidates = profile_df.sort_values(
        ["performance_score", "longevity"],
        ascending=[False, False],
    )
    pick_first_available(
        candidate_df=hype_candidates,
        segment_name="Hype",
    )

    # 2. High Retention = strongest longevity
    retention_candidates = profile_df.sort_values(
        ["longevity", "performance_score"],
        ascending=[False, False],
    )
    pick_first_available(
        candidate_df=retention_candidates,
        segment_name="High Retention",
    )

    # 3. Balanced = best combined normalized longevity + popularity
    longevity_max = profile_df["longevity"].max()
    performance_max = profile_df["performance_score"].max()

    profile_df["longevity_norm"] = (
        profile_df["longevity"] / longevity_max if longevity_max > 0 else 0
    )
    profile_df["performance_norm"] = (
        profile_df["performance_score"] / performance_max if performance_max > 0 else 0
    )
    profile_df["balance_score"] = (
        profile_df["longevity_norm"] + profile_df["performance_norm"]
    )

    balanced_candidates = profile_df.sort_values(
        ["balance_score", "performance_score", "longevity"],
        ascending=[False, False, False],
    )
    pick_first_available(
        candidate_df=balanced_candidates,
        segment_name="Balanced",
    )

    result_df = pd.DataFrame(selected_rows)

    if result_df.empty:
        return pd.DataFrame()

    result_df["point_label"] = (
        result_df["show_title"].astype(str)
        + "<br>"
        + result_df["longevity"].astype(int).astype(str)
        + "w | "
        + result_df["performance_score"].astype(int).astype(str)
    )

    segment_order = ["Balanced", "High Retention", "Hype"]
    result_df["segment"] = pd.Categorical(
        result_df["segment"],
        categories=segment_order,
        ordered=True,
    )

    return result_df.sort_values("segment").reset_index(drop=True)


@st.cache_data
def build_success_profile_data(
    df: pd.DataFrame,
    country: str,
    year: int,
    month: str,
    category: str,
) -> tuple[pd.DataFrame, str]:
    """Build profile data using strict monthly filters, then yearly fallback."""
    strict_df = df[
        (df["country_name"] == country)
        & (df["year"] == year)
        & (df["month_name"].astype(str) == month)
        & (df["category"] == category)
    ].copy()

    if not strict_df.empty:
        return _aggregate_success_profile(strict_df), "strict"

    relaxed_df = df[
        (df["country_name"] == country)
        & (df["year"] == year)
        & (df["category"] == category)
    ].copy()

    return _aggregate_success_profile(relaxed_df), "relaxed"


def build_success_profile_figure(profile_df: pd.DataFrame):
    """Create the cream storytelling-style Success Profile scatter chart."""
    y_max = profile_df["performance_score"].max()
    x_max = profile_df["longevity"].max()

    x_axis_max = x_max + 1
    y_axis_max = y_max * 1.35 if y_max > 0 else 1

    fig = px.scatter(
        profile_df,
        x="longevity",
        y="performance_score",
        color="segment",
        color_discrete_map=SEGMENT_COLORS,
        category_orders={"segment": ["Balanced", "High Retention", "Hype"]},
        text="point_label",
        hover_name="show_title",
    )

    fig.update_traces(
        mode="markers+text",
        marker=dict(size=26, line=dict(width=2, color="#FFFFFF")),
        textposition="top center",
        textfont=dict(color=CHART_COLORS["text"], size=15),
        cliponaxis=False,
    )

    fig.update_layout(
        height=650,
        paper_bgcolor=CHART_COLORS["background"],
        plot_bgcolor=CHART_COLORS["background"],
        font=dict(color=CHART_COLORS["text"], size=16),
        legend=dict(
            title=dict(
                text="Segment",
                font=dict(color=CHART_COLORS["text"], size=15),
            ),
            font=dict(color=CHART_COLORS["text"], size=14),
            bgcolor="rgba(255, 253, 248, 0.92)",
            bordercolor=CHART_COLORS["axis"],
            borderwidth=1,
            orientation="h",
            x=0.98,
            xanchor="right",
            y=0.98,
            yanchor="top",
        ),
        xaxis_title="Longevity (weeks in Top 10)",
        yaxis_title="Popularity",
        margin=dict(l=80, r=80, t=40, b=80),
    )

    # Vertical grid lines ON
    fig.update_xaxes(
        showgrid=True,
        gridcolor=CHART_COLORS["vertical_guide"],
        showline=False,
        zeroline=False,
        range=[0, x_axis_max],
        title_font=dict(size=20, color=CHART_COLORS["text"]),
        tickfont=dict(size=15, color=CHART_COLORS["text"]),
        tickcolor=CHART_COLORS["axis"],
        title_standoff=22,
    )

    # Horizontal grid lines OFF
    fig.update_yaxes(
        showgrid=False,
        showline=False,
        zeroline=False,
        range=[0, y_axis_max],
        showticklabels=False,
        title_font=dict(size=20, color=CHART_COLORS["text"]),
        title_standoff=24,
    )

    arrow_style = dict(
        showarrow=True,
        arrowhead=3,
        arrowwidth=2,
        arrowcolor=CHART_COLORS["text"],
        text="",
    )

    # X-axis arrow
    fig.add_annotation(
        x=x_axis_max,
        y=0,
        ax=0,
        ay=0,
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        **arrow_style,
    )

    # Y-axis arrow
    fig.add_annotation(
        x=0,
        y=y_axis_max,
        ax=0,
        ay=0,
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        **arrow_style,
    )

    return fig


def _render_success_story_cards() -> None:
    """Render 4 branded storytelling cards above the filters."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="sp-card sp-card-metric">
                <div class="sp-card-title sp-metric-title">How to read this chart</div>
                <div class="sp-card-body">
                    <strong>Weeks</strong> = time in Top 10.<br>
                    <strong>Score</strong> = how popular the show was.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="sp-card sp-card-retention">
                <div class="sp-card-title sp-retention-title">High Retention</div>
                <div class="sp-card-body">
                    People keep watching again and again.<br><br>
                    These titles stay in the Top 10 longer and show stronger staying power.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="sp-card sp-card-balanced">
                <div class="sp-card-title sp-balanced-title">Balanced Success</div>
                <div class="sp-card-body">
                    Strong popularity and strong retention.<br><br>
                    These titles combine momentum with consistency.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="sp-card sp-card-hype">
                <div class="sp-card-title sp-hype-title">Hype</div>
                <div class="sp-card-body">
                    Strongest popularity spike.<br><br>
                    These titles rise fast and stand out through high popularity score.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_success_filters(df: pd.DataFrame) -> tuple[str, int, str, str]:
    """Render filters local to this page so shared filters stay unchanged."""
    countries = sorted(df["country_name"].dropna().unique().tolist())
    years = sorted(df["year"].dropna().unique().tolist(), reverse=True)
    months_in_data = set(df["month_name"].dropna().astype(str).unique().tolist())
    months = [month for month in MONTH_ORDER if month in months_in_data]
    categories = sorted(df["category"].dropna().unique().tolist())

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        country = st.selectbox("Country", countries, index=0)

    with col2:
        year = st.selectbox("Year", years, index=0)

    with col3:
        month = st.selectbox("Month", months, index=0)

    with col4:
        category = st.selectbox("Category", categories, index=0)

    return country, year, month, category


def _render_streamly_banner() -> None:
    """Render the Streamly logo banner above the page title."""
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=220)
    else:
        st.markdown(
            f"""
            <div style="
                color: {BRAND_COLORS['amber']};
                font-family: Georgia, 'Times New Roman', serif;
                font-size: 3rem;
                font-weight: 700;
                line-height: 1;
                margin-bottom: 0.2rem;
            ">
                Streamly
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div style="
            color: {BRAND_COLORS['muted']};
            font-size: 0.95rem;
            margin-top: -0.25rem;
            margin-bottom: 1.1rem;
        ">
            Global Netflix viewing statistics
        </div>

        <div style="
            height: 1px;
            background: {BRAND_COLORS['surface']};
            margin: 0 0 1.8rem 0;
        "></div>
        """,
        unsafe_allow_html=True,
    )


def success_profile() -> None:
    """Render the Success Profile page."""
    css_path = STYLES_PATH / "dashboard.css"
    if css_path.exists():
        read_css(css_path)

    _inject_success_profile_styles()
    _render_streamly_banner()
    _render_success_profile_header()
    _render_success_story_cards()

    weekly_df = prepare_success_profile_data()

    if "_missing_columns" in weekly_df.columns:
        st.error(
            "Success Profile cannot render because these required columns are missing: "
            f"{weekly_df['_missing_columns'].iloc[0]}"
        )
        return

    if weekly_df.empty:
        st.warning("No weekly data available.")
        return

    country, year, month, category = _render_success_filters(weekly_df)

    profile_df, mode = build_success_profile_data(
        weekly_df,
        country,
        year,
        month,
        category,
    )

    if profile_df.empty:
        st.warning("No data available for the selected filters.")
        return

    if mode == "relaxed":
        st.info(
            f"No rows for {month} in {country} ({year}, {category}). "
            "Showing broader yearly data instead."
        )

    fig = build_success_profile_figure(profile_df)
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    success_profile()