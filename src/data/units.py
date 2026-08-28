import json
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import List

from src.data.countries import resolve_countries


@dataclass(frozen=True)
class Unit:
    country: str
    category: str
    keyword: str

    @property
    def id(self) -> str:
        # Stable key for checkpoint/merge; no commas to keep JSON simple.
        return f"{self.country}|{self.category}|{self.keyword}"


def _load_categories(path: Path) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_units(
    categories_file: Path,
    countries_spec: str | None = None,
    full_countries: bool = False,
    config_file: Path | None = None,
) -> List[Unit]:
    """Build the (country, category, keyword) unit matrix, optionally guided by a TOML config file.

    Keyword = canonical job `name` only (alternatives ignored to bound volume).
    """
    categories = _load_categories(categories_file)
    units: List[Unit] = []

    if config_file and config_file.exists():
        with open(config_file, "rb") as f:
            config = tomllib.load(f)
        
        global_config = config.get("global", {})
        default_countries = global_config.get("default_countries", [])
        
        cfg_categories = config.get("categories", [])
        if cfg_categories:
            cat_dict = {cat["name"]: cat for cat in categories}
            for cfg_cat in cfg_categories:
                cat_name = cfg_cat.get("name")
                if cat_name not in cat_dict:
                    continue
                cat_data = cat_dict[cat_name]
                cfg_countries = cfg_cat.get("countries", default_countries)
                cfg_keywords = cfg_cat.get("keywords", [])
                
                for job in cat_data.get("jobs", []):
                    keyword = job["name"]
                    if cfg_keywords and keyword not in cfg_keywords:
                        continue
                    for country in cfg_countries:
                        units.append(Unit(country=country, category=cat_name, keyword=keyword))
            return units

    countries = resolve_countries(countries_spec, full=full_countries)
    for cat in categories:
        cat_name = cat["name"]
        for job in cat.get("jobs", []):
            keyword = job["name"]
            for country in countries:
                units.append(Unit(country=country, category=cat_name, keyword=keyword))
    return units


def split_units(units: List[Unit], device: int, of: int) -> List[Unit]:
    """Deterministic mod-split: device owns units where index % of == device-1."""
    if of < 1:
        raise ValueError("--of must be >= 1")
    if not (1 <= device <= of):
        raise ValueError("--device must be between 1 and --of")
    return [u for i, u in enumerate(units) if i % of == device - 1]


def filter_units(
    units: List[Unit],
    countries_spec: str | None = None,
    categories_spec: str | None = None,
) -> List[Unit]:
    """Explicit include filter by country/category names (case-insensitive contains)."""
    country_set = None
    if countries_spec:
        country_set = {c.strip().lower() for c in countries_spec.split(",") if c.strip()}
    cat_set = None
    if categories_spec:
        cat_set = {c.strip().lower() for c in categories_spec.split(",") if c.strip()}
    out = []
    for u in units:
        if country_set is not None and u.country.lower() not in country_set:
            continue
        if cat_set is not None and u.category.lower() not in cat_set:
            continue
        out.append(u)
    return out
