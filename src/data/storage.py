import polars as pl
from pathlib import Path
from typing import List, Dict

def append_to_csv(data: List[Dict], path: Path) -> None:
    df = pl.from_dicts(data)
    if not path.exists():
        df.write_csv(path)
    else:
        # Read existing, concat, write back
        existing = pl.read_csv(path)
        combined = pl.concat([existing, df])
        combined.write_csv(path)

def append_to_jsonl(data: List[Dict], path: Path) -> None:
    # Option B: JSON Lines - efficient append
    df = pl.from_dicts(data)
    # Write each row as a line in ndjson format
    with open(path, 'a') as f:
        # Polars write_ndjson writes to a file object
        df.write_ndjson(f)
