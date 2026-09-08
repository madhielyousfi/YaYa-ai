from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from models.media import MediaAsset
from models.script import Script
from models.timeline import Timeline


class ProjectStatus(str, Enum):
    CREATED = "created"
    SCRIPTING = "scripting"
    MEDIA_SEARCH = "media_search"
    MEDIA_READY = "media_ready"
    AUDIO_GENERATION = "audio_generation"
    SUBTITLES = "subtitles"
    TIMELINE_READY = "timeline_ready"
    RENDERING = "rendering"
    THUMBNAIL = "thumbnail"
    COMPLETED = "completed"
    FAILED = "failed"


class ProjectState(BaseModel):
    id: str
    topic: str
    status: ProjectStatus = ProjectStatus.CREATED
    output_dir: Path

    script: Script | None = None
    media_assets: list[MediaAsset] = Field(default_factory=list)
    narration_path: Path | None = None
    music_path: Path | None = None
    music_track: dict | None = None
    subtitle_path: Path | None = None
    thumbnail_path: Path | None = None
    video_path: Path | None = None
    timeline: Timeline | None = None

    error: str | None = None

    def save(self) -> None:
        path = self.output_dir / "project_state.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2))

    @classmethod
    def load(cls, project_dir: Path) -> ProjectState:
        path = project_dir / "project_state.json"
        return cls.model_validate_json(path.read_text())
