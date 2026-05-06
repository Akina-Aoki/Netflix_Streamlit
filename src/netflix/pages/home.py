"""Compatibility entrypoint for the integrated Country Insights home."""

from netflix.pages.country_insights import country_insights


def home() -> None:
    """Render the new integrated Country Insights home experience."""
    country_insights()

if __name__ == "__main__":
    home()