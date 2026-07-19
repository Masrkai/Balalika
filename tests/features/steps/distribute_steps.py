import sys
from pathlib import Path

from behave import given, when, then
from src.data.units import build_units, split_units, filter_units
from src.data.storage import append_to_jsonl_shard
import polars as pl

CATS = Path(__file__).resolve().parent.parent.parent.parent / "Data" / "CS_Jobs.json"


@given('the full unit matrix for Germany and Canada')
def step_given_matrix(context):
    context.units = build_units(CATS, countries_spec="Germany,Canada")


@when('I split it across {of} devices by mod')
def step_when_split(context, of):
    of = int(of)
    context.slices = [split_units(context.units, d, of) for d in range(1, of + 1)]


@then('every unit belongs to exactly one device')
def step_then_disjoint(context):
    seen = set()
    for s in context.slices:
        for u in s:
            assert u.id not in seen, f"overlap: {u.id}"
            seen.add(u.id)


@then('the union of all devices equals the full matrix')
def step_then_complete(context):
    seen = set()
    for s in context.slices:
        for u in s:
            seen.add(u.id)
    assert len(seen) == len(context.units)


@when('I filter to country {country} and category {category}')
def step_when_filter(context, country, category):
    context.filtered = filter_units(context.units, countries_spec=country, categories_spec=category)


@then('all selected units are in {country} and {category}')
def step_then_filtered(context, country, category):
    for u in context.filtered:
        assert u.country == country
        assert u.category == category


@given('two device shards with one overlapping job url')
def step_given_shards(context):
    context.data_dir = Path(context.fixture).parent.parent  # tests/fixtures -> tests -> (no shards here)
    # Use a temp dir via behave tmp; create under features dir shards.
    import tempfile
    context.data_dir = Path(tempfile.mkdtemp())
    base = [{
        "country": "Germany", "category": "Software Engineering", "keyword": "Software Engineer",
        "job_title": "SWE", "company_name": "A", "location": "Berlin", "salary": None,
        "job_url": "https://www.linkedin.com/jobs/view/1", "posted_date": None, "description": None,
    }, {
        "country": "Canada", "category": "Data Science & AI", "keyword": "Data Scientist",
        "job_title": "DS", "company_name": "B", "location": "Toronto", "salary": None,
        "job_url": "https://www.linkedin.com/jobs/view/2", "posted_date": None, "description": None,
    }]
    append_to_jsonl_shard(base, context.data_dir, "dev1")
    append_to_jsonl_shard([dict(base[0]), base[1]], context.data_dir, "dev2")
    context.expected_unique = 2


@when('I merge the shards')
def step_when_merge(context):
    from src.merge import main as merge_main
    sys.argv = ["merge", "--data-dir", str(context.data_dir)]
    merge_main()
    context.merged = pl.read_ndjson(context.data_dir / "jobs.jsonl")


@then('the canonical output has no duplicate job urls')
def step_then_no_dupes(context):
    assert context.merged["job_url"].n_unique() == context.merged.height


@then('the row count equals the number of unique job urls')
def step_then_count(context):
    assert context.merged.height == context.expected_unique


@given('a merged canonical output')
def step_given_merged(context):
    step_given_shards(context)
    step_when_merge(context)
    context.first_text = (context.data_dir / "jobs.jsonl").read_text()


@when('I merge again')
def step_when_merge_again(context):
    step_when_merge(context)


@then('the output is unchanged')
def step_then_unchanged(context):
    assert (context.data_dir / "jobs.jsonl").read_text() == context.first_text
