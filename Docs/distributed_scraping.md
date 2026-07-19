# Distributed / Partitioned Scraping

How Balalika splits a mass LinkedIn scrape across multiple devices, and the
patterns that make the split safe and resumable.

## Mental model: the work matrix

The total work is a matrix of **units**:

```
Unit = (country, category, keyword)
```

- **country** — from a vendored list (`src/data/countries.py`); default 9, or
  `--full-countries` for the full set.
- **category** — from `Data/CS_Jobs.json` (9 categories).
- **keyword** — the canonical job `name` only (alternatives are intentionally
  *not* searched, to bound request volume).

Total units = `|countries| × |categories| × |jobs per category|`. A unit is the
smallest assignable piece of work and the unit of resume.

## Pattern 1 — Deterministic mod-split (no coordinator)

Devices are assigned by `unit_index % of == device - 1`. Because the unit list
is built deterministically from the same inputs on every machine, each device
computes its own slice with **no shared state or coordination server**:

```python
owned = [u for i, u in enumerate(units) if i % of == device - 1]
```

This is a **content-based partition**: the work is hashed by position, not by a
random allocator, so device 3 always owns the same units regardless of when or
where it runs.

**Explicit override.** `--countries` / `--categories` filter the matrix by name
(case-insensitive substring). This is a manual, human-readable slice used when
you want to hand-pick a region rather than take a modulo chunk.

## Pattern 2 — Per-unit checkpointing

The old design stored a single `start_index` for one `(keyword, location)` pair.
That cannot support partitioning. Each device now keeps one checkpoint file
(`Data/checkpoints/<device>.json`) that is a dict:

```json
{ "Germany|Software Engineering|Software Engineer": 25,
  "Germany|Software Engineering|Backend Engineer": 0 }
```

`start_index` means "the LinkedIn search pagination offset for this unit". When
a unit returns no jobs, the loop ends for that unit and moves on; if interrupted
(`Ctrl+C`), every unit touched so far has already been persisted, so the next run
resumes exactly where it stopped. This is **fine-grained, independent resume** —
one device crashing doesn't lose another's progress.

## Pattern 3 — Sharded output, separate merge

Each device appends only to its own shard:

```
Data/shards/jobs.<device>.jsonl
Data/shards/jobs.<device>.csv
```

Writing to separate files means **no two devices ever contend for the same file**
— there is no cross-device lock, no append race. Combining happens later, in a
single-threaded `src/merge.py`:

```python
combined = pl.concat([read(shard) for shard in all_shards])
combined = combined.unique(subset=["job_url"], keep="first")  # cross-device dedup
combined.write_ndjson("Data/jobs.jsonl")
combined.write_csv("Data/jobs.csv")
```

Key properties:

- **Cross-device dedup by `job_url`.** Two devices whose slices overlap (e.g. an
  explicit filter that crosses a mod boundary) will not produce duplicate rows.
- **Idempotent.** Merge reads the canonical `Data/jobs.jsonl` as just another
  source, dedups, and rewrites it identically. Re-merging is a no-op.
- **Extensible rows.** Every row carries `country`, `category`, `keyword`, so the
  collected data is self-describing and safely re-mergeable.

## Why these choices (trade-offs)

| Choice | Benefit | Cost / ceiling |
|---|---|---|
| Mod-split, no coordinator | trivial to add devices; reproducible | uneven unit sizes if a category has many jobs; manual rebalance |
| Shard + merge (not shared file) | no locks, no races | a merge step is required before analysis |
| Dedup at merge (not write) | simple writers | duplicate bytes exist transiently in shards |
| Canonical name only | bounds request count | misses alt-title variants (acceptable for research) |
| Sequential per device | simple, low-risk | intra-device throughput capped (YAGNI to parallelize) |

## When to graduate past this pattern

- **Need dynamic rebalancing** (a device is slow/dead): introduce a shared work
  queue with a lock/lease instead of mod-split.
- **Need live combined output**: switch the shard append to a single append-only
  store with a `job_url` unique constraint (DB) instead of file shards.
- **High volume**: the per-request jitter + 429 backoff still applies, but you'll
  want proxies (JobSpy's model) rather than one IP per device.
