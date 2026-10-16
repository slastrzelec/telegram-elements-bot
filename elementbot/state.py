"""Stan: które pierwiastki już opublikowano. Zapis atomowy."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


def load(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if "published" not in data or not isinstance(data["published"], list):
        raise ValueError("Uszkodzony plik stanu: brak listy 'published'")
    return data


def save(path: Path, data: dict) -> None:
    path = Path(path)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".state-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def published_numbers(data: dict) -> set[int]:
    return {int(item["z"]) for item in data["published"]}


def published_dates(data: dict) -> set[str]:
    return {item["date"] for item in data["published"] if item.get("date")}


def mark_published(data: dict, z: int, symbol: str, date_iso: str, message_id: int | None) -> None:
    data["published"].append({"z": z, "symbol": symbol, "date": date_iso, "message_id": message_id})
