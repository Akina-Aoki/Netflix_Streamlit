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
    try:
        import pycountry

        country = pycountry.countries.get(alpha_2=str(iso2_code).upper())
        return country.alpha_3 if country else None
    except Exception:
        return None


def make_country_choropleth(df: pd.DataFrame, selected_country: str):
    countries = (
        df[["country_name", "country_iso2"]]
        .dropna(subset=["country_name", "country_iso2"])
        .drop_duplicates()
        .copy()
    )
    if countries.empty:
        return None

    countries["iso3"] = countries["country_iso2"].apply(_iso2_to_iso3)
    countries = countries.dropna(subset=["iso3"]).copy()
    if countries.empty:
        return None

    countries["is_selected"] = (countries["country_name"] == selected_country).astype(int)

    fig = px.choropleth(
        countries,
        locations="iso3",
        locationmode="ISO-3",
        hover_name="country_name",
        custom_data=["country_name", "country_iso2"],
        color="is_selected",
        color_continuous_scale=[PAGE_COLORS["muted"], PAGE_COLORS["yellow"]],
        range_color=(0, 1),
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=PAGE_COLORS["card"],
        plot_bgcolor=PAGE_COLORS["card"],
        font=dict(color=PAGE_COLORS["text"], family="Segoe UI, sans-serif"),
        coloraxis_showscale=False,
        geo=dict(showframe=False, showcoastlines=False, bgcolor=PAGE_COLORS["card"], projection_type="natural earth"),
        height=360,
    )
    return fig



def make_success_scatter(df: pd.DataFrame):

    # -------------------------
    # AGGREGATE PER SHOW
    # -------------------------
    agg = (
        df.groupby("show_title", as_index=False)
        .agg(
            longevity=("cumulative_weeks_in_top_10", "max"),
            hype=("score", "sum"),
        )
    )

    if agg.empty:
        return None

    # -------------------------
    # THRESHOLDS (dynamic)
    # -------------------------
    lon_thr = agg["longevity"].median()
    hype_thr = agg["hype"].median()

    # -------------------------
    # SEGMENTATION
    # -------------------------
    def classify(row):
        if row["longevity"] >= lon_thr and row["hype"] >= hype_thr:
            return "Balanced Hit"
        elif row["longevity"] < lon_thr and row["hype"] >= hype_thr:
            return "Flash Hit"
        else:
            return "Evergreen"

    agg["segment"] = agg.apply(classify, axis=1)

    # -------------------------
    # LIMIT → TOP 3 PER SEGMENT
    # -------------------------
    agg = (
        agg.sort_values("hype", ascending=False)
        .groupby("segment")
        .head(3)
    )

    # -------------------------
    # SCATTER
    # -------------------------
    fig = px.scatter(
        agg,
        x="longevity",
        y="hype",
        color="segment",
        text="show_title",
        size="hype",
        size_max=25,
        color_discrete_map={
            "Evergreen": "#457B9D",              # blue
            "Balanced Hit": PAGE_COLORS["yellow"],
            "Flash Hit": PAGE_COLORS["orange"],
        },
    )

    fig.update_traces(textposition="top center")

    fig.update_layout(
        paper_bgcolor=PAGE_COLORS["card"],
        plot_bgcolor=PAGE_COLORS["card"],
        font=dict(color=PAGE_COLORS["text"], family="Segoe UI"),
        xaxis=dict(title="Show Longevity (Weeks in Top 10)", showgrid=False),
        yaxis=dict(title="Hype / Performance Score", showgrid=False),
        legend_title="",
        height=500,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig