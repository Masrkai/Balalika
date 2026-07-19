import argparse
import json
from pathlib import Path

import polars as pl


def main():
    parser = argparse.ArgumentParser(description="Merge device shards into canonical jobs output.")
    parser.add_argument("--data-dir", type=Path, default=Path("Data"))
    parser.add_argument("--out-jsonl", type=Path, default=None)
    parser.add_argument("--out-csv", type=Path, default=None)
    args = parser.parse_args()

    data_dir = args.data_dir
    out_jsonl = args.out_jsonl or (data_dir / "jobs.jsonl")
    out_csv = args.out_csv or (data_dir / "jobs.csv")

    shard_dir = data_dir / "shards"
    frames = []

    # Existing canonical output is treated as just another source (idempotent re-merge).
    for path in [data_dir / "jobs.jsonl", *sorted(shard_dir.glob("jobs.*.jsonl"))]:
        if path.exists():
            try:
                df = pl.read_ndjson(path)
                frames.append(df)
                print(f"Loaded {path.name}: {df.height} rows")
            except Exception as e:
                print(f"Skipping {path}: {e}")

    if not frames:
        print("No shard or output files found. Nothing to merge.")
        return

    combined = pl.concat(frames, how="vertical")
    # Cross-device dedup by job_url, keeping the first occurrence.
    combined = combined.unique(subset=["job_url"], keep="first")
    combined = combined.sort(["country", "category", "keyword", "job_title"])

    combined.write_ndjson(out_jsonl)
    combined.write_csv(out_csv)
    print(f"Merged -> {out_jsonl.name} and {out_csv.name}: {combined.height} unique jobs")


if __name__ == "__main__":
    main()
