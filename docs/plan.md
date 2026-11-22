# Development plan (working copy)

Source: "PFA Simulator — Development Plan" and "Project Proposal" (Nov 22, 2026).
One developer, Dec 2026 – Jun 2027. Each step = 1–2 Claude Code sessions and ends with a runnable check.
Update the status column when a step is done.

Target hardware: **Meta Quest 2** (standalone, Unity 6 LTS + Meta XR SDK, Android build) and a
**MacBook M4, 16 GB** running all AI locally. Quest Link does not run on macOS, so every device test is a
build to the headset.

| Step | Deliverable | Done when | Status |
|---|---|---|---|
| **Phase 0 — Setup** (Nov 30 – Dec 6) ||||
| 0.1 | Monorepo, CLAUDE.md, .gitignore, Git LFS | pushed to GitHub | local commit pending |
| 0.2 | Python 3.11+, Ollama, 2–3 candidate 7–8B instruct models (manual) | `ollama run <model>` answers | partial (qwen3:8b only) |
| 0.3 | Unity 6 LTS + Android Build Support, URP project in `unity/`, Meta XR All-in-One SDK, Project Setup Tool fixes (manual) | empty scene on Quest 2 shows tracked hands | todo |
| **Phase 1 — Local AI server** (Dec 7 – Dec 27) ||||
| 1.1 | FastAPI WS server, streaming Ollama client, config, CLI, latency log | CLI streams reply + prints TTFT | **done** |
| 1.2 | Model benchmark: TTFT, tokens/s, staying in character | one model chosen, results in `docs/` | todo |
| 1.3 | STT: faster-whisper / whisper.cpp, audio chunks, VAD end-of-speech | 5 s WAV transcribed < 1 s | todo |
| 1.4 | TTS (e.g. Piper), sentence-by-sentence streaming | audio in → audio out from CLI, first audio ≤ ~1.5 s | todo |
| **Phase 2 — Stress engine + NPC brain** (Dec 28 – Jan 24) ||||
| 2.1 | Victim profile JSON schema | 3 profiles validated | todo |
| 2.2 | Deterministic stress engine (utterance labels + body signals → level, band, decay) | unit tests for every rule in the proposal table | todo |
| 2.3 | LLM utterance classifier (introduction, calming, open question, dismissive, blaming, instruction) → JSON | ≥ 90% agreement on 50 hand-labelled phrases | todo |
| 2.4 | NPC prompt from profile + band; short replies + emotion tag | replies clearly differ by band | todo |
| 2.5 | Web text playground with live stress | scripted good talk → Calm, bad → Acute | todo |
| **Phase 3 — VR foundation** (Jan 25 – Feb 28, exams) ||||
| 3.1 | Unity WS client; JSON events + binary audio frames | Quest ↔ Mac messages over Wi-Fi | todo |
| 3.2 | Mic capture, pinch push-to-talk, NPC-positioned reply audio | spoken question → spoken answer in headset | todo |
| 3.3 | Body signals (distance, head height vs NPC eyes, facing, open palm, touch) at 5–10 Hz | live debug panel | todo |
| 3.4 | Placeholder humanoid, idle per band, amplitude lip-sync | crouching + calm speech lower stress on panel | todo |
| **Phase 4 — Fire scenario slice** (Mar 1 – Apr 4) | 4.1 environment · 4.2 soundscape · 4.3 victim character · 4.4 interactions · 4.5 phrase dictionary · 4.6 scene logic | playable start to end, 3–5 testers | todo |
| **Phase 5 — Tutorial, debrief, safety** (Apr 5 – Apr 25) | 5.1 safe room · 5.2 scenario cards · 5.3 debrief · 5.4 content warning + pause/exit | | todo |
| **Phase 6 — Scenarios 2–3** (Apr 26 – May 30) | 6.1 road accident (aggression) · 6.2 two victims | | todo |
| **Phase 7 — Validation + polish** (May 31 – Jun 20) | 7.1 expert review · 7.2 user test · 7.3 72 fps + latency · 7.4 demo | | todo |

If Phase 3 slips, Phase 6 shrinks before Phase 4 does.
