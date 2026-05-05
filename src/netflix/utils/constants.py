# --------------------------------------------------------------------
# constants.py
# Syfte: Definiera ALLA sökvägar som används i projektet
# Best Practice: "Single responsibility, denna filen gör en sak,
# den hanterar sökvägar.
# ---------------------------------------------------------------------

from pathlib import Path

# Bassökväg
# Path(__file__) = absolut sökväg till denna fil (constants.py)
# .parents[0]   = utils/          (en nivå upp)
# .parents[1]   = src/netflix/    BASE_PATH (två nivåer upp)
BASE_PATH = Path(__file__).parents[1]

# Assets
# Allt statiskt innehåll samlas under assets/
ASSETS_PATH = BASE_PATH / "assets"

# Undermappar till assets
IMAGE_PATH = ASSETS_PATH / "image"  # logtyper, bilder
STYLES_PATH = ASSETS_PATH / "style"  # CSS-filer
MARKDOWN_PATH = ASSETS_PATH / "markdown"  # Textsidor som .md-filer
DATA_PATH = (
    ASSETS_PATH / "data"
)  # Excel-filerna, 2026-02-08_global_alltime.xlsx, 2026-02-08_global_weekly.xlsx

# Komponenter
COMPONENTS_PATH = BASE_PATH / "components"
