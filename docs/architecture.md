# Architecture

```
Meta Quest 2 (Unity 6 app, Android build, hand tracking)
  │  mic audio + body signals (gestures, eye level)        WebSocket over Wi-Fi
  ▼
Python server on the Mac (server/)
  1. Speech-to-text (Whisper)            audio  -> player text
  2. Utterance classifier (LLM)          text   -> labels (e.g. empathy, order, promise)
  3. Stress engine (deterministic Python) labels + body signals -> stress 0–100
  4. NPC reply (local LLM via Ollama)    persona + history + stress -> streamed text
  5. Text-to-speech                      text   -> audio
  │  audio + emotion tag + stress update
  ▼
Meta Quest 2 (plays voice, animates NPC)
```

Stress bands: Calm 0–25, Anxious 26–50, Distressed 51–75, Acute 76–100.

Latency target: first NPC audio within ~1.5 s after the player stops speaking.
Every stage streams and runs locally.

## Status

| Stage | Status |
|---|---|
| WebSocket protocol, text turns | done (`/ws/session`, `player_text` -> `npc_token`* -> `npc_done`) |
| NPC LLM via Ollama | done (streaming) |
| STT, classifier, stress engine, TTS | not started |
| Unity client (Quest 2) | not started |
