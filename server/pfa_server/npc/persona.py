"""Load NPC personas (system prompts) from server/personas/<name>.md."""

from pathlib import Path


def load_persona(personas_dir: Path, name: str) -> str:
    path = personas_dir / f"{name}.md"
    if not path.is_file():
        raise FileNotFoundError(f"Persona '{name}' not found at {path}")
    return path.read_text(encoding="utf-8").strip()
