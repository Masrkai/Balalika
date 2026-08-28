from pathlib import Path
from typing import Dict


def _load(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    data = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                data[key.strip()] = val.strip()
            else:
                # Fallback for single flat number in global checkpoint file
                data["__global__"] = line
    return data


def _save(path: Path, data: Dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for key, val in data.items():
            if key == "__global__" and len(data) == 1:
                f.write(f"{val}\n")
            else:
                f.write(f"{key}={val}\n")


def get_checkpoint(path: Path) -> int:
    if not path.exists():
        return 0
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return 0
    if content.isdigit() or (content.startswith("-") and content[1:].isdigit()):
        return int(content)
    data = _load(path)
    if "__global__" in data:
        return int(data["__global__"])
    return 0


def update_checkpoint(path: Path, index: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(index), encoding="utf-8")


def reset_checkpoint(path: Path) -> None:
    if path.exists():
        path.unlink()


# Per-unit checkpoints: a file holding key=value pairs (unit_id=start_index).
def get_unit_checkpoint(path: Path, unit_id: str) -> int:
    data = _load(path)
    return int(data.get(unit_id, 0))


def update_unit_checkpoint(path: Path, unit_id: str, index: int) -> None:
    data = _load(path)
    data[unit_id] = str(index)
    _save(path, data)


def reset_unit_checkpoint(path: Path, unit_id: str | None = None) -> None:
    if unit_id is None:
        if path.exists():
            path.unlink()
    else:
        data = _load(path)
        if unit_id in data:
            data.pop(unit_id)
            _save(path, data)
