import pandas as pd
import plotly.express as px
import streamlit as st

from netflix.components.filters import filters_ui
from netflix.utils.constants import STYLE_PATH
from netflix.utils.helpers import get_global_weekly_df, read_css


# -------------------------
# COLORS (UPDATED)
# -------------------------
SEGMENT_COLORS = {
    "Hype": "#E8622A",
    "Balanced": "#F7B952",
    "High Retention": "#4C78A8",
}


# -------------------------
# AGGREGATION (CORRECT GRAIN)
# -------------------------
@st.cache_data
def _aggregate_success_profile(filtered_df):
    if filtered_df.empty:
        return filtered_df

    profile_df = (
        filtered_df.groupby(["show_title", "category"], as_index=False)
        .agg(
            # FIX: weekly count inside month
            longevity=("week", "count"),
            performance_score=("weekly_rank", lambda s: (11 - s).sum()),
        )
        .copy()
    )

    # -------------------------
    # SEGMENTATION
    # -------------------------
    profile_df["segment"] = "Hype"
    profile_df.loc[profile_df["longevity"] == 4, "segment"] = "High Retention"
    profile_df.loc[profile_df["longevity"] == 3, "segment"] = "Balanced"

    # -------------------------
    # PICK BEST PER SEGMENT
    # -------------------------
    profile_df = (
        profile_df.sort_values("performance_score", ascending=False)
        .groupby("segment", as_index=False)
        .head(1)
        .copy()
    )

    # -------------------------
    # LABELS
    # -------------------------
    profile_df["point_label"] = (
        profile_df["show_title"]
        + "<br>"
        + profile_df["longevity"].astype(int).astype(str)
        + "w | "
        + profile_df["performance_score"].astype(int).astype(str)
    )

    return profile_df


# -------------------------
# DATA BUILDER
# -------------------------
@st.cache_data
def build_success_profile_data(df, country, year, month, category):

    strict_df = df[
        (df["country_name"] == country)
        & (df["year"] == year)
        & (df["month_name"] == month)
        & (df["category"] == category)
    ].copy()

    if not strict_df.empty:
        return _aggregate_success_profile(strict_df), "strict"

    # fallback
    relaxed_df = df[
        (df["country_name"] == country)
        & (df["year"] == year)
        & (df["category"] == category)
    ].copy()

    return _aggregate_success_profile(relaxed_df), "relaxed"


# -------------------------
# FIGURE
# -------------------------
def build_success_profile_figure(profile_df):

    fig = px.scatter(
        profile_df,
        x="longevity",
        y="performance_score",
        color="segment",
        color_discrete_map=SEGMENT_COLORS,
        text="point_label",
        hover_name="show_title",
    )

    fig.update_traces(
        mode="markers+text",
        marker=dict(size=26, line=dict(width=2, color="#FFFFFF")),
        textposition="top center",
        textfont=dict(color="#1A1612", size=15),
    )

    fig.update_layout(
        paper_bgcolor="#F5F0E8",
        plot_bgcolor="#F5F0E8",
        font=dict(color="#1A1612", size=16),
        legend_title_text="Segment",
        xaxis_title="Longevity (weeks in Top 10)",
        yaxis_title="Popularity",
        margin=dict(l=20, r=20, t=20, b=20),
    )

    # -------------------------
    # AXIS FIX (NO CLIPPING)
    # -------------------------
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#F7B952",
        range=[0.5, profile_df["longevity"].max() + 0.5],
        title_font=dict(size=18),
        tickfont=dict(size=15),
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#F7B952",
        range=[0, profile_df["performance_score"].max() * 1.2],
        showticklabels=False,
        title_font=dict(size=18),
    )

    return fig


# -------------------------
# PAGE
# -------------------------
def success_profile():
    read_css(STYLE_PATH / "dashboard.css")

    st.title("What does a successful show look like?")
    st.markdown("Compare top shows by longevity and popularity.")

    # Load data
    weekly_df = get_global_weekly_df()

    # -------------------------
    # FIX MONTH ORDER (PROPER)
    # -------------------------
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    weekly_df["month_name"] = pd.Categorical(
        weekly_df["month_name"],
        categories=month_order,
        ordered=True
    )

    # -------------------------
    # FILTERS
    # -------------------------
    country, year, month, category = filters_ui(weekly_df)

    # -------------------------
    # DATA
    # -------------------------
    profile_df, mode = build_success_profile_data(
        weekly_df, country, year, month, category
    )

    if profile_df.empty:
        st.warning("No data available for the selected filters.")
        return

    if mode == "relaxed":
        st.info(
            f"No rows for {month} in {country} ({year}, {category}). "
            "Showing broader data instead."
        )

    # -------------------------
    # CHART
    # -------------------------
    fig = build_success_profile_figure(profile_df)

    st.plotly_chart(fig, width="stretch")


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    success_profile()