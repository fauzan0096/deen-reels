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


_ARABIC_TO_ENGLISH_DIGITS = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"
)


def source_line(story: dict) -> str:
    """Hawala: kitab ka naam Arabic me, sirf hadees/dafa numbers English digits me."""
    source = story.get("source") or {}
    book = str(source.get("book", "")).strip()
    ref = str(source.get("ref", "")).translate(_ARABIC_TO_ENGLISH_DIGITS)

    if book and ref:
        return f"{book} — {ref}"
    return book or ref


def _safe_title(text: str) -> str:
    return text.replace("<", "").replace(">", "").strip()


def _pick_outro(lang: dict, ordinal: int) -> str:
    lines = lang.get("outro_lines") or []
    if not lines:
        return lang.get("cta", "")
    return lines[ordinal % len(lines)]


def build_script(story: dict, lang: dict, cfg: Config, ordinal: int) -> Script:
    hook = _sentence(story.get("hook") or story.get("subtitle"))
    beats = [_sentence(beat.get("urdu")) for beat in story.get("beats", [])]
    lesson = _sentence(story.get("lesson"))
    closing = _sentence(lang["closing"])
    cta = _sentence(lang["cta"])
    citation = source_line(story)

    intro = _sentence(lang["intro_template"].format(channel=cfg.channel_name))
    outro = _sentence(_pick_outro(lang, ordinal))

    # Pehla screen: intro + hook saath me bola jata hai.
    opening = " ".join(part for part in (intro, hook) if part)
    spoken_parts = [opening] + beats + [lesson, closing, outro]
    narration = " ".join(part for part in spoken_parts if part)

    cards: List[Card] = [
        Card(
            text=story["title"],
            sub=hook,
            label=lang["label_story"],
            spoken=opening or story["title"],
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
    cards.append(Card(text=closing, footer=citation, spoken=closing))
    # Aakhir me marketing line.
    cards.append(Card(text=outro, sub=cta, spoken=outro))

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
            outro,
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
