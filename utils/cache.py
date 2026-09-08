from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path


class FileCache:
    def __init__(self, cache_dir: str = ".cache", ttl_seconds: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl_seconds

    def _key_path(self, key: str) -> Path:
        h = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{h}.json"

    def get(self, key: str) -> dict | None:
        path = self._key_path(key)
        if not path.exists():
            return None

        data = json.loads(path.read_text())
        if time.time() - data.get("timestamp", 0) > self.ttl:
            path.unlink(missing_ok=True)
            return None

        return data.get("value")

    def set(self, key: str, value: dict) -> None:
        path = self._key_path(key)
        path.write_text(json.dumps({"timestamp": time.time(), "value": value}))

    def clear(self) -> None:
        for f in self.cache_dir.glob("*.json"):
            f.unlink()

    def has(self, key: str) -> bool:
        return self.get(key) is not None
