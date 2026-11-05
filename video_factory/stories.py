"""Stories (waqiyat) load aur validate karta hai.

Har story ek JSON object hai. Video usi se banti hai, isliye har story ka
source dena lazmi hai — bina hawale wali story load hi nahi hogi.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Tuple

REQUIRED_KEYS = ("id", "title", "beats", "source")


class StoryError(ValueError):
    """Story file me kuch galat hai."""


def _validate(story: dict, index: int) -> dict:
    where = f"stories[{index}]"
    for key in REQUIRED_KEYS:
        if key not in story:
            raise StoryError(f"{where}: '{key}' missing hai")

    story_id = str(story["id"]).strip()
    if not story_id:
        raise StoryError(f"{where}: id khali hai")

    title = str(story["title"]).strip()
    if not title:
        raise StoryError(f"{where} ({story_id}): title khali hai")

    beats = story["beats"]
    if not isinstance(beats, list) or not beats:
        raise StoryError(f"{where} ({story_id}): beats khali hai")
    for beat_index, beat in enumerate(beats):
        if not isinstance(beat, dict) or not str(beat.get("urdu", "")).strip():
            raise StoryError(f"{where} ({story_id}) beat #{beat_index + 1}: 'urdu' chahiye")

    source = story["source"]
    if not isinstance(source, dict):
        raise StoryError(f"{where} ({story_id}): source object hona chahiye")
    for field in ("book", "ref"):
        if not str(source.get(field, "")).strip():
            raise StoryError(f"{where} ({story_id}): source.{field} khali hai")

    return {
        "id": story_id,
        "title": title,
        "subtitle": str(story.get("subtitle", "")).strip(),
        "hook": str(story.get("hook", "")).strip(),
        "beats": [
            {
                "label": str(beat.get("label", "")).strip(),
                "urdu": str(beat.get("urdu", "")).strip(),
                "arabic": str(beat.get("arabic", "")).strip(),
            }
            for beat in beats
        ],
        "lesson": str(story.get("lesson", "")).strip(),
        # Agla hissa aane wala ho to screen par us ki targheeb.
        "next_hint": str(story.get("next_hint", "")).strip(),
        "source": {
            "book": str(source.get("book", "")).strip(),
            "author": str(source.get("author", "")).strip(),
            "ref": str(source.get("ref", "")).strip(),
            "note": str(source.get("note", "")).strip(),
        },
    }


def load_stories(path: Path) -> List[dict]:
    if not path.exists():
        raise StoryError(f"Stories file nahi mili: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("stories") if isinstance(data, dict) else data
    if not isinstance(items, list) or not items:
        raise StoryError(f"{path} me 'stories' list khali ya galat hai")

    stories = [_validate(story, index) for index, story in enumerate(items)]

    seen = set()
    for story in stories:
        if story["id"] in seen:
            raise StoryError(f"Duplicate story id: {story['id']}")
        seen.add(story["id"])

    return stories


def next_story(
    stories: List[dict], state: dict
) -> Tuple[Optional[dict], Optional[int]]:
    posted = set(state.get("posted") or [])
    for ordinal, story in enumerate(stories):
        if story["id"] not in posted:
            return story, ordinal
    return None, None
