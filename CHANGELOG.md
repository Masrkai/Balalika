# Changelog

All notable changes to the Balalika project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to Semantic Versioning.

## [1.0.0] - 2026-08-28

### Added
- **Targeted Scraping Configuration**: Introduced `Data/scraping_config.toml` supporting flexible category-to-country and keyword mappings.
- **Configuration-Driven Runner**: Updated `src/main.py` and `src/data/units.py` to support TOML configuration loading with automatic fallback.
- **Polars Market Analysis Script**: Added `scripts/analyze_jobs.py` leveraging Polars for high-performance job market statistics and reporting.
- **Regression Testing**: Added `test_build_units_with_toml_config()` in `tests/test_units.py` to validate multi-configuration scraping flows.
- **Versioning Support**: Created `src/version.py` and added `--version` support to the CLI.

### Changed
- Refactored project organization and established robust task planning framework via `.planning/`.
