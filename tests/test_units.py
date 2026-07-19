from pathlib import Path

from src.data.units import build_units, split_units, filter_units, Unit
from src.data.countries import normalize_country, resolve_countries

CATS = Path(__file__).parent.parent / "Data" / "CS_Jobs.json"


def test_normalize_country():
    assert normalize_country("germany") == "Germany"
    assert normalize_country("United States") == "United States"


def test_resolve_countries_default():
    countries = resolve_countries(None)
    assert "Germany" in countries and "Canada" in countries
    assert len(countries) == 9


def test_build_units_shape():
    units = build_units(CATS, countries_spec="Germany,Canada")
    # Germany + Canada with only two categories present in CS_Jobs.json sample.
    # Build from full category file: count = countries * sum(jobs per category).
    cats = __import__("json").load(open(CATS))
    expected = 2 * sum(len(c["jobs"]) for c in cats)
    assert len(units) == expected
    assert all(isinstance(u, Unit) for u in units)
    # keyword = canonical job name only (no alternatives)
    cats = __import__("json").load(open(CATS))
    valid_names = {j["name"] for c in cats for j in c["jobs"]}
    assert all(u.keyword in valid_names for u in units)


def test_split_units_disjoint_and_complete():
    units = build_units(CATS, countries_spec="Germany,Canada")
    of = 4
    slices = [split_units(units, d, of) for d in range(1, of + 1)]
    # disjoint
    seen_ids = set()
    for s in slices:
        for u in s:
            assert u.id not in seen_ids, "overlap between devices"
            seen_ids.add(u.id)
    # complete
    assert len(seen_ids) == len(units)


def test_filter_units():
    units = build_units(CATS, countries_spec="Germany,Canada")
    filtered = filter_units(units, countries_spec="Germany",
                            categories_spec="Software Engineering")
    assert filtered
    assert all(u.country == "Germany" for u in filtered)
    assert all(u.category == "Software Engineering" for u in filtered)
