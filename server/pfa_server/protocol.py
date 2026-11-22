"""WebSocket message schemas for /ws/session.

Every message is a JSON object with a "type" field. To add a new message
(audio_frame, body_signals, stress_update, emotion_tag, ...), define a model
with a unique `type` literal and add it to ClientMessage or ServerMessage.
"""

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter

# ---------- client -> server ----------


class PlayerText(BaseModel):
    type: Literal["player_text"] = "player_text"
    text: str = Field(min_length=1)


ClientMessage = Annotated[Union[PlayerText], Field(discriminator="type")]

# ---------- server -> client ----------


class NpcToken(BaseModel):
    type: Literal["npc_token"] = "npc_token"
    text: str


class Latency(BaseModel):
    ttft_ms: float  # player message received -> first NPC token
    total_ms: float  # player message received -> last NPC token


class NpcDone(BaseModel):
    type: Literal["npc_done"] = "npc_done"
    text: str  # full NPC reply
    latency: Latency


class ErrorMessage(BaseModel):
    type: Literal["error"] = "error"
    message: str


ServerMessage = Annotated[
    Union[NpcToken, NpcDone, ErrorMessage], Field(discriminator="type")
]

client_message_adapter: TypeAdapter[ClientMessage] = TypeAdapter(ClientMessage)
server_message_adapter: TypeAdapter[ServerMessage] = TypeAdapter(ServerMessage)


def parse_client_message(raw: str | bytes) -> ClientMessage:
    """Parse and validate a JSON message from the client. Raises pydantic.ValidationError."""
    return client_message_adapter.validate_json(raw)


def parse_server_message(raw: str | bytes) -> ServerMessage:
    """Parse and validate a JSON message from the server (used by clients and tests)."""
    return server_message_adapter.validate_json(raw)
