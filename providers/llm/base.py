from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    def generate(self, prompt: str, system: str = "") -> str:
        """Generate text from a prompt."""
        ...
