# LinkedIn Job Market Analysis

A lightweight scraper that collects CS job listings from LinkedIn across 9 countries and 9 specializations, then enriches each listing with salary, description, and job criteria data.

Built as a university Data Mining project.

---

## What it does

Two-phase pipeline:

```
Phase 1: src/Scraper.py
  Reads job titles from Data/CS_Job_Titles_Categorized.json
  Hits LinkedIn's guest search API (async, aiohttp)
  Writes CSVs to Data/Scraped/{Country}/{Category}/*.csv

Phase 2: src/batch.py
  Reads each CSV, fetches individual job pages (sync, requests)
  Extracts salary, description, criteria
  Writes enriched JSONs to Data/Scraped/{Country}/{Category}/*.json
```

---

## Setup

### NixOS

```bash
nix-shell
```

This creates a `.venv` with Python 3.13 and installs dependencies via `uv`.

### Non-NixOS

```bash
pip install -r requirements.txt
```

> Note: `requirements.txt` lists `random` and `asyncio` which are stdlib — ignore those lines.

### Environment variables

```bash
export LINKEDIN_EMAIL="dummy@example.com"
export LINKEDIN_PASSWORD="secure_password"
export BRAVE_PATH="/path/to/brave"  # optional, defaults to Chrome
```

---

## Usage

### Phase 1 — Scrape search results

```bash
cd src
python Scraper.py
```

Reads `Data/CS_Job_Titles_Categorized.json` for job categories and titles. Scrapes LinkedIn's guest search API for each job title across all 9 countries. Outputs CSVs:

```
Data/Scraped/{Country}/{Category}/{Category}.csv
```

### Phase 2 — Enrich individual job pages

```bash
python src/batch.py
```

Runs from the project root. Processes all CSVs under `Data/Scraped/`. Fetches each job's LinkedIn page and extracts salary, description, and criteria. Outputs JSONs alongside the CSVs.

Progress checkpoints every 20 jobs — safe to Ctrl+C and resume.

### Phase 2 (selective) — Enrich specific countries/categories

```bash
python src/split.py <countries> <categories>
```

Examples:

```bash
python src/split.py Brazil "Data Science & AI"
python src/split.py "Brazil,Canada" "Data Science & AI,Cybersecurity"
python src/split.py all "Meme Jobs"        # one category, all countries
python src/split.py Brazil all              # all categories in Brazil
```

---

## Countries scraped

| Tier | Countries |
|---|---|
| 1st class | United States, Germany, Canada |
| 2nd class | Poland, Finland, Brazil |
| 3rd class | Egypt, Madagascar, Morocco |

## Categories

Software Engineering, Data Science & AI, Cybersecurity, Cloud & Network Engineering, DevOps & SRE, Robotics & Automation, Enterprise IT & Systems Administration, Bioinformatics & Computational Biology, Meme Jobs.

---

## Rate limiting

- 2–5s random jitter between requests
- 10–30s between batches of 20–100 jobs
- Exponential backoff on HTTP 429 (up to 3 retries)
- Auto-increases batch delay after 3 consecutive rate limits

This is a small-scale research scraper, not designed for high-volume use.

---

## Running tests

```bash
nix-shell --run "pytest tests/ -v"
```

---

## Project structure

```
├── Data/
│   ├── CS_Job_Titles_Categorized.json   # input: job categories + titles
│   ├── Scraped/                          # output: CSVs and JSONs per country/category
│   └── Proccessed_data/                  # processed outputs (note: typo is intentional)
│
├── src/
│   ├── Scraper.py                        # Phase 1: scrape search results
│   ├── batch.py                          # Phase 2: enrich job URLs
│   ├── split.py                          # Phase 2 CLI: selective enrichment
│   ├── extract_links.py                  # Utility: extract URLs from CSVs
│   ├── helpers/
│   │   ├── LinkedinAPI2.py              # Async scraper (aiohttp)
│   │   ├── UserAgent.py                 # Random user agent generation
│   │   ├── normalize.py                 # LinkedIn URL normalization
│   │   ├── resolve_path.py              # Path resolution utility
│   │   ├── makefolder.py                # Dir/file/CSV helpers
│   │   └── data_fetcher_from_Json_DS.py # JSON data loading
│   └── URL/
│       ├── salary.py                    # Salary extraction from HTML
│       ├── description.py               # Description extraction from HTML
│       └── extract_criteria.py          # Job criteria extraction from HTML
│
├── tests/                               # pytest test suite (84 tests)
├── requirements.txt
├── shell.nix                            # Nix dev environment
└── AGENTS.md                            # Agent instructions
```
