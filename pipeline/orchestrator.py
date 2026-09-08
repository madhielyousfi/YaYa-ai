from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from pathlib import Path

from models.project import ProjectState, ProjectStatus
from pipeline.stages import script, media, tts, subtitles, assembler, thumbnail, music
from providers.llm.ollama import OllamaProvider
from providers.tts.edge_tts import EdgeTTSProvider
from providers.media.pexels import PexelsProvider
from providers.media.pixabay import PixabayProvider
from providers.music.pixabay_music import PixabayMusicProvider
from config.settings import settings


class Orchestrator:
    def __init__(
        self,
        llm: OllamaProvider | None = None,
        tts_provider: EdgeTTSProvider | None = None,
        media_providers: list | None = None,
        music_provider: PixabayMusicProvider | None = None,
    ):
        self.llm = llm or OllamaProvider()
        self.tts_provider = tts_provider or EdgeTTSProvider()
        self.media_providers = media_providers or self._default_media_providers()
        self.music_provider = music_provider or self._default_music_provider()

    def _default_media_providers(self) -> list:
        providers = []
        if settings.media.pexels_api_key:
            providers.append(PexelsProvider())
        if settings.media.pixabay_api_key:
            providers.append(PixabayProvider())
        return providers

    def _default_music_provider(self) -> PixabayMusicProvider | None:
        if settings.media.pixabay_api_key:
            return PixabayMusicProvider()
        return None

    def create_project(self, topic: str, output_dir: Path | None = None) -> ProjectState:
        project_id = uuid.uuid4().hex[:12]
        if output_dir is None:
            output_dir = settings.paths.output_dir / project_id
        output_dir.mkdir(parents=True, exist_ok=True)

        state = ProjectState(
            id=project_id,
            topic=topic,
            output_dir=output_dir,
        )
        state.save()
        return state

    def run(self, topic: str, duration: int = 60, language: str = "en", mood: str = "cinematic") -> ProjectState:
        state = self.create_project(topic)

        print(f"[1/7] Generating script for: {topic}")
        state.status = ProjectStatus.SCRIPTING
        state.save()
        state = script.generate_script(state, self.llm, duration, language)
        print(f"      Script: {state.script.title} ({len(state.script.scenes)} scenes)")

        print("[2/7] Searching and downloading media...")
        state.status = ProjectStatus.MEDIA_SEARCH
        state.save()
        state = media.search_and_download_media(state, self.media_providers)
        print(f"      Found {len(state.media_assets)} media assets")

        print("[3/7] Generating narration...")
        state.status = ProjectStatus.AUDIO_GENERATION
        state.save()
        state = asyncio.run(tts.generate_narration(state, self.tts_provider))
        print(f"      Narration: {state.narration_path}")

        print("[4/7] Searching background music...")
        if self.music_provider:
            state = music.search_and_download_music(state, self.music_provider, mood)
            if state.music_path:
                print(f"      Music: {state.music_path}")
            else:
                print("      No music found, continuing without")
        else:
            print("      Skipped (no music provider)")

        print("[5/7] Generating subtitles...")
        state.status = ProjectStatus.SUBTITLES
        state.save()
        state = subtitles.generate_subtitles(state)
        print(f"      Subtitles: {state.subtitle_path}")

        print("[6/7] Building timeline and rendering video...")
        state.status = ProjectStatus.RENDERING
        state.save()
        assembler.build_timeline(state)
        video_path = assembler.render_video(state)
        print(f"      Video: {video_path}")

        print("[7/7] Generating thumbnail...")
        state.status = ProjectStatus.THUMBNAIL
        state.save()
        thumbnail_path = thumbnail.generate_thumbnail(state)
        print(f"      Thumbnail: {thumbnail_path}")

        state.status = ProjectStatus.COMPLETED
        state.save()
        print(f"\nDone! Output: {state.output_dir}")
        return state
