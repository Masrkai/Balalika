import pytest
from src.scraper.scrape import parse_listings
import os

@pytest.fixture
def sample_html():
    with open("debug_response.html", "r", encoding="utf-8") as f:
        return f.read()

def test_parse_listings_structure(sample_html):
    jobs = parse_listings(sample_html)
    
    assert len(jobs) > 0, "No jobs parsed!"
    
    for job in jobs:
        assert isinstance(job['job_title'], str)
        assert isinstance(job['company_name'], str)
        assert isinstance(job['job_url'], str)
        assert job['job_title'] != "N/A"
        assert job['company_name'] != "N/A"

def test_parse_listings_handles_malformed_html():
    malformed_html = "<div><h3 class='base-search-card__title'>Missing stuff</h3></div>"
    jobs = parse_listings(malformed_html)
    # Should not crash, just return empty list
    assert jobs == []

def test_parse_listings_missing_optional_fields():
    # Simulate a job with missing salary and date
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
    assert jobs[0]['salary'] == 'N/A'
    assert jobs[0]['posted_date'] == 'N/A'
