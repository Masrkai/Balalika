import pytest
from pathlib import Path

from src.scraper.scrape import parse_listings, parse_salary, fetch_and_parse_batch
from src.scraper.checkpoint import get_checkpoint, update_checkpoint, reset_checkpoint
from src.data.storage import append_to_csv, append_to_jsonl

FIXTURE = Path(__file__).parent / "fixtures" / "debug_response.html.example"


@pytest.fixture
def sample_html():
    return FIXTURE.read_text(encoding="utf-8")


def test_parse_listings_structure(sample_html):
    jobs = parse_listings(sample_html)

    assert len(jobs) > 0, "No jobs parsed!"

    for job in jobs:
        assert isinstance(job['job_title'], str)
        assert isinstance(job['company_name'], str)
        assert isinstance(job['job_url'], str)
        assert job['job_title'] != "N/A"
        assert job['company_name'] != "N/A"
        # salary is now a dict or None, never the string "N/A"
        assert job['salary'] is None or isinstance(job['salary'], dict)
        assert job['posted_date'] is None or isinstance(job['posted_date'], str)


def test_parse_listings_handles_malformed_html():
    malformed_html = "<div><h3 class='base-search-card__title'>Missing stuff</h3></div>"
    jobs = parse_listings(malformed_html)
    # Should not crash, just return empty list
    assert jobs == []


def test_parse_listings_missing_optional_fields():
    html = """
    <div class='job-search-card'>
        <h3 class='base-search-card__title'>Title</h3>
        <h4 class='base-search-card__subtitle'>Company</h4>
        <span class='job-search-card__location'>Loc</span>
        <a class='base-card__full-link' href='http://test.com'></a>
    </div>
    """
    jobs = parse_listings(html)
    assert len(jobs) == 1
    assert jobs[0]['salary'] is None
    assert jobs[0]['posted_date'] is None


def test_parse_salary_ranges():
    parsed = parse_salary("$80,000 - $120,000")
    assert parsed == {'min_amount': 80000, 'max_amount': 120000, 'currency': 'USD'}

    assert parse_salary("Not a salary") is None
    assert parse_salary("") is None
    assert parse_salary(None) is None


def test_fetch_and_parse_batch_contract():
    # On fetch failure the function must return ([], int), never None.
    jobs, next_start = fetch_and_parse_batch("software engineer", "Nowhere, ZZ", start=0)
    assert isinstance(jobs, list)
    assert isinstance(next_start, int)


def test_checkpoint_roundtrip(tmp_path):
    cp = tmp_path / "checkpoint.json"
    assert get_checkpoint(cp) == 0
    update_checkpoint(cp, 40)
    assert get_checkpoint(cp) == 40
    reset_checkpoint(cp)
    assert get_checkpoint(cp) == 0


def test_storage_csv_append_idempotent(tmp_path):
    path = tmp_path / "jobs.csv"
    rows = [{'job_title': 'A', 'company_name': 'C', 'location': 'L',
             'salary': None, 'job_url': 'u1', 'posted_date': None, 'description': None}]
    append_to_csv(rows, path)
    append_to_csv(rows, path)
    import polars as pl
    df = pl.read_csv(path)
    # header written once; two appends => two data rows
    assert df.height == 2
    assert df.columns == ['job_title', 'company_name', 'location', 'salary', 'job_url', 'posted_date', 'description']


def test_storage_jsonl_append(tmp_path):
    path = tmp_path / "jobs.jsonl"
    rows = [{'job_title': 'A', 'job_url': 'u1'}]
    append_to_jsonl(rows, path)
    append_to_jsonl(rows, path)
    lines = path.read_text().strip().splitlines()
    assert len(lines) == 2
