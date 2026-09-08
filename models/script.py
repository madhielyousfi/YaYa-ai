from __future__ import annotations

from pydantic import BaseModel


class Scene(BaseModel):
    id: int
    duration: float
    narration: str
    visual_prompt: str
    search_queries: list[str]


class Script(BaseModel):
    title: str
    hook: str
    duration: int
    language: str = "en"
    scenes: list[Scene]

    @property
    def full_narration(self) -> str:
        return " ".join(scene.narration for scene in self.scenes)
