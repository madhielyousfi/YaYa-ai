from __future__ import annotations

from pathlib import Path

from models.project import ProjectState
from providers.music.base import MusicProvider


def search_and_download_music(
    state: ProjectState,
    music_provider: MusicProvider,
    mood: str = "cinematic",
) -> ProjectState:
    music_dir = state.output_dir / "music"
    music_dir.mkdir(parents=True, exist_ok=True)

    query = f"{mood} background music"
    if state.script:
        topic_words = state.script.title.split()[:3]
        query = f"{' '.join(topic_words)} {mood}"

    tracks = music_provider.search(query, count=3)

    if not tracks:
        tracks = music_provider.search("cinematic background", count=3)

    if tracks:
        track = tracks[0]
        local_path = music_provider.download(track, str(music_dir))
        state.music_path = Path(local_path)
        state.music_track = track
    else:
        state.music_path = None
        state.music_track = None

    state.save()
    return state
