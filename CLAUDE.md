# PFA Simulator

Year-long university VR project, solo developer. A **Meta Quest 2** app (Unity 6, hand tracking) that
trains ordinary people in Psychological First Aid (PFA). The player talks by voice to an AI-driven
victim NPC.

## Target device: Quest 2, built with Unity

- The client is a Unity 6 project in `unity/`, built for Android and deployed to a Quest 2 from Unity.
- Quest 2 is a mobile headset with limited CPU/GPU: the headset only captures input (mic, hands, head
  pose), renders and plays audio. All AI work (STT, classifier, stress engine, LLM, TTS) runs on the
  Mac server; never plan on-device models.
- Wire formats must be cheap to produce and parse on Quest 2 (small JSON messages, compact audio frames).

## Plan and current step

The step-by-step plan with "done when" checks and status lives in [docs/plan.md](docs/plan.md).
Work one plan step per session, finish with its check, then update the status column there.

## Core mechanic

Each victim has a **stress level 0–100**, with bands Calm 0–25, Anxious 26–50, Distressed 51–75,
Acute 76–100. It starts from the victim's physical and psychological condition and changes with the
player's words, gestures and eye level.

## Architecture

Quest app streams mic audio + body signals over WebSocket (Wi-Fi) to a local Python server on the Mac:

1. speech-to-text (Whisper)
2. utterance classifier (LLM): labels what the player said
3. **stress engine: deterministic Python, owns the stress value**
4. NPC reply: local LLM via Ollama, conditioned on persona, history and current stress
5. text-to-speech
6. audio + emotion tag back to the Quest

Latency target: first reply audio within ~1.5 s after the player stops speaking. Every stage
streams and runs locally; no cloud APIs.

### Hard rule: the stress engine is deterministic

The stress value is computed only by plain Python code from classifier labels and body signals.
LLMs may *classify* input and *voice* the NPC, but must never set, compute or adjust the stress
number. Stress engine logic must be pure and unit-testable (same inputs, same output).

## Repo layout

```
server/                 Python package (FastAPI + uvicorn), managed with uv
  pfa_server/
    config.py           Settings from env vars (prefix PFA_) / server/.env
    protocol.py         ALL WebSocket message schemas (Pydantic, discriminated by "type")
    llm/                LLMClient protocol + OllamaClient (async token streaming)
    npc/                persona loading
    session.py          per-connection conversation + turn pipeline + latency measurement
    main.py             FastAPI app: GET /health, WS /ws/session
  personas/             NPC system prompts, one <name>.md per persona
  tools/chat_cli.py     interactive text client for the WebSocket
  tests/                pytest
unity/                  Unity 6 project for Quest 2, Android build (not created yet)
docs/                   architecture notes
```

Planned modules plug in as separate subpackages next to `llm/` and `npc/` (e.g. `stt/`, `classifier/`,
`stress/`, `tts/`) and are wired together in `session.py`.

## Run and test

```bash
make install     # uv sync in server/
make run         # start server on PFA_HOST:PFA_PORT (default 0.0.0.0:8000), needs Ollama running
make cli         # text chat client (URL=ws://... to override)
make test        # pytest (Ollama is mocked; no server or model needed)
```

## Conventions

- Python 3.11+, type hints everywhere, async for all I/O.
- New WebSocket messages: add a Pydantic model with a unique `type` literal in `protocol.py` and
  include it in `ClientMessage` / `ServerMessage`. No ad-hoc dicts on the wire.
- External services (Ollama, later Whisper/TTS) sit behind small interfaces so tests can use fakes;
  tests never need a running Ollama.
- Keep modules small and readable; no features beyond the current task.
- Log one line per turn with latency (`ttft`, `total`); keep latency measurement in place when
  adding pipeline stages.
- Personas are prompt files, not code.
