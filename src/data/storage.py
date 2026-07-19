import polars as pl
from pathlib import Path
from typing import List, Dict

def append_to_csv(data: List[Dict], path: Path) -> None:
    # Append-only: header written once on creation, avoids O(n^2) reread-rewrite.
    df = pl.from_dicts(data)
    if not path.exists():
        df.write_csv(path)
    else:
        with open(path, "a") as f:
            df.write_csv(f, include_header=False)

def append_to_jsonl(data: List[Dict], path: Path) -> None:
    # Option B: JSON Lines - efficient append
    df = pl.from_dicts(data)
    # Write each row as a line in ndjson format
    with open(path, 'a') as f:
        # Polars write_ndjson writes to a file object
        df.write_ndjson(f)


def shard_path(data_dir: Path, device_id: str, ext: str) -> Path:
    shard_dir = data_dir / "shards"
    shard_dir.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in device_id)
    return shard_dir / f"jobs.{safe}.{ext}"


def append_to_csv_shard(data: List[Dict], data_dir: Path, device_id: str) -> None:
    append_to_csv(data, shard_path(data_dir, device_id, "csv"))


def append_to_jsonl_shard(data: List[Dict], data_dir: Path, device_id: str) -> None:
    append_to_jsonl(data, shard_path(data_dir, device_id, "jsonl"))
