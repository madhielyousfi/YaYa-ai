from __future__ import annotations

from pydantic import BaseModel


class VideoTrack(BaseModel):
    scene_id: int
    start: float
    end: float
    asset_path: str


class AudioTrack(BaseModel):
    type: str  # "voice" or "music"
    start: float
    file_path: str
    volume: float = 1.0


class Timeline(BaseModel):
    duration: float
    video_tracks: list[VideoTrack]
    audio_tracks: list[AudioTrack]
    subtitle_path: str | None = None
