"""Story se narration aur on-screen cards banata hai.

Story ka text content/stories.json se aata hai (har story ke saath uska
hawala hota hai). Ye module sirf usko video ke liye tarteeb deta hai.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .config import Config

SENTENCE_END = "۔"
_ENDINGS = "۔.!?؟:؛"


@dataclass
class Card:
    """Video ka ek screen.

    text   — bara text jo screen par dikhta hai
    sub    — uske neeche chhota text (hook / CTA)
    arabic — upar Arabic asal (agar ho)
    label  — chhota heading (jaise 'سبق')
    footer — sabse neeche (hawala)
    spoken — is card ke dauraan jo bolа jata hai (timing ke liye)
    """

    text: str = ""
    sub: str = ""
    arabic: str = ""
    label: str = ""
    footer: str = ""
    spoken: str = ""


@dataclass
class Script:
    narration: str
    cards: List[Card] = field(default_factory=list)
    title: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)


def _sentence(text: Optional[str]) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    if text[-1] not in _ENDINGS:
        text += SENTENCE_END
    return text


def source_line(story: dict) -> str:
    source = story.get("source") or {}
    book = source.get("book", "")
    ref = source.get("ref", "")
    if book and ref:
        return f"{book} — {ref}"
    return book or ref


def _safe_title(text: str) -> str:
    return text.replace("<", "").replace(">", "").strip()


def build_script(story: dict, lang: dict, cfg: Config, ordinal: int) -> Script:
    hook = _sentence(story.get("hook") or story.get("subtitle"))
    beats = [_sentence(beat.get("urdu")) for beat in story.get("beats", [])]
    lesson = _sentence(story.get("lesson"))
    closing = _sentence(lang["closing"])
    cta = _sentence(lang["cta"])
    citation = source_line(story)

    spoken_parts = [hook] + beats + [lesson, closing]
    narration = " ".join(part for part in spoken_parts if part)

    cards: List[Card] = [
        Card(
            text=story["title"],
            sub=hook,
            label=lang["label_story"],
            spoken=hook or story["title"],
        )
    ]
    for beat in story.get("beats", []):
        cards.append(
            Card(
                text=_sentence(beat.get("urdu")),
                arabic=beat.get("arabic", ""),
                spoken=_sentence(beat.get("urdu")),
            )
        )
    cards.append(Card(text=lesson, label=lang["label_lesson"], spoken=lesson))
    cards.append(
        Card(text=closing, sub=cta, label="", footer=citation, spoken=closing)
    )

    title = _safe_title(f"{story['title']} | {cfg.channel_name} #Shorts")
    if len(title) > 100:
        title = _safe_title(f"{story['title']} #Shorts")[:100]

    description = "\n".join(
        [
            hook,
            "",
            *[f"• {beat}" for beat in beats if beat],
            "",
            lesson,
            "",
            f"({lang['label_source']}: {citation})",
            "",
            lang["daily_line"],
            cta,
            "",
            " ".join(lang["hashtags"]),
        ]
    ).strip()[:4900]

    tags = list(lang["tags"]) + [cfg.channel_name, "seerah", "sahaba"]

    return Script(
        narration=narration,
        cards=cards,
        title=title,
        description=description,
        tags=tags,
    )
