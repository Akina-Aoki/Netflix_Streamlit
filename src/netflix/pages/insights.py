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
        st.write(
            meta["description"]
            if str(meta["description"]) != "nan"
            else "Data is not available"
        )
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


if title_left:
    meta_left = get_metadata(title_left)
    with col_left:
        show_poster(meta_left)
        show_info(title_left, meta_left)

if title_right:
    meta_right = get_metadata(title_right)
    with col_right:
        show_poster(meta_right)
        show_info(title_right, meta_right)
