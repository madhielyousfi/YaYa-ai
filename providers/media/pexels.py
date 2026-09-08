from __future__ import annotations

import hashlib
import time
from pathlib import Path

import httpx

from config.settings import settings
from models.media import MediaAsset, MediaType


class PexelsProvider:
    BASE_URL = "https://api.pexels.com"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.media.pexels_api_key
        self.client = httpx.Client(
            headers={"Authorization": self.api_key},
            timeout=30.0,
        )

    def search_videos(self, query: str, count: int = 5) -> list[MediaAsset]:
        response = self.client.get(
            f"{self.BASE_URL}/videos/search",
            params={"query": query, "per_page": count, "orientation": "portrait"},
        )
        response.raise_for_status()
        data = response.json()

        assets = []
        for video in data.get("videos", []):
            files = video.get("video_files", [])
            if not files:
                continue
            best = max(files, key=lambda f: f.get("height", 0))
            assets.append(
                MediaAsset(
                    id=str(video["id"]),
                    source="pexels",
                    media_type=MediaType.VIDEO,
                    url=best["link"],
                    width=best.get("width", 0),
                    height=best.get("height", 0),
                    duration=video.get("duration", 0),
                    query=query,
                )
            )
        return assets

    def search_images(self, query: str, count: int = 5) -> list[MediaAsset]:
        response = self.client.get(
            f"{self.BASE_URL}/v1/search",
            params={"query": query, "per_page": count, "orientation": "portrait"},
        )
        response.raise_for_status()
        data = response.json()

        assets = []
        for photo in data.get("photos", []):
            src = photo.get("src", {})
            assets.append(
                MediaAsset(
                    id=str(photo["id"]),
                    source="pexels",
                    media_type=MediaType.IMAGE,
                    url=src.get("large", src.get("original", "")),
                    width=photo.get("width", 0),
                    height=photo.get("height", 0),
                    query=query,
                )
            )
        return assets

    def download(self, asset: MediaAsset, output_dir: str) -> str:
        ext = "mp4" if asset.media_type == MediaType.VIDEO else "jpg"
        filename = f"{asset.source}_{asset.id}.{ext}"
        output_path = Path(output_dir) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.exists():
            asset.local_path = str(output_path)
            return str(output_path)

        with self.client.stream("GET", asset.url) as response:
            response.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)

        asset.local_path = str(output_path)
        return str(output_path)
