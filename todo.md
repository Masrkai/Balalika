# Todo List

- [ ] Create `Data/scraping_config.json` to define target locations for the categories
  - [ ] Refactor `src/main.py` to loop through configurations (locations/categories) instead of hardcoding them.
- [ ] Ensure checkpointing logic handles multi-configuration scraping (per location/category).
  - [ ] Add regression tests for the multi-configuration scraping flow.
  - [ ] Allow distributed scraping
- [ ] Implement data analysis scripts using `polars` in `scripts/` to generate statistics from `Data/jobs.csv` and `Data/jobs.jsonl`.
