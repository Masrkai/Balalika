import csv
import time
import random

import requests
from rustysoup import BeautifulSoup
from src.scraper.header import make_headers

# Define the schema
FIELDS = [
    'job_title',
    'company_name',
    'location',
    'salary',
    'job_url',
    'posted_date',
    'description'
]

# Create a persistent session
session = requests.Session()
session.headers.update(make_headers())

BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

def fetch_listings(keywords, location, start=0):
    params = {
        "keywords": keywords,
        "location": location,
        "start": start,
    }

    # Adding a random delay to mimic human behavior
    time.sleep(random.uniform(1, 2))

    response = session.get(BASE_URL, params=params)

    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch: {response.status_code}")
        return None

def fetch_job_details(job_url):
    """
    Scrapes the job detail page for description and full salary info.
    """
    time.sleep(random.uniform(1, 2))  # Longer delay for detail pages
    try:
        response = session.get(job_url, timeout=10)
        if response.status_code != 200:
            return None, None

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Description
        description_element = soup.find('div', class_='show-more-less-html__markup')
        description = description_element.text.strip() if description_element else "N/A"
        
        # Salary (Detail page might have more accurate info)
        salary_element = soup.find('span', class_='job-details-salary-estimate__total-salary')
        salary = salary_element.text.strip() if salary_element else None
        
        return description, salary
    except Exception as e:
        print(f"Error fetching details: {e}")
        return None, None

def parse_listings(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    jobs = []

    listings = soup.find_all('div', class_='job-search-card')

    for job in listings:
        try:
            title = job.find('h3', class_='base-search-card__title').text.strip()
            company = job.find('h4', class_='base-search-card__subtitle').text.strip()
            location = job.find('span', class_='job-search-card__location').text.strip()
            url = job.find('a', class_='base-card__full-link')['href']

            salary = job.find('span', class_='job-search-card__salary-info')
            salary = salary.text.strip() if salary else "N/A"

            posted_date = job.find('time', class_='job-search-card__listdate')
            posted_date = posted_date['datetime'] if posted_date else "N/A"

            jobs.append({
                'job_title': title,
                'company_name': company,
                'location': location,
                'salary': salary,
                'job_url': url,
                'posted_date': posted_date,
                'description': None # Placeholder for detail scraping
            })
        except AttributeError:
            continue

    return jobs

# The scraper logic now just returns the data
def fetch_and_parse_batch(keywords, location, start):
    html = fetch_listings(keywords, location, start=start)
    if not html:
        return None, start
    
    jobs = parse_listings(html)
    return jobs, start + len(jobs)
