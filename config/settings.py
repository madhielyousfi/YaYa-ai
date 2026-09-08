from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OLLAMA_")

    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5:7b"


class TTSSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TTS_")

    voice: str = "en-US-GuyNeural"
    rate: str = "+0%"
    volume: str = "+0%"


class MediaSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    pexels_api_key: str = ""
    pixabay_api_key: str = ""


class VideoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VIDEO_")

    width: int = 1080
    height: int = 1920
    fps: int = 30
    codec: str = "libx264"
    audio_codec: str = "aac"


class PathSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="")

    output_dir: Path = Path("./output")
    fonts_dir: Path = Path("./assets/fonts")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm: LLMSettings = LLMSettings()
    tts: TTSSettings = TTSSettings()
    media: MediaSettings = MediaSettings()
    video: VideoSettings = VideoSettings()
    paths: PathSettings = PathSettings()


settings = Settings()
