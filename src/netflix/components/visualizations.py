import streamlit as st
import matplotlib.pyplot as plt
from netflix.utils.helpers import get_df
from netflix.utils.constants import DATA_PATH
RED_1 = "#E50914"
GRAY_3 = "#888888"


df = get_df() 

russia_rows = (
    df[df["country_name"] == "Russia"]
    .groupby(df[df["country_name"] == "Russia"]["week"].dt.year)["country_name"]
    .count()
    .reindex([2021, 2022, 2023, 2024, 2025], fill_value=0)
)
russia_2022 = russia_rows[russia_rows > 0]

world_df = df[df["country_name"] != "Russia"]
world_yearly = (
    world_df.groupby(world_df["week"].dt.year)["country_name"].count()
    / world_df["country_name"].nunique()
)
world_continue = world_yearly[world_yearly.index <= 2025]


def russia_line_chart():
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.spines[["top", "right"]].set_visible(False)

    ax.set_xlabel("YEAR")
    ax.set_ylabel("# of rows")


    ax.plot(range(len(russia_2022)), russia_2022.values, linewidth=2, linestyle="--", zorder=2)
    ax.plot(range(len(world_continue)), world_continue.values, linewidth=2, linestyle="--", zorder=2, color=GRAY_3)

    ax.scatter(range(len(russia_2022)), russia_2022.values, s=80, zorder=3)
    ax.scatter([1], [russia_2022.iloc[1]], s=120, zorder=4, color=RED_1)

    ax.set_xticks(range(len(russia_rows)))
    ax.set_xticklabels(russia_rows.index, rotation=0)

    ax.set_title(
        "Netflix data for Russia ends abruptly in March 2022"
        "\nfollowing the invasion of Ukraine",
        pad=22, loc="left",
    )

    ax.annotate(
        "Start of Russian aggression\nin Ukraine",
        xy=(1, russia_2022.iloc[1]),
        xytext=(1.8, russia_2022.iloc[1] * 2.5),
        arrowprops=dict(arrowstyle="->", color=RED_1, shrinkB=8),
        fontsize=10, ha="center", color=RED_1
    )

    ax.text(4.1, world_continue.iloc[-1], "Rest of world (avg)", fontsize=9, va="center")
    ax.text(1.1, russia_2022.iloc[-1], "Russia", fontsize=9, va="center")

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)