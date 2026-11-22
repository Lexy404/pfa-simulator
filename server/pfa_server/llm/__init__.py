"""LLM clients."""

from typing import AsyncIterator, Protocol


class LLMClient(Protocol):
    """Anything that can stream a chat reply token by token."""

    def stream_chat(self, messages: list[dict[str, str]]) -> AsyncIterator[str]: ...

    async def ping(self) -> bool: ...
