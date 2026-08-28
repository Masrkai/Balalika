# Balalika Project Comprehensive Task List

## Core Configuration & Analytics
- [x] Create `Data/scraping_config.toml` to define target locations for the categories
  - [x] Refactor `src/main.py` to loop through configurations (locations/categories) instead of hardcoding them.
- [x] Ensure checkpointing logic handles multi-configuration scraping (per location/category).
  - [x] Add regression tests for the multi-configuration scraping flow.
  - [x] Allow distributed scraping
- [x] Implement data analysis scripts using `polars` in `scripts/analyze_jobs.py` to generate statistics from `Data/jobs.csv` and `Data/jobs.jsonl`.

## Performance Optimizations & Resilience
- [x] Analyze and evaluate parallelizing unit processing across device cores
- [x] Make request delays and jitter configurable
- [x] Make detail-fetching thread pool size (`max_workers`) configurable
- [x] Optimize checkpoint I/O and evaluation of batching
- [x] Evaluate asynchronous I/O (`httpx` / `asyncio`) transition
- [x] Evaluate proxy pool support for IP rate-limiting resilience

## Code Quality & Architecture
- [x] Standardize type hints across modules (PEP 604 union syntax `str | None`)
- [x] Narrow exception catching (replace broad `Exception` catches with specific exception types)
- [x] Centralize magic numbers (retry counts, delays, timeouts, pool sizes)
- [x] Review redundant facade module (`src/scraper/scrape.py`)

## Documentation & Testing
- [x] Add module-level docstrings to Python files in `src/`
- [x] Create data schema documentation (`Docs/data_schemas.md` for schemas, checkpoints, outputs)
- [x] Complete macroeconomic comparison guides (`GDP_Comparison.md`)
- [x] Create documentation index / enhance README discoverability
- [x] Document BDD test suite (`tests/features/` and step definitions)

## Versioning & Release Management
- [x] Implement semantic version module (`src/version.py`)
- [x] Add `--version` CLI flag in `src/main.py`
- [x] Establish `CHANGELOG.md` adhering to Keep a Changelog standards
