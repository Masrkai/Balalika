# Balalika

A lightweight scraper that collects CS job listings from LinkedIn across 9 countries and 9 specializations, then enriches each listing with salary, description, and job criteria data.

Built as a university Data Mining project (and for a doctor who didn't deserve it).

## Why

because linkedin is so stupid of an idea that it allowed corporations to analyse the market but not consumers which is INSANE.
so this is a protest against this nasty cornering situation against the situation of job market and how to collect data on it putting US in our well deserved seat where we can again OBSERVE THE JOB MARKET.
So next time a corporation say the very stupid arguement that they are hiring more than ever or paying more than ever or Ai didn't effect jobs you have numbers to back this up.
also this has the potential to be a distributed effort

---

## What it does

A **partitioned** LinkedIn guest-API scraper. The work is modeled as a matrix of
**units** = `(country, category, keyword)`, where `keyword` is the canonical job
title from `Data/CS_Jobs.json`. A run can be split across multiple devices, each
device owning a **disjoint slice** of the matrix and writing to its own shard. A
separate merge step combines all shards and dedups cross-device by `job_url`.

```
src/main.py  <device>  ->  owns a slice of (country, category, keyword) units
  for each owned unit:
    loop fetch_and_parse_batch(keyword, country, start=unit_checkpoint)
      dedup by job_url (seen set, per unit)
      enrich via fetch_job_details(job_url)  -> description + salary
      append to Data/shards/jobs.<device>.jsonl / .csv
      advance per-unit checkpoint
  Ctrl+C safe: each unit's checkpoint is saved

src/merge.py  ->  combine all Data/shards/jobs.*.jsonl + Data/jobs.jsonl
  dedup by job_url (cross-device)
  write canonical Data/jobs.jsonl + Data/jobs.csv  (idempotent)
```

Each scraped row is tagged with `country`, `category`, and `keyword` so the
collected data is extensible and safely re-mergeable.

> This is intentionally small-scale research scraping, not high-volume use. Rate
> limiting (jitter + 429 backoff) is per-request and per-device.

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

---

## Usage

### Single device (whole matrix)

```bash
python src/main.py
```

Scrapes every `(country, category, keyword)` unit using the default 9 countries
and all categories in `Data/CS_Jobs.json`. Writes to `Data/shards/jobs.local.jsonl`.
Resume is automatic via per-unit checkpoints.

### Split across devices (mod-split)

Assign each device a deterministic, disjoint slice of the full matrix:

```bash
# Device 1 of 4
python src/main.py --device 1 --of 4 --device-id dev1
# Device 2 of 4
python src/main.py --device 2 --of 4 --device-id dev2
# Device 3 of 4
python src/main.py --device 3 --of 4 --device-id dev3
# Device 4 of 4
python src/main.py --device 4 --of 4 --device-id dev4
```

`--device N --of M` keeps unit `i` on device `(i % M) + 1`, so the split is
reproducible on any machine from the same inputs. `--device` and `--of` must be
supplied together.

### Explicit slice

Hand-pick a slice by country and/or category (overrides mod-split):

```bash
python src/main.py \
  --countries "Germany,Canada" \
  --categories "Software Engineering,Data Science & AI" \
  --device-id devG
```

`--countries` and `--categories` accept comma-separated names (case-insensitive
substring match against the canonical lists).

### Merge device outputs

After the devices finish, on any machine with the shards:

```bash
python src/merge.py
```

Reads `Data/shards/jobs.*.jsonl` (and the existing `Data/jobs.jsonl` if present),
dedups by `job_url`, and writes the canonical `Data/jobs.jsonl` + `Data/jobs.csv`.
Re-running merge is safe (idempotent).

### Reset checkpoints

```bash
python src/main.py --override-checkpoint            # resets this device's units
python src/main.py --device 1 --of 4 --override-checkpoint
```

### Useful flags

| Flag                    | Meaning                                                     |
|-------------------------|-------------------------------------------------------------|
| `--device` / `--of`     | mod-split assignment (1-based index, total count)           |
| `--countries`           | comma-separated country filter (overrides mod-split)        |
| `--categories`          | comma-separated category filter                             |
| `--device-id`           | shard identifier (defaults to `dev<N>` or `local`)          |
| `--full-countries`      | use the full vendored country list instead of the default 9 |
| `--override-checkpoint` | reset this device's per-unit checkpoints                    |
| `--categories-file`     | path to the categories JSON (default `Data/CS_Jobs.json`)   |
| `--data-dir`            | output root (default `Data`)                                |

---

## Countries scraped

| Tier      | Countries                      |
|-----------|--------------------------------|
| 1st class | United States, Germany, Canada |
| 2nd class | Poland, Finland, Brazil        |
| 3rd class | Egypt, Madagascar, Morocco     |

The default set is the 9 above. Pass `--full-countries` to scrape the full
vendored list (see `src/data/countries.py`).

## Categories

Software Engineering, Data Science & AI, Cybersecurity, Cloud & Network Engineering, DevOps & SRE, Robotics & Automation, Enterprise IT & Systems Administration, Bioinformatics & Computational Biology, Meme Jobs.

These come from `Data/CS_Jobs.json`. `keyword` for each unit is the job's
canonical `name` (alternatives are not used as separate searches, to bound
request volume).

---

## Rate limiting

- 1–2s random jitter between requests
- Bounded retry with exponential backoff on HTTP 429 (up to 3 retries)
- Silent failures return `None` / `(None, None)` and advance the checkpoint —
  no run is killed by a single bad batch

This is a small-scale research scraper, not designed for high-volume use. Each
device is independent, so distributing work multiplies total request volume;
keep the jitter and backoff in place.

---

## Running tests

```bash
just test
```

---

See [`Docs/distributed_scraping.md`](Docs/distributed_scraping.md) for the
design rationale and the partitioning pattern.

---

see the [License](LICENSE)
