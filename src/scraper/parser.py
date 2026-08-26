import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from rustysoup import BeautifulSoup
from pydantic import ValidationError
from src.scraper.client import _request, BASE_URL
from src.scraper.models import JobRecord
from src.scraper.utils import parse_salary, normalize_url

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

BLOCK_INDICATORS = ('captcha', 'security verification', 'challenge', 'one more step')

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

            raw_job = {
                'country': country,
                'category': category,
                'keyword': keyword,
                'job_title': title,
                'company_name': company,
                'location': location,
                'salary': salary,
                'job_url': normalize_url(url),
                'posted_date': posted_date,
                'description': None
            }
            validated = JobRecord(**raw_job)
            jobs.append(validated.model_dump())
        except (AttributeError, ValidationError):
            continue

    return jobs

def fetch_and_parse_batch(keywords, location, start, max_block_retries=2):
    """
    Fetches and parses a batch of listings. Detects blocking/captcha pages
    and backs off/retries rather than falsely terminating pagination.
    """
    for attempt in range(1, max_block_retries + 1):
        html = fetch_listings(keywords, location, start=start)
        if not html:
            return [], start

        # Check for block/captcha indicators in response HTML
        lower_html = html.lower()
        if any(indicator in lower_html for indicator in BLOCK_INDICATORS):
            delay = 5 * attempt
            print(f"[Block Detected] Security/captcha page encountered at start={start}. Backing off {delay}s (attempt {attempt}/{max_block_retries})...")
            time.sleep(delay)
            continue

        jobs = parse_listings(html)
        return jobs, start + len(jobs)

    return [], start

def fetch_job_details_batch(jobs, max_workers=5):
    """
    Fetches job details concurrently for a list of job dicts using a ThreadPoolExecutor.
    """
    def _fetch_one(job):
        url = job.get("job_url")
        if not url:
            return job
        desc, sal = fetch_job_details(url)
        if desc:
            job["description"] = desc
        if sal:
            job["salary"] = sal
        return job

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_fetch_one, job): job for job in jobs}
        updated_jobs = []
        for future in as_completed(futures):
            try:
                updated_jobs.append(future.result())
            except Exception:
                updated_jobs.append(futures[future])
    return updated_jobs
