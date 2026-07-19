import json
from pathlib import Path
from typing import Dict


def _load(path: Path) -> Dict:
    if not path.exists():
        return {}
    with open(path, 'r') as f:
        return json.load(f)


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


# Per-unit checkpoints: a single device file holds {unit_id: start_index}.
def get_unit_checkpoint(path: Path, unit_id: str) -> int:
    data = _load(path)
    return int(data.get(unit_id, 0))


def update_unit_checkpoint(path: Path, unit_id: str, index: int) -> None:
    data = _load(path)
    data[unit_id] = index
    with open(path, 'w') as f:
        json.dump(data, f)


def reset_unit_checkpoint(path: Path, unit_id: str | None = None) -> None:
    if unit_id is None:
        if path.exists():
            path.unlink()
    else:
        data = _load(path)
        data.pop(unit_id, None)
        with open(path, 'w') as f:
            json.dump(data, f)

