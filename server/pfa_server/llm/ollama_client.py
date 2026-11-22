"""Async streaming client for the Ollama chat API (POST /api/chat)."""

import json
from typing import AsyncIterator

import httpx


class OllamaClient:
    def __init__(self, host: str, model: str, timeout: float = 60.0) -> None:
        self.model = model
        self._http = httpx.AsyncClient(base_url=host, timeout=timeout)

    async def stream_chat(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        """Yield reply tokens as they arrive. `messages` uses Ollama/OpenAI chat format."""
        payload = {"model": self.model, "messages": messages, "stream": True}
        async with self._http.stream("POST", "/api/chat", json=payload) as resp:
            resp.raise_for_status()
            # Ollama streams newline-delimited JSON objects.
            async for line in resp.aiter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                if "error" in chunk:
                    raise RuntimeError(f"Ollama error: {chunk['error']}")
                token = chunk.get("message", {}).get("content", "")
                if token:
                    yield token
                if chunk.get("done"):
                    break

    async def ping(self) -> bool:
        """True if Ollama is reachable."""
        try:
            resp = await self._http.get("/api/tags", timeout=2.0)
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def aclose(self) -> None:
        await self._http.aclose()
