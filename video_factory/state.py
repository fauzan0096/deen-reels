"""Posting state — kaun si story ja chuki hai.

state.json kharab ho jaye to chup chaap reset karna sabse bara khatra hai:
pipeline samajh leti hai ke kuch post nahi hua aur saari stories dobara chali
jati hain. Is liye kharab file par saaf error aata hai, reset nahi hota.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

STATE_VERSION = 1


class StateError(RuntimeError):
    """state.json padhi nahi ja saki — ise haath se theek karna hoga."""


def _empty() -> dict:
    return {"version": STATE_VERSION, "posted": [], "history": []}


def load(path: Path) -> dict:
    if not path.exists():
        return _empty()

    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return _empty()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise StateError(
            f"state.json kharab hai ({path}): {exc}. Ise theek kijiye ya delete "
            "kijiye — kharab file ko reset karna wahi stories dobara post kar dega."
        ) from exc

    if not isinstance(data, dict):
        raise StateError(f"state.json me object hona chahiye, mila: {type(data).__name__}")

    data.setdefault("version", STATE_VERSION)
    data.setdefault("posted", [])
    data.setdefault("history", [])
    if not isinstance(data["posted"], list) or not isinstance(data["history"], list):
        raise StateError("state.json me 'posted' aur 'history' list honi chahiye")
    return data


def save(path: Path, data: dict) -> None:
    """Pehle temp file, phir replace — beech me run ruk jaye to file adhoori na ho."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temp.replace(path)


def mark_posted(state: dict, story_id: str, meta: Optional[dict] = None) -> None:
    posted = state.setdefault("posted", [])
    if story_id not in posted:
        posted.append(story_id)
    state.setdefault("history", []).append(
        {
            "id": story_id,
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            **(meta or {}),
        }
    )
