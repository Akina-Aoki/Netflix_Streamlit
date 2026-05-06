# ---------------------------------------------------------
# helpers.py
# Syfte: Hjälpfunktioner för fil-läsning och datainsamling
# ---------------------------------------------------------

from netflix.utils.constants import DATA_PATH  # sökvägen till data-mappen
import pandas as pd
import streamlit as st


def read_textfile(path):
    """Funktion för att läsa in vilken fil som helst"""
    with open(path) as file:

        return file.read()


def read_css(path):
    """Funktionen läser in CSS och injicerar i streamlit"""
    css = read_textfile(path)

    st.write(
        f"<style>{css}</style>",  # slår in CSS i HTML style-tagg
        unsafe_allow_html=True,  # Krävs - Streamlit blockerar annars HTML
    )


@st.cache_data
def get_weekly_df():
    """Läser in global_weekly Excel-data"""
    return pd.read_excel(DATA_PATH / "global_weekly.xlsx")


@st.cache_data
def get_alltime_df():
    """Läser in global_alltime Excel-data"""
    return pd.read_excel(DATA_PATH / "global_alltime.xlsx")


@st.cache_data
def get_global_df():
    """Läser in normaliserad global data"""
    return pd.read_csv(DATA_PATH / "FactGlobal_Final.csv")


@st.cache_data
def get_country_df():
    """Läser in normaliserad country-data"""
    return pd.read_csv(DATA_PATH / "FactCountry_Final.csv")


@st.cache_data
def get_metadata_df():
    """Läser in metadata med posters, trailers o beskrivningar"""
    return pd.read_csv(DATA_PATH / "DimMetaData_Final.csv")

def show_banner():
    from netflix.utils.constants import IMAGE_PATH
    st.image(str(IMAGE_PATH / "Logga_Streamly.png"), width=200)
    st.caption("Global Netflix viewing statistics")



# --- For Russias KPIs using unique "shows" (film and series) --
# Adding filters with 3 options
def get_russia_kpi(category="All"):

# Loading the data and filtering only Russia
    df = get_country_df()
    df["week"] = pd.to_datetime(df["week"])
    russia = df[df["country_name"] == "Russia"]

    # Filter by category
    if category != "All":
        russia = russia[russia["category"] == category]


# Counting unique shows at beginning and ends of 2021 and 2022 (march)
# Filtering now month (July) and extracting unique value
    start_2021 = russia[russia["month"] == 7]["show_title"].nunique()
    end_2021   = russia[russia["month"] == 12]["show_title"].nunique()
    start_2022 = russia[(russia["year"] == 2022) & (russia["month"] == 1)]["show_title"].nunique()
    end_2022   = russia[(russia["year"] == 2022) & (russia["month"] == 2)]["show_title"].nunique()

# Calculating the difference | function only used here
    def cal_diff(start, end):
        return end - start, ((end - start) / start) * 100
    
    diff_2021, prct_2021 = cal_diff(start_2021, end_2021)
    diff_2022, prct_2022 = cal_diff(start_2022, end_2022)
    both_years, both_years_prct  = cal_diff(start_2021, end_2022)

# returning a dict
    return {
    "start_2021":  start_2021,
    "end_2021":    end_2021,
    "diff_2021": diff_2021,
    "pct_2021":    prct_2021,
    "start_2022":  start_2022,
    "end_2022":    end_2022,
    "diff_2022": diff_2022,
    "pct_2022":    prct_2022,
    "both_years":     both_years_prct,
    "both_years_pct": both_years_prct,
}

# --- separation band between sections ---
def separation_band(title):
    st.markdown(f"## {title}")









