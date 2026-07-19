from typing import List

# Vendored subset of JobSpy's Country enum (no import to avoid coupling).
# Each entry: canonical display name used as LinkedIn location string.
# Default-active set mirrors README's 9 priority countries; FULL adds the rest.
DEFAULT_COUNTRIES: List[str] = [
    "United States",
    "Germany",
    "Canada",
    "Poland",
    "Finland",
    "Brazil",
    "Egypt",
    "Madagascar",
    "Morocco",
]

FULL_COUNTRIES: List[str] = sorted(set(DEFAULT_COUNTRIES + [
    "Argentina", "Australia", "Austria", "Bahrain", "Bangladesh", "Belgium",
    "Bulgaria", "Chile", "China", "Colombia", "Costa Rica", "Croatia", "Cyprus",
    "Czech Republic", "Denmark", "Ecuador", "Estonia", "France", "Greece",
    "Hong Kong", "Hungary", "India", "Indonesia", "Ireland", "Israel", "Italy",
    "Japan", "Kuwait", "Latvia", "Lithuania", "Luxembourg", "Malaysia", "Malta",
    "Mexico", "Netherlands", "New Zealand", "Nigeria", "Norway", "Oman", "Pakistan",
    "Panama", "Peru", "Philippines", "Portugal", "Qatar", "Romania", "Saudi Arabia",
    "Singapore", "Slovakia", "Slovenia", "South Africa", "South Korea", "Spain",
    "Sweden", "Switzerland", "Taiwan", "Thailand", "Turkey", "Ukraine",
    "United Arab Emirates", "United Kingdom", "Uruguay", "Venezuela", "Vietnam",
]))

# minimal: plain list; if LinkedIn ever needs ISO/subdomain mapping, add a dict here
def normalize_country(name: str) -> str:
    """Return the canonical LinkedIn location string for a country name (case-insensitive)."""
    if not name:
        raise ValueError("country name is empty")
    lowered = name.strip().lower()
    for known in FULL_COUNTRIES:
        if known.lower() == lowered:
            return known
    raise ValueError(f"Unknown country: {name!r}. Known: {', '.join(FULL_COUNTRIES)}")


def resolve_countries(spec: str | None, full: bool = False) -> List[str]:
    """Resolve a comma-separated country spec, or return the default/full set if None."""
    if spec:
        return [normalize_country(c) for c in spec.split(",") if c.strip()]
    return list(FULL_COUNTRIES) if full else list(DEFAULT_COUNTRIES)
