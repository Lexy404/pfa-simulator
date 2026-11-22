# PFA Simulator

A Meta Quest 2 VR app that trains ordinary people in Psychological First Aid: the player talks by voice
to an AI-driven victim NPC whose stress level reacts to what they say and do.

This repository holds the local Python server (`server/`) and, later, the Unity 6 project (`unity/`)
that is built for Android and deployed to Quest 2 from Unity. The headset only captures input and
renders; all AI processing runs on the server.
See [docs/architecture.md](docs/architecture.md) for the pipeline.

## Requirements

- macOS (Apple Silicon) or Linux
- Python 3.11+ and [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com) with a chat model pulled:
  ```bash
  ollama pull qwen3:4b-instruct-2507-q4_K_M
  ```
- Git LFS for Unity assets: `brew install git-lfs && git lfs install`

## Setup

```bash
make install                      # creates server/.venv and installs dependencies
cp server/.env.example server/.env   # optional: change model, host, port, persona
```

## Run

```bash
make run          # server on 0.0.0.0:8000
make cli          # in a second terminal: type lines, see streamed NPC replies + latency
make test         # pytest
```

Check the server and Ollama: `curl http://localhost:8000/health`.

To connect from another machine (e.g. the Quest), use the Mac's LAN IP:
`make cli URL=ws://192.168.x.x:8000/ws/session`.

## Configuration

Environment variables (or `server/.env`):

| Variable | Default |
|---|---|
| `PFA_OLLAMA_HOST` | `http://localhost:11434` |
| `PFA_OLLAMA_MODEL` | `qwen3:4b-instruct-2507-q4_K_M` |
| `PFA_HOST` | `0.0.0.0` |
| `PFA_PORT` | `8000` |
| `PFA_PERSONA` | `burning_building` (file in `server/personas/`) |

## WebSocket protocol (`/ws/session`)

Client -> server:
```json
{"type": "player_text", "text": "Hi, my name is Alex. I'm here to help."}
```
Server -> client (streamed):
```json
{"type": "npc_token", "text": "Who"}
{"type": "npc_done", "text": "Who are you?", "latency": {"ttft_ms": 310.2, "total_ms": 1240.8}}
{"type": "error", "message": "..."}
```
Schemas live in `server/pfa_server/protocol.py`.
