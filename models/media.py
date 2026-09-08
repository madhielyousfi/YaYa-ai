from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class MediaType(str, Enum):
    VIDEO = "video"
    IMAGE = "image"


class MediaAsset(BaseModel):
    id: str
    source: str
    media_type: MediaType
    url: str
    local_path: str | None = None
    width: int = 0
    height: int = 0
    duration: float = 0.0
    query: str = ""


class SearchQuery(BaseModel):
    query: str
    count: int = 5
    media_type: MediaType = MediaType.VIDEO


class MediaSearchResult(BaseModel):
    query: str
    assets: list[MediaAsset]
    source: str
