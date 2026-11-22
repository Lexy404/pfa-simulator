import pytest
from pydantic import ValidationError

from pfa_server.protocol import (
    Latency,
    NpcDone,
    NpcToken,
    PlayerText,
    parse_client_message,
    parse_server_message,
)


def test_parse_player_text():
    msg = parse_client_message('{"type": "player_text", "text": "Hi, I am here to help."}')
    assert isinstance(msg, PlayerText)
    assert msg.text == "Hi, I am here to help."


@pytest.mark.parametrize(
    "raw",
    [
        '{"type": "player_text"}',  # missing text
        '{"type": "player_text", "text": ""}',  # empty text
        '{"type": "unknown", "text": "x"}',  # unknown type
        '{"text": "x"}',  # no type
        "not json",
    ],
)
def test_invalid_client_messages(raw):
    with pytest.raises(ValidationError):
        parse_client_message(raw)


def test_server_messages_roundtrip():
    token = NpcToken(text="Help")
    done = NpcDone(text="Help me", latency=Latency(ttft_ms=120.0, total_ms=900.0))
    assert parse_server_message(token.model_dump_json()) == token
    assert parse_server_message(done.model_dump_json()) == done
    assert '"type":"npc_done"' in done.model_dump_json()
