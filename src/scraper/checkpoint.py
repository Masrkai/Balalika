import json
from pathlib import Path
from typing import Dict

def get_checkpoint(path: Path) -> int:
    if not path.exists():
        return 0
    with open(path, 'r') as f:
        data = json.load(f)
        return data.get('start_index', 0)

def update_checkpoint(path: Path, index: int) -> None:
    data = {'start_index': index}
    with open(path, 'w') as f:
        json.dump(data, f)

def reset_checkpoint(path: Path) -> None:
    if path.exists():
        path.unlink()
