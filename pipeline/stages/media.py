from __future__ import annotations

import random
from pathlib import Path

from models.media import MediaAsset
from models.project import ProjectState
from providers.media.base import MediaProvider


def search_and_download_media(
    state: ProjectState,
    providers: list[MediaProvider],
    max_per_scene: int = 2,
) -> ProjectState:
    if not state.script:
        raise ValueError("Script must be generated before media search")

    media_dir = state.output_dir / "media"
    media_dir.mkdir(parents=True, exist_ok=True)

    all_assets: list[MediaAsset] = []

    for scene in state.script.scenes:
        scene_assets: list[MediaAsset] = []

        for query in scene.search_queries:
            for provider in providers:
                try:
                    results = provider.search_videos(query, count=max_per_scene)
                    scene_assets.extend(results)
                except Exception:
                    continue

                if len(scene_assets) >= max_per_scene:
                    break
            if len(scene_assets) >= max_per_scene:
                break

        for asset in scene_assets[:max_per_scene]:
            try:
                local_path = provider.download(asset, str(media_dir))
                asset.local_path = local_path
                all_assets.append(asset)
            except Exception:
                continue

    state.media_assets = all_assets
    state.save()
    return state
