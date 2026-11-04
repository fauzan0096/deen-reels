"""Posting state — kaun si story ja chuki hai."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

STATE_VERSION = 1


def _empty() -> dict:
    return {"version": STATE_VERSION, "posted": [], "history": []}


def load(path: Path) -> dict:
    if not path.exists():
        return _empty()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _empty()
    if not isinstance(data, dict):
        return _empty()
    data.setdefault("version", STATE_VERSION)
    data.setdefault("posted", [])
    data.setdefault("history", [])
    return data


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


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
