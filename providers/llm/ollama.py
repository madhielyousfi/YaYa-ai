from __future__ import annotations

import httpx

from config.settings import settings


class OllamaProvider:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
    ):
        self.base_url = base_url or settings.llm.base_url
        self.model = model or settings.llm.model
        self.client = httpx.Client(base_url=self.base_url, timeout=120.0)

    def generate(self, prompt: str, system: str = "") -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.post(
            "/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    def is_available(self) -> bool:
        try:
            response = self.client.get("/api/tags")
            return response.status_code == 200
        except httpx.ConnectError:
            return False
