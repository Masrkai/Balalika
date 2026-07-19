import json
from pathlib import Path

import polars as pl

from src.data.storage import append_to_jsonl_shard
from src.merge import main as merge_main
import argparse


def _write_shard(data_dir, device_id, rows):
    append_to_jsonl_shard(rows, data_dir, device_id)


def test_merge_dedups_cross_device(tmp_path):
    shard_dir = tmp_path / "shards"
    shard_dir.mkdir()

    base = [
        {"country": "Germany", "category": "Software Engineering", "keyword": "Software Engineer",
         "job_title": "SWE", "company_name": "A", "location": "Berlin", "salary": None,
         "job_url": "https://www.linkedin.com/jobs/view/1", "posted_date": None, "description": None},
        {"country": "Canada", "category": "Data Science & AI", "keyword": "Data Scientist",
         "job_title": "DS", "company_name": "B", "location": "Toronto", "salary": None,
         "job_url": "https://www.linkedin.com/jobs/view/2", "posted_date": None, "description": None},
    ]
    # Device 1 and Device 2 both scrape the same overlapping job (simulating slice overlap).
    overlap = dict(base[0])
    _write_shard(tmp_path, "dev1", base)
    _write_shard(tmp_path, "dev2", [overlap, base[1]])

    merge_main.__wrapped__ if hasattr(merge_main, "__wrapped__") else None
    # Run merge via argparse override.
    import sys
    sys.argv = ["merge", "--data-dir", str(tmp_path)]
    merge_main()

    out = pl.read_ndjson(tmp_path / "jobs.jsonl")
    # dedup by job_url -> 2 unique despite 3 rows written
    assert out.height == 2
    assert out["job_url"].n_unique() == 2
    # fields preserved
    assert set(out["country"].to_list()) == {"Germany", "Canada"}


def test_merge_idempotent(tmp_path):
    rows = [
        {"country": "Germany", "category": "Software Engineering", "keyword": "Software Engineer",
         "job_title": "SWE", "company_name": "A", "location": "Berlin", "salary": None,
         "job_url": "https://www.linkedin.com/jobs/view/1", "posted_date": None, "description": None},
    ]
    _write_shard(tmp_path, "dev1", rows)
    import sys
    sys.argv = ["merge", "--data-dir", str(tmp_path)]
    merge_main()
    first = (tmp_path / "jobs.jsonl").read_text()
    merge_main()
    second = (tmp_path / "jobs.jsonl").read_text()
    assert first == second
