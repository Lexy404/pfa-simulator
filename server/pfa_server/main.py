"""FastAPI app: GET /health and WebSocket /ws/session.

Run:  uvicorn pfa_server.main:app   (or `make run` from the repo root)
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from pfa_server.config import Settings, get_settings
from pfa_server.llm import LLMClient
from pfa_server.llm.ollama_client import OllamaClient
from pfa_server.npc.persona import load_persona
from pfa_server.protocol import ErrorMessage, PlayerText, parse_client_message
from pfa_server.session import Session

log = logging.getLogger("pfa_server")


def create_app(settings: Settings | None = None, llm: LLMClient | None = None) -> FastAPI:
    """Build the app. Tests pass a fake `llm`; otherwise an OllamaClient is created."""
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        owned = llm is None
        app.state.llm = llm or OllamaClient(settings.ollama_host, settings.ollama_model)
        app.state.system_prompt = load_persona(settings.personas_dir, settings.persona)
        log.info("model=%s persona=%s", settings.ollama_model, settings.persona)
        yield
        if owned:
            await app.state.llm.aclose()

    app = FastAPI(title="PFA Simulator server", lifespan=lifespan)

    @app.get("/health")
    async def health() -> dict:
        ollama_ok = await app.state.llm.ping()
        return {
            "status": "ok" if ollama_ok else "degraded",
            "ollama": ollama_ok,
            "model": settings.ollama_model,
        }

    @app.websocket("/ws/session")
    async def ws_session(ws: WebSocket) -> None:
        await ws.accept()
        session = Session(app.state.llm, app.state.system_prompt)
        log.info("session opened")
        try:
            while True:
                raw = await ws.receive_text()
                try:
                    msg = parse_client_message(raw)
                except ValidationError as e:
                    await ws.send_text(ErrorMessage(message=f"invalid message: {e}").model_dump_json())
                    continue

                if isinstance(msg, PlayerText):
                    try:
                        async for out in session.player_text(msg.text):
                            await ws.send_text(out.model_dump_json())
                    except WebSocketDisconnect:
                        raise
                    except Exception as e:  # LLM unreachable, model missing, ...
                        log.exception("turn failed")
                        await ws.send_text(ErrorMessage(message=f"turn failed: {e}").model_dump_json())
        except WebSocketDisconnect:
            log.info("session closed after %d turns", session.turn)

    return app


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
app = create_app()


def run() -> None:
    s = get_settings()
    uvicorn.run(app, host=s.host, port=s.port)


if __name__ == "__main__":
    run()
