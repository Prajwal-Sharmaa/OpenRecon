"""Small JSON persistence layer with atomic writes and no external services."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Bookmark, Investigation


class LocalStore:
    """Persist user-created data below the project folder for transparent local use."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        return self.root / f"{name}.json"

    def _read(self, name: str, fallback: Any) -> Any:
        path = self._path(name)
        if not path.exists():
            return fallback
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            # Keep a damaged file around for manual recovery instead of
            # overwriting it on the next save.
            damaged = path.with_suffix(".corrupt.json")
            if not damaged.exists():
                try:
                    path.replace(damaged)
                except OSError:
                    pass
            return fallback

    def _write(self, name: str, data: Any) -> None:
        path = self._path(name)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        if path.exists():
            backup = path.with_suffix(".bak.json")
            try:
                backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            except OSError:
                pass
        temporary.replace(path)

    def investigations(self) -> list[Investigation]:
        values = self._read("investigations", [])
        return [Investigation.from_dict(item) for item in values]

    def save_investigations(self, records: list[Investigation]) -> None:
        self._write("investigations", [record.to_dict() for record in records])

    def bookmarks(self) -> list[Bookmark]:
        values = self._read("bookmarks", [])
        return [Bookmark.from_dict(item) for item in values]

    def save_bookmarks(self, records: list[Bookmark]) -> None:
        self._write("bookmarks", [record.to_dict() for record in records])

    def settings(self) -> dict[str, Any]:
        return self._read("settings", {"analyst_name": "Analyst", "default_engine": "Google"})

    def save_settings(self, settings: dict[str, Any]) -> None:
        self._write("settings", settings)
