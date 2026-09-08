from __future__ import annotations

import edge_tts

from config.settings import settings


class EdgeTTSProvider:
    def __init__(
        self,
        voice: str | None = None,
        rate: str | None = None,
        volume: str | None = None,
    ):
        self.voice = voice or settings.tts.voice
        self.rate = rate or settings.tts.rate
        self.volume = volume or settings.tts.volume

    async def generate(self, text: str, output_path: str) -> None:
        communicate = edge_tts.Communicate(
            text,
            voice=self.voice,
            rate=self.rate,
            volume=self.volume,
        )
        await communicate.save(output_path)

    async def list_voices(self, language: str = "en") -> list[dict]:
        voices = await edge_tts.list_voices()
        return [v for v in voices if v["Locale"].startswith(language)]

    async def list_voice_names(self, language: str = "en") -> list[str]:
        voices = await self.list_voices(language)
        return [v["ShortName"] for v in voices]
