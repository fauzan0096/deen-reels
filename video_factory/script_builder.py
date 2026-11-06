"""Story se narration aur on-screen cards banata hai.

Story ka text content/stories.json se aata hai (har story ke saath uska
hawala hota hai). Ye module sirf usko video ke liye tarteeb deta hai.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from .config import Config
from .roman import to_roman
from .talaffuz import say as _speak

SENTENCE_END = "۔"
_ENDINGS = "۔.!?؟:؛"

_PROPHET = re.compile(r"(رسول اللہ|نبی اللہ)(?![^۔]{0,3}ﷺ)")
_SAHABI_MARK = "رضی اللہ"


def _honorifics(text: str) -> str:
    """رسول اللہ کے بعد ﷺ، اور awaaz bhi usay parh sake — is liye poora likha jata hai."""
    if not text:
        return text
    text = _PROPHET.sub(r"\1 ﷺ", text)
    # TTS "ﷺ" nahi bolta, is liye lafzon me likh dete hain.
    return text.replace("ﷺ", "صلی اللہ علیہ وسلم")


def _honor_title(title: str) -> str:
    if _SAHABI_MARK in title:
        return title
    return f"{title} رضی اللہ عنہ" if title else title


# Talaffuz ki poori list `video_factory/talaffuz.py` me hai.
# Aakhri line me "سبسکرائب" — beech wale cards se hata diya jata hai.
_SUBSCRIBE = re.compile(r"[^۔]*سبسکرائب[^۔]*۔?")


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


# Har sahabi ke apne hashtag — YouTube/Instagram par topic saaf rahe.
_SAHABI_HASHTAGS = (
    ("abu-bakr", ["#AbuBakr", "#Siddiq"]),
    ("umar", ["#Umar", "#Farooq"]),
)


def _hashtags(story: dict, lang: dict, ordinal: int) -> list:
    """Bhasha ke hashtags + sahabi ka naam + hissa number (duplicate hata kar)."""
    tags = list(lang.get("hashtags") or [])
    story_id = str(story.get("id", "")).lower()
    for prefix, extra in _SAHABI_HASHTAGS:
        if story_id.startswith(prefix):
            tags.extend(extra)
            break
    tags.append(f"#Part{ordinal + 1}")

    unique: list = []
    for tag in tags:
        if tag and tag not in unique:
            unique.append(tag)
    return unique[:8]


def _pieces(text: str, minimum: int = 70) -> List[str]:
    """Beat ko chhote jumlon me todta hai.

    Shorts me screen par text jaldi badalna chahiye — ek hi lambe card par
    20 second tak rukna log scroll kar dete hain.
    """
    text = (text or "").strip()
    if not text:
        return []

    chunks = [part.strip() for part in re.split(r"(?<=۔)", text) if part.strip()]
    pieces: List[str] = []
    current = ""
    for chunk in chunks:
        if chunk and len(chunk) < minimum and not current:
            current = chunk
        elif current and len(current) < minimum:
            current = f"{current} {chunk}"
        else:
            if current:
                pieces.append(current)
            current = chunk
    if current:
        pieces.append(current)
    return pieces


def _title(hook: str, story_title: str) -> str:
    """Title me hook — story ka naam nahi. Hook hi click karata hai."""
    for head in (hook, story_title):
        text = _safe_title(f"{head} #Shorts")
        if len(text) <= 100:
            return text
    return _safe_title(f"{story_title} #Shorts")[:100]


def build_script(story: dict, lang: dict, cfg: Config, ordinal: int) -> Script:
    hook = _sentence(_honorifics(story.get("hook") or story.get("subtitle")))
    beats = [_sentence(_honorifics(beat.get("urdu"))) for beat in story.get("beats", [])]
    lesson = _sentence(_honorifics(story.get("lesson")))
    closing = _sentence(lang["closing"])
    cta = _sentence(lang["cta"])
    citation = source_line(story)
    story_title = _honor_title(story["title"])

    outro = _sentence(_pick_outro(lang, ordinal))

    # Hook sab se pehle — shuru ke 3 second me asli baat. "Khush aamdeed"
    # wali intro hata di gayi hai: wo pehle 3 second kha jati thi.
    cards: List[Card] = [
        Card(
            text=hook or story_title,
            sub=story_title,
            label=lang["label_story"],
            spoken=_speak(hook or story_title),
        )
    ]
    for beat in story.get("beats", []):
        for index, piece in enumerate(_pieces(beat.get("urdu"))):
            cards.append(
                Card(
                    text=piece,
                    arabic=beat.get("arabic", "") if index == 0 else "",
                    label=beat.get("label", "") if index == 0 else "",
                    spoken=_speak(piece),
                )
            )
    cards.append(Card(text=lesson, label=lang["label_lesson"], spoken=_speak(lesson)))
    cards.append(Card(text=closing, spoken=_speak(closing)))
    # Beech ke cards par subscribe ki baat nahi — wo sirf aakhri line me.
    next_hint = _sentence(_SUBSCRIBE.sub("", story.get("next_hint") or "").strip())
    if next_hint:
        cards.append(Card(text=next_hint, spoken=_speak(next_hint)))
    cards.append(Card(text=outro, sub=cta, footer=citation, spoken=_speak(outro)))

    narration = " ".join(card.spoken for card in cards if card.spoken)

    title = _title(hook, story_title)

    hashtags = _hashtags(story, lang, ordinal)
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
            " ".join(hashtags),
        ]
    ).strip()[:4900]

    tags = list(lang["tags"])
    tags += [tag.lstrip("#") for tag in hashtags[:4]]
    tags += [lang.get("header_text") or cfg.channel_name, "seerah", "sahaba"]
    tags = [tag for index, tag in enumerate(tags) if tag and tag not in tags[:index]]

    # Roman mode (VIDEO_LANG=hi): wahi text, sirf likhai Latin me — taake
    # Hindi awaaz usay theek parhe. Arabic asal (card.arabic) jaisa hai waisa
    # hi rehta hai, wo kabhi Roman nahi hota.
    if lang.get("roman"):
        for card in cards:
            card.text = to_roman(card.text)
            card.sub = to_roman(card.sub)
            card.label = to_roman(card.label)
            card.footer = to_roman(card.footer)
            card.spoken = to_roman(card.spoken)
        narration = to_roman(narration)
        title = to_roman(title)
        description = to_roman(description)

    return Script(
        narration=narration,
        cards=cards,
        title=title,
        description=description,
        tags=tags,
    )
