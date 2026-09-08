from __future__ import annotations

from typing import Protocol


class TTSProvider(Protocol):
    async def generate(self, text: str, output_path: str) -> None:
        """Generate speech audio from text."""
        ...
