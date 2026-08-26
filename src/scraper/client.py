import time
import random
import requests
from requests.adapters import HTTPAdapter
from src.scraper.header import make_headers

MAX_RETRIES = 3
BASE_RETRY_DELAY = 2
BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

# Create a persistent session with thread-safe connection pooling adapter
session = requests.Session()
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20)
session.mount("https://", adapter)
session.mount("http://", adapter)
session.headers.update(make_headers())

def _request(url, params=None, timeout=10):
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            time.sleep(random.uniform(1, 2))
            response = session.get(url, params=params, timeout=timeout)
            
            # Handle rate limiting (429) or server errors (500-504)
            if response.status_code == 429 or (500 <= response.status_code <= 504):
                delay = BASE_RETRY_DELAY * (2 ** (attempt - 1))
                print(f"HTTP {response.status_code}, backing off {delay}s (attempt {attempt}/{MAX_RETRIES})")
                time.sleep(delay)
                last_err = f"HTTP {response.status_code} after {attempt} retries"
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
