import streamlit as st
from netflix.utils.helpers import get_global_df, get_metadata_df
from netflix.utils.helpers import read_css
from netflix.utils.constants import STYLES_PATH

read_css(STYLES_PATH / "insights.css")
