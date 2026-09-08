from __future__ import annotations

from pathlib import Path

import httpx

from config.settings import settings
from models.media import MediaAsset, MediaType


class PixabayProvider:
    BASE_URL = "https://pixabay.com/api"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.media.pixabay_api_key
        self.client = httpx.Client(timeout=30.0)

    def search_videos(self, query: str, count: int = 5) -> list[MediaAsset]:
        response = self.client.get(
            f"{self.BASE_URL}/videos/",
            params={
                "key": self.api_key,
                "q": query,
                "per_page": max(3, count),
                "video_type": "film",
                "safesearch": "true",
            },
        )
        response.raise_for_status()
        data = response.json()

        assets = []
        for hit in data.get("hits", []):
            videos = hit.get("videos", {})
            medium = videos.get("medium", videos.get("small", {}))
            if not medium.get("url"):
                continue
            assets.append(
                MediaAsset(
                    id=str(hit["id"]),
                    source="pixabay",
                    media_type=MediaType.VIDEO,
                    url=medium["url"],
                    width=medium.get("width", 0),
                    height=medium.get("height", 0),
                    duration=hit.get("duration", 0),
                    query=query,
                )
            )
        return assets

    def search_images(self, query: str, count: int = 5) -> list[MediaAsset]:
        response = self.client.get(
            f"{self.BASE_URL}/",
            params={
                "key": self.api_key,
                "q": query,
                "per_page": max(3, count),
                "image_type": "photo",
                "safesearch": "true",
            },
        )
        response.raise_for_status()
        data = response.json()

        assets = []
        for hit in data.get("hits", []):
            assets.append(
                MediaAsset(
                    id=str(hit["id"]),
                    source="pixabay",
                    media_type=MediaType.IMAGE,
                    url=hit.get("largeImageURL", hit.get("webformatURL", "")),
                    width=hit.get("imageWidth", 0),
                    height=hit.get("imageHeight", 0),
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
