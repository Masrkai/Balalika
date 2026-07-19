import csv
import time
import random
import re

import requests
from rustysoup import BeautifulSoup
from src.scraper.header import make_headers

# Define the schema
FIELDS = [
    'country',
    'category',
    'keyword',
    'job_title',
    'company_name',
    'location',
    'salary',
    'job_url',
    'posted_date',
    'description'
]

MAX_RETRIES = 3
BASE_RETRY_DELAY = 2

# Create a persistent session
session = requests.Session()
session.headers.update(make_headers())

BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

# minimal: flat retry/backoff; per-(keywords,location) session is fine at research scale
def _request(url, params=None, timeout=10):
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            time.sleep(random.uniform(1, 2))
            response = session.get(url, params=params, timeout=timeout)
            if response.status_code == 429:
                delay = BASE_RETRY_DELAY * (2 ** (attempt - 1))
                print(f"429 rate limited, backing off {delay}s (attempt {attempt}/{MAX_RETRIES})")
                time.sleep(delay)
                last_err = f"429 after {attempt} retries"
                continue
            if response.status_code == 200:
                return response.text
            print(f"Failed to fetch {url}: {response.status_code}")
            return None
        except Exception as e:
            last_err = str(e)
            delay = BASE_RETRY_DELAY * (2 ** (attempt - 1))
            print(f"Request error (attempt {attempt}/{MAX_RETRIES}): {e}; retry in {delay}s")
            time.sleep(delay)
    print(f"Giving up after {MAX_RETRIES} retries: {last_err}")
    return None

def fetch_listings(keywords, location, start=0):
    params = {
        "keywords": keywords,
        "location": location,
        "start": start,
    }
    return _request(BASE_URL, params=params)

def fetch_job_details(job_url):
    """
    Scrapes the job detail page for description and full salary info.
    Returns (description, salary_dict). On failure returns (None, None).
    """
    html = _request(job_url, timeout=10)
    if html is None:
        return None, None

    soup = BeautifulSoup(html, 'html.parser')

    # Description
    description_element = soup.find('div', class_='show-more-less-html__markup')
    description = description_element.text.strip() if description_element else None

    # Salary (Detail page might have more accurate info)
    salary_element = soup.find('span', class_='job-details-salary-estimate__total-salary')
    salary = parse_salary(salary_element.text.strip()) if salary_element else None

    return description, salary

def parse_salary(salary_text):
    """
    Parse a LinkedIn salary string like "$80,000 - $120,000" into
    (min_amount, max_amount, currency). Returns None when unparseable.
    Mirrors JobSpy's currency_parser intent without the dependency.
    """
    if not salary_text:
        return None
    parts = [p.strip() for p in salary_text.split('-')]
    if len(parts) < 2:
        return None
    # minimal: handles "$X - $Y" / "€X - €Y"; no interval/yearly conversion yet
    CURRENCY_SYMBOLS = {'$': 'USD', '€': 'EUR', '£': 'GBP', '₹': 'INR'}

    def _num(token):
        m = re.search(r'[\d,]+', token)
        return int(m.group().replace(',', '')) if m else None

    min_amount = _num(parts[0])
    max_amount = _num(parts[1])
    if min_amount is None or max_amount is None:
        return None
    symbol = parts[0][0] if parts[0] else ''
    currency = CURRENCY_SYMBOLS.get(symbol, 'USD')
    return {'min_amount': min_amount, 'max_amount': max_amount, 'currency': currency}

def parse_listings(html_content, country=None, category=None, keyword=None):
    soup = BeautifulSoup(html_content, 'html.parser')
    jobs = []

    listings = soup.find_all('div', class_='job-search-card')

    for job in listings:
        try:
            title = job.find('h3', class_='base-search-card__title').text.strip()
            company = job.find('h4', class_='base-search-card__subtitle').text.strip()
            location = job.find('span', class_='job-search-card__location').text.strip()
            url = job.find('a', class_='base-card__full-link')['href']

            salary_element = job.find('span', class_='job-search-card__salary-info')
            salary = parse_salary(salary_element.text.strip()) if salary_element else None

            posted_date = job.find('time', class_='job-search-card__listdate')
            posted_date = posted_date['datetime'] if posted_date else None

            jobs.append({
                'country': country,
                'category': category,
                'keyword': keyword,
                'job_title': title,
                'company_name': company,
                'location': location,
                'salary': salary,
                'job_url': url,
                'posted_date': posted_date,
                'description': None  # Placeholder for detail scraping
            })
        except AttributeError:
            continue

    return jobs

# The scraper logic now just returns the data. Always returns (list, int).
def fetch_and_parse_batch(keywords, location, start):
    html = fetch_listings(keywords, location, start=start)
    if not html:
        return [], start

    jobs = parse_listings(html)
    return jobs, start + len(jobs)
