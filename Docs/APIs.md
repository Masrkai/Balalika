# APIs

## LinkedIn's "Guest" API (The Direct Scraping Method)

LinkedIn uses a public-facing endpoint to serve job listings to visitors who aren't logged in.
This is the same data you see when you search for jobs on Google and land on a LinkedIn "guest" page.

- The Endpoint: <https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search>
- How it works: You can send GET requests with parameters like keywords, location, and start (for pagination).
- Pros: Completely free.
- Cons: Very high risk of being blocked. LinkedIn uses aggressive rate-limiting, IP blacklisting, and browser fingerprinting. You would likely need rotating proxies and custom headers to use this at scale.

### using that API

```
GET https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search
```

| Parameter | Example | Notes |
|---|---|---|
| `keywords` | `keywords=software+engineer` | URL-encoded search term |
| `location` | `location=New+York%2C+United+States` | Free-text location string |
| `geoId` | `geoId=103644278` | LinkedIn's internal ID for a location (more reliable than `location`) |
| `start` | `start=25` | Pagination offset, increments by 25 (one page = 25 jobs) |
| `f_TPR` | `f_TPR=r86400` | Time posted filter (r86400 = past 24h, r604800 = past week) |
| `f_E` | `f_E=2` | Experience level (1=Internship, 2=Entry, 3=Associate, 4=Mid-Senior, 5=Director, 6=Executive) |
| `f_JT` | `f_JT=F` | Job type (F=Full-time, P=Part-time, C=Contract, etc.) |
| `f_WT` | `f_WT=2` | Workplace type (1=On-site, 2=Remote, 3=Hybrid) |

Example combined request:

```
https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=data+analyst&location=Austin%2C+Texas&f_TPR=r604800&start=0
```

The response is server-rendered HTML fragments (not JSON), so consuming it means parsing HTML (e.g., BeautifulSoup) rather than hitting a clean REST API.

## Where I'd steer you instead

If you want job listing data for a real project, options that don't involve adversarial scraping:

- **LinkedIn's official Talent Solutions / Jobs API** — requires a partnership agreement, but it's sanctioned and stable.
- **Aggregators with legitimate APIs**: Indeed's API (partner program), Adzuna API, Jooble API, USAJobs API (public sector), or The Muse API — all have proper terms of service for programmatic access.
- **RSS/public job boards** that explicitly allow automated access.

Happy to help you build a scraper against any of those, or help you parse/structure job data you already have. Want help with one of those instead?

## Indirect API via Google Jobs (SERP APIs)

Google indexes almost all LinkedIn job postings. Instead of scraping LinkedIn directly, you can use a Search Engine Results Page (SERP) API to search for jobs on Google and filter for LinkedIn results.

- How to do it: Use a service like SerpApi or HasData to query Google Jobs.
- Example Query: site:linkedin.com/jobs/view "Software Engineer" in New York
- Pros: More stable than scraping LinkedIn directly because Google is easier to "search" programmatically via API.
- Cons: You might not get 100% of the listings, and the data structure depends on how Google displays it.
