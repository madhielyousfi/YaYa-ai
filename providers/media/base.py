from __future__ import annotations

from typing import Protocol

from models.media import MediaAsset, MediaType


class MediaProvider(Protocol):
    def search_videos(self, query: str, count: int = 5) -> list[MediaAsset]:
        """Search for videos matching query."""
        ...

    def search_images(self, query: str, count: int = 5) -> list[MediaAsset]:
        """Search for images matching query."""
        ...

    def download(self, asset: MediaAsset, output_dir: str) -> str:
        """Download media asset to local path, return local path."""
        ...
