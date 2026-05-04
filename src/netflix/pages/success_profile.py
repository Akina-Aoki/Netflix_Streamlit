import plotly.express as px
import streamlit as st

from netflix.components.filters import filters_ui
from netflix.utils.constants import STYLE_PATH
from netflix.utils.helpers import get_global_weekly_df, read_css

SEGMENT_COLORS = {
    "Evergreen": "#4C78A8",
    "Blockbuster": "#F7B952",
    "Hype": "#E45756",
}


@st.cache_data
def _aggregate_success_profile(filtered_df):
    if filtered_df.empty:
        return filtered_df

    profile_df = (
        filtered_df.groupby(["show_title", "category"], as_index=False)
        .agg(
            longevity=("cumulative_weeks_in_top_10", "max"),
            performance_score=("weekly_rank", lambda s: (11 - s).sum()),
        )
        .sort_values("performance_score", ascending=False)
        .head(3)
        .copy()
    )

    profile_df["segment"] = "Hype"
    profile_df.loc[
        (profile_df["longevity"] >= 40) & (profile_df["performance_score"] >= 20000),
        "segment",
    ] = "Blockbuster"
    profile_df.loc[profile_df["longevity"] >= 80, "segment"] = "Evergreen"

    profile_df["point_label"] = (
        profile_df["show_title"]
        + "<br>"
        + profile_df["longevity"].astype(int).astype(str)
        + "w | "
        + profile_df["performance_score"].astype(int).astype(str)
    )

    return profile_df


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

    relaxed_df = df[
        (df["country_name"] == country)
        & (df["year"] == year)
        & (df["category"] == category)
    ].copy()
    return _aggregate_success_profile(relaxed_df), "relaxed"


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
        marker=dict(size=22, line=dict(width=1, color="#FFFFFF")),
        textposition="bottom center",
        textfont=dict(color="#FFFFFF", size=12),
    )

    fig.update_layout(
        paper_bgcolor="#0F0D0B",
        plot_bgcolor="#0F0D0B",
        font=dict(color="#FFFFFF"),
        legend_title_text="Segment",
        xaxis_title="Longevity (weeks in Top 10)",
        yaxis_title="Performance Score",
        margin=dict(l=20, r=20, t=20, b=20),
    )

    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.15)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.15)")
    return fig


def success_profile():
    read_css(STYLE_PATH / "dashboard.css")

    st.title("What does a successful show look like?")
    st.markdown("Compare top shows by longevity and popularity.")


    weekly_df = get_global_weekly_df()
    country, year, month, category = filters_ui(weekly_df)

    profile_df, mode = build_success_profile_data(weekly_df, country, year, month, category)

    if profile_df.empty:
        st.warning("No data available for the selected filters.")
        return

    if mode == "relaxed":
        st.info(
            f"No rows for {month} in {country} ({year}, {category}). "
            "Showing the same country/year/category across all months instead."
        )

    fig = build_success_profile_figure(profile_df)
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    success_profile()
