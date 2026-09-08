from __future__ import annotations

from pathlib import Path

import httpx

from config.settings import settings


class PixabayMusicProvider:
    BASE_URL = "https://pixabay.com/api"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.media.pixabay_api_key
        self.client = httpx.Client(timeout=30.0)

    def search(self, query: str, count: int = 5) -> list[dict]:
        for endpoint in ["/music/", "/sound-effects/", "/videos/"]:
            try:
                response = self.client.get(
                    f"{self.BASE_URL}{endpoint}",
                    params={
                        "key": self.api_key,
                        "q": query,
                        "per_page": max(3, count),
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    tracks = []
                    for hit in data.get("hits", []):
                        audio_url = hit.get("audio", hit.get("url", ""))
                        if audio_url:
                            tracks.append({
                                "id": hit.get("id"),
                                "url": audio_url,
                                "duration": hit.get("duration", 0),
                                "tags": hit.get("tags", ""),
                                "user": hit.get("user", ""),
                            })
                    if tracks:
                        return tracks
            except Exception:
                continue
        return []

    def download(self, track: dict, output_dir: str) -> str:
        filename = f"music_{track['id']}.mp3"
        output_path = Path(output_dir) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.exists():
            return str(output_path)

        url = track.get("url", "")
        if not url:
            raise ValueError(f"No URL for track {track['id']}")

        with self.client.stream("GET", url) as response:
            response.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)

        return str(output_path)
