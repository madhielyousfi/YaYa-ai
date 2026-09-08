from __future__ import annotations

from typing import Protocol


class MusicProvider(Protocol):
    def search(self, query: str, count: int = 5) -> list[dict]:
        """Search for music tracks. Returns list of dicts with id, url, duration."""
        ...

    def download(self, track: dict, output_dir: str) -> str:
        """Download music track to local path, return local path."""
        ...
