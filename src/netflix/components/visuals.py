import importlib.util

import pandas as pd
import plotly.express as px

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


def _iso2_to_iso3(iso2_code: str) -> str | None:
    if importlib.util.find_spec("pycountry") is None:
        return None
    
    import pycountry

    country = pycountry.countries.get(alpha_2=str(iso2_code).upper())
    return country.alpha_3 if country else None


def make_country_choropleth(df: pd.DataFrame, selected_country: str):
    columns = ["country_name"]

    if "country_iso2" in df.columns:
        columns.append("country_iso2")

    countries = (
        df[columns]
        .dropna(subset=["country_name"])
        .drop_duplicates()
        .copy()
    )

    if countries.empty:
        return None

    location_column = "country_name"
    location_mode = "country names"
    custom_data = ["country_name"]

    if "country_iso2" in countries.columns:
        countries["iso3"] = countries["country_iso2"].apply(_iso2_to_iso3)

        if countries["iso3"].notna().any():
            countries = countries.dropna(subset=["iso3"]).copy()
            location_column = "iso3"
            location_mode = "ISO-3"
            custom_data = ["country_name", "country_iso2"]

    countries["is_selected"] = (
        countries["country_name"] == selected_country
    ).astype(int)

    fig = px.choropleth(
        countries,
        locations=location_column,
        locationmode=location_mode,
        hover_name="country_name",
        custom_data=custom_data,
        color="is_selected",
        color_continuous_scale=[
            PAGE_COLORS["muted"],
            PAGE_COLORS["yellow"],
        ],
        range_color=(0, 1),
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=PAGE_COLORS["card"],
        plot_bgcolor=PAGE_COLORS["card"],
        font=dict(
            color=PAGE_COLORS["text"],
            family="Segoe UI, sans-serif",
        ),
        coloraxis_showscale=False,
        geo=dict(
            showframe=False,
            showcoastlines=False,
            bgcolor=PAGE_COLORS["card"],
            projection_type="natural earth",
        ),
        height=360,
    )

    return fig