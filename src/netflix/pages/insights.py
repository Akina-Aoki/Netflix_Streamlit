import streamlit as st
from netflix.utils.helpers import get_global_df, get_metadata_df
from netflix.utils.helpers import read_css
from netflix.utils.constants import STYLES_PATH


read_css(STYLES_PATH / "insights.css")

df_global = get_global_df()
df_metadata = get_metadata_df()

st.title("Compare titles")
st.caption("Select two titles to compare side by side")
st.divider()

# Dropdowns
all_titles = sorted(df_global["show_title"].unique())
col_left, col_right = st.columns(2, gap="large", vertical_alignment="top")

with col_left:
    title_left = st.selectbox(
        label="Select first title",
        options=all_titles,
        index=None,
        placeholder="Choose a title",
        key="left",
    )

with col_right:
    title_right = st.selectbox(
        label="Select second title",
        options=all_titles,
        index=None,
        placeholder="Choose a title",
        key="right",
    )


def show_poster(meta):
    """Visar filmpostern om den finns annars felmedalande"""
    if meta is not None and str(meta["image"]) != "nan":
        st.image(meta["image"], width=250)

    else:
        st.caption("Image is not available")


def show_info(title, meta):
    """Visar titel, rating, beskrivning och cast, annars felmeddelande"""
    st.subheader(title.title())
    if meta is not None:
        st.caption(f"⭐ {meta['rating']} / 10")

        description = (
            str(meta["description"])
            if str(meta["description"]) != "nan"
            else "Data is not available"
        )
        if len(description) > 150:
            description = description[:150] + "..."
        st.write(description)

        st.caption(
            f"**Cast:** {meta['cast_members'] if str(meta['cast_members']) != 'nan' else 'Data is not available'}"
        )
        if str(meta["trailer"]) != "nan":
            st.link_button("▶ Play Trailer", meta["trailer"])

    else:
        st.warning("Data is not available")


def get_metadata(title):
    """Get metadata for selected title"""
    match = df_metadata[df_metadata["show_title"] == title.lower()]
    return match.iloc[0] if not match.empty else None


def show_kpi(stats):
    """Visar KPI-kort med statistik annars felmeddelande"""
    if stats is not None:
        st.divider()
        k1, k2, k3 = st.columns(3)
        k1.metric("Weeks in Global Top 10", stats["global_weeks_in_top10"], border=True)
        k2.metric("Best Global Rank Achieved", stats["global_best_rank"], border=True)
        k3.metric(
            "Average Global Rank in Top 10", stats["global_avg_rank"], border=True
        )
    else:
        st.warning("Data is missing")


def show_title_card(col, title, meta, stats):
    """Samlar alla delar i ett kort, anropar show_posterm show_info och show_kpi"""

    with col:
        show_poster(meta)
        show_info(title, meta)
        show_kpi(stats)


def get_stats(title):
    """Hämtar statistik för den givna titeln från FactGlobal_Final.csv"""
    data = df_global[df_global["show_title"] == title]
    if data.empty:
        return None
    return {
        "global_weeks_in_top10": int(data["cumulative_weeks_in_top_10"].max()),
        "global_best_rank": int(data["weekly_rank"].min()),
        "global_avg_rank": round(data["weekly_rank"].mean()),
    }


if title_left:
    meta_left = get_metadata(title_left)
    stats_left = get_stats(title_left)
    show_title_card(col_left, title_left, meta_left, stats_left)


if title_right:
    meta_right = get_metadata(title_right)
    stats_right = get_stats(title_right)
    show_title_card(col_right, title_right, meta_right, stats_right)
