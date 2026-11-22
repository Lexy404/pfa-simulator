"""One conversation between a player and an NPC (lives for one WebSocket connection).

Current turn pipeline (text only):  player text -> NPC LLM -> streamed tokens.
Later stages (STT, utterance classifier, stress engine, TTS) plug in here.
"""

import logging
import time
from typing import AsyncIterator

from pfa_server.llm import LLMClient
from pfa_server.protocol import Latency, NpcDone, NpcToken

log = logging.getLogger(__name__)


class Session:
    def __init__(self, llm: LLMClient, system_prompt: str) -> None:
        self.llm = llm
        self.history: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        self.turn = 0

    async def player_text(self, text: str) -> AsyncIterator[NpcToken | NpcDone]:
        """Handle one player utterance; yield NPC tokens, then a final NpcDone."""
        self.turn += 1
        start = time.perf_counter()
        ttft: float | None = None
        parts: list[str] = []

        self.history.append({"role": "user", "content": text})
        async for token in self.llm.stream_chat(self.history):
            if ttft is None:
                ttft = time.perf_counter() - start
            parts.append(token)
            yield NpcToken(text=token)

        total = time.perf_counter() - start
        reply = "".join(parts)
        self.history.append({"role": "assistant", "content": reply})

        latency = Latency(
            ttft_ms=round((ttft if ttft is not None else total) * 1000, 1),
            total_ms=round(total * 1000, 1),
        )
        log.info("turn=%d ttft=%.0fms total=%.0fms", self.turn, latency.ttft_ms, latency.total_ms)
        yield NpcDone(text=reply, latency=latency)
