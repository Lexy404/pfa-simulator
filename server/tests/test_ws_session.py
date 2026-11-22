from typing import AsyncIterator

import pytest
from fastapi.testclient import TestClient

from pfa_server.config import Settings
from pfa_server.main import create_app


class FakeLLM:
    """Stands in for OllamaClient: streams a fixed reply and records the prompts it got."""

    def __init__(self, tokens: list[str]) -> None:
        self.tokens = tokens
        self.calls: list[list[dict[str, str]]] = []

    async def stream_chat(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        self.calls.append([dict(m) for m in messages])
        for t in self.tokens:
            yield t

    async def ping(self) -> bool:
        return True


@pytest.fixture
def llm() -> FakeLLM:
    return FakeLLM(["Who ", "are ", "you?"])


@pytest.fixture
def client(llm):
    with TestClient(create_app(Settings(), llm=llm)) as c:
        yield c


def read_turn(ws) -> list[dict]:
    msgs = []
    while True:
        msg = ws.receive_json()
        msgs.append(msg)
        if msg["type"] in ("npc_done", "error"):
            return msgs


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["ollama"] is True


def test_turn_streams_tokens_then_done(client, llm):
    with client.websocket_connect("/ws/session") as ws:
        ws.send_json({"type": "player_text", "text": "Hello, are you okay?"})
        msgs = read_turn(ws)

    assert [m["type"] for m in msgs] == ["npc_token"] * 3 + ["npc_done"]
    assert "".join(m["text"] for m in msgs[:-1]) == "Who are you?"
    done = msgs[-1]
    assert done["text"] == "Who are you?"
    assert 0 <= done["latency"]["ttft_ms"] <= done["latency"]["total_ms"]

    prompt = llm.calls[0]
    assert prompt[0]["role"] == "system" and "fire" in prompt[0]["content"]
    assert prompt[-1] == {"role": "user", "content": "Hello, are you okay?"}


def test_history_kept_between_turns(client, llm):
    with client.websocket_connect("/ws/session") as ws:
        ws.send_json({"type": "player_text", "text": "first"})
        read_turn(ws)
        ws.send_json({"type": "player_text", "text": "second"})
        read_turn(ws)

    roles = [m["role"] for m in llm.calls[1]]
    assert roles == ["system", "user", "assistant", "user"]


def test_invalid_message_returns_error_and_keeps_connection(client):
    with client.websocket_connect("/ws/session") as ws:
        ws.send_json({"type": "bogus"})
        assert ws.receive_json()["type"] == "error"
        ws.send_json({"type": "player_text", "text": "still there?"})
        assert read_turn(ws)[-1]["type"] == "npc_done"
