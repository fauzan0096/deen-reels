"""Story se narration aur on-screen cards banata hai.

Story ka text content/stories.json se aata hai (har story ke saath uska
hawala hota hai). Ye module sirf usko video ke liye tarteeb deta hai.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from .config import Config

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


# Sunne me talaffuz theek aaye — sirf awaaz ke liye. Screen par Urdu hi rehta hai.
_PRONOUNCE = [
    ("ابن ابی قحافہ", "ابنِ اَبی قُحافَہ"),
    ("ابو بکر صدیق", "اَبُو بَکْر صِدِّیق"),
    ("ابی قحافہ", "اَبی قُحافہ"),
    ("یا رسول اللہ", "یا رَسُولَ اللہ"),
    ("رسول اللہ", "رَسُولَ اللہ"),
    ("عمر بن خطاب", "عُمَر بِن خَطّاب"),
    ("عثمان بن عفان", "عُثمان بِن عَفّان"),
    ("علی بن ابی طالب", "عَلی بِن اَبی طالِب"),
    ("صدیق", "صِدِّیق"),
    ("فاروق", "فارُوق"),
    ("رضی اللہ عنہم", "رَضِیَ اللہُ عَنہُم"),
    ("رضی اللہ عنہما", "رَضِیَ اللہُ عَنہُما"),
    ("رضی اللہ عنہا", "رَضِیَ اللہُ عَنہا"),
    ("رضی اللہ عنہ", "رَضِیَ اللہُ عَنہُ"),
    ("عبد اللہ", "عَبدُ اللہ"),
    ("ابو بکر", "اَبُو بَکْر"),
    ("ورثة الانبياء", "وَرَثَةُ الْاَنْبِیَاء"),
    ("قرآن", "قُرْآن"),
]

# Aakhri line me "سبسکرائب" — beech wale cards se hata diya jata hai.
_SUBSCRIBE = re.compile(r"[^۔]*سبسکرائب[^۔]*۔?")


def _speak(text: str) -> str:
    if not text:
        return text
    for urdu, arabic in _PRONOUNCE:
        text = text.replace(urdu, arabic)
    return text


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
    hook = _sentence(_honorifics(story.get("hook") or story.get("subtitle")))
    beats = [_sentence(_honorifics(beat.get("urdu"))) for beat in story.get("beats", [])]
    lesson = _sentence(_honorifics(story.get("lesson")))
    closing = _sentence(lang["closing"])
    cta = _sentence(lang["cta"])
    citation = source_line(story)
    story_title = _honor_title(story["title"])

    intro = _sentence(
        lang["intro_template"].format(
            channel=lang.get("channel_spoken") or cfg.channel_name
        )
    )
    outro = _sentence(_pick_outro(lang, ordinal))

    # Pehla screen: intro + hook saath me bola jata hai.
    opening = " ".join(part for part in (intro, hook) if part)
    spoken_parts = [opening] + beats + [lesson, closing, outro]
    narration = " ".join(part for part in spoken_parts if part)

    cards: List[Card] = [
        Card(
            text=story_title,
            sub=hook,
            label=lang["label_story"],
            spoken=_speak(opening or story_title),
        )
    ]
    for beat in story.get("beats", []):
        body = _sentence(beat.get("urdu"))
        cards.append(
            Card(
                text=body,
                arabic=beat.get("arabic", ""),
                label=beat.get("label", ""),
                spoken=_speak(body),
            )
        )
    cards.append(Card(text=lesson, label=lang["label_lesson"], spoken=_speak(lesson)))
    cards.append(Card(text=closing, spoken=_speak(closing)))
    # Beech ke cards par subscribe ki baat nahi — wo sirf aakhri line me.
    next_hint = _sentence(_SUBSCRIBE.sub("", story.get("next_hint") or "").strip())
    if next_hint:
        cards.append(Card(text=next_hint, spoken=_speak(next_hint)))
    cards.append(Card(text=outro, sub=cta, footer=citation, spoken=_speak(outro)))

    title = _safe_title(f"{story_title} | {cfg.channel_name} #Shorts")
    if len(title) > 100:
        title = _safe_title(f"{story_title} #Shorts")[:100]

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
