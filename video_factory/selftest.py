"""Pipeline ki tez jaanch — bina ffmpeg, bina internet.

Chalaiye:

    python -m video_factory.selftest

Kya dekhta hai:

- settings sahi hain (language, privacy, fonts, stories file)
- stories.json ke sab waqiyat poore hain (beats, hook, lesson, hawala)
- dono zubano ke liye script aur captions banti hain
- Roman mode me Urdu ka koi lafz bacha nahi, aur Arabic asal jaisa hai
- Roman dictionary me kaunse Urdu lafz chhoot rahe hain (talaffuz ke liye)

CI isi ko har push par chalata hai — is liye syntax ya import ki ghalti
render shuru hone se pehle hi pakdi jati hai.
"""

from __future__ import annotations

import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

from .config import ROOT, load_config
from .i18n import LANGS, get_lang
from .roman import URDU_RE, unknown_words
from .script_builder import build_script
from .stories import load_stories
from .talaffuz import WORDS as TALAFFUZ_WORDS
from .talaffuz import say as speak
from .thumbnail import thumbnail_text
from .visuals import IMAGE_SUFFIXES, build_captions

PRIVACY = {"public", "unlisted", "private"}
RATE = re.compile(r"^[+-]\d{1,2}%$")


class Result:
    def __init__(self) -> None:
        self.failed = 0
        self.warned = 0

    def ok(self, name: str, detail: str = "") -> None:
        print(f"OK    {name}" + (f" — {detail}" if detail else ""))

    def fail(self, name: str, detail: str) -> None:
        self.failed += 1
        print(f"FAIL  {name} — {detail}")

    def warn(self, name: str, detail: str) -> None:
        self.warned += 1
        print(f"WARN  {name} — {detail}")


def _check_settings(cfg, out: Result) -> None:
    if cfg.lang in LANGS:
        out.ok("VIDEO_LANG", f"{cfg.lang} (supported: {', '.join(sorted(LANGS))})")
    else:
        out.fail(
            "VIDEO_LANG",
            f"{cfg.lang!r} supported nahi — in me se koi ek: {', '.join(sorted(LANGS))}",
        )

    if cfg.privacy in PRIVACY:
        out.ok("PRIVACY", cfg.privacy)
    else:
        out.fail("PRIVACY", f"{cfg.privacy!r} — public, unlisted ya private hona chahiye")

    if RATE.match(cfg.tts_rate or ""):
        out.ok("TTS_RATE", cfg.tts_rate)
    else:
        out.warn("TTS_RATE", f"{cfg.tts_rate!r} ajeeb lagta hai — jaise '+0%' ya '-5%'")

    fonts = Path(ROOT) / "assets" / "fonts"
    missing = [
        name
        for name in ("NotoNaskhArabic-Regular.ttf", "NotoSans-Regular.ttf")
        if not (fonts / name).exists()
    ]
    if missing:
        out.fail("Fonts", "missing: " + ", ".join(missing))
    else:
        out.ok("Fonts", "Noto Naskh Arabic + Noto Sans")

    folder = Path(ROOT) / "assets" / "backgrounds"
    if folder.is_dir():
        pictures = [
            item
            for item in folder.iterdir()
            if item.is_file() and item.suffix.lower() in IMAGE_SUFFIXES
        ]
        out.ok("Background pictures", f"{len(pictures)} mili")

    voice = cfg.voice or ""
    if voice and not re.match(r"^[a-z]{2,3}-[A-Z]{2}-\w+Neural$", voice):
        out.warn("VOICE", f"{voice!r} naam ajeeb lagta hai")


def _check_talaffuz(out: Result) -> None:
    sample = speak("ابو بکر نے 13 برس خلافت کی۔")
    if "13" in sample:
        out.fail("Talaffuz", "adad Urdu lafz me nahi badle (13 waisa hi reh gaya)")
    elif "اَبُو بَکْر" not in sample:
        out.fail("Talaffuz", "naam par harakat nahi lagi")
    elif "۔" in sample:
        out.fail("Talaffuz", "Urdu full stop TTS ke liye saaf nahi hua")
    else:
        out.ok("Talaffuz", f"{len(TALAFFUZ_WORDS)} lafz harakat ke saath")


def _check_stories(stories, out: Result) -> None:
    if not stories:
        out.fail("Stories", "koi waqiya nahi mila")
        return

    out.ok("Stories", f"{len(stories)} waqiya, sab me hawala maujood")

    for story in stories:
        name = story["id"]
        if len(story["beats"]) < 2:
            out.warn(name, f"sirf {len(story['beats'])} beat — video bahut chhoti lagegi")
        if not story.get("hook"):
            out.warn(name, "hook khali hai")
        if not story.get("lesson"):
            out.warn(name, "lesson khali hai")
        if len(str(story["title"])) > 90:
            out.warn(name, "title lamba hai")
        for index, beat in enumerate(story["beats"]):
            if len(beat["urdu"]) < 20:
                out.warn(name, f"beat #{index + 1} bahut chhota hai")


def _check_script(story, cfg, out: Result) -> None:
    for code in sorted(LANGS):
        lang = get_lang(code)
        try:
            script = build_script(story, lang, cfg, 0)
        except Exception as exc:  # noqa: BLE001
            out.fail(f"Script ({code})", str(exc))
            continue

        if len(script.cards) < 3:
            out.fail(f"Script ({code})", f"sirf {len(script.cards)} card bane")
            continue
        if len(script.narration) < 120:
            out.fail(f"Script ({code})", "narration bahut chhoti hai")
            continue
        if len(script.title) > 100:
            out.fail(f"Script ({code})", f"title {len(script.title)} characters ka hai")
            continue
        out.ok(f"Script ({code})", f"{len(script.cards)} card, {len(script.title)} char title")

        hashtags = script.description.count("#")
        if hashtags < 3:
            out.warn(f"Hashtags ({code})", f"sirf {hashtags} hashtag — kam se kam 3 behtar")
        elif hashtags > 15:
            out.fail(f"Hashtags ({code})", f"{hashtags} hashtag — YouTube 15 se zyada ignore karta hai")
        else:
            out.ok(f"Hashtags ({code})", f"{hashtags} hashtag")

        try:
            payload = thumbnail_text(script, lang, cfg)
        except Exception as exc:  # noqa: BLE001
            out.fail(f"Thumbnail ({code})", str(exc))
        else:
            if "Dialogue:" in payload and "{font}" not in payload:
                out.ok(f"Thumbnail ({code})", "ASS taiyar")
            else:
                out.fail(f"Thumbnail ({code})", "ASS khaali ya placeholder bacha")

        if not lang.get("roman"):
            continue

        leftovers = [
            card.text for card in script.cards if URDU_RE.search(card.text or "")
        ]
        if URDU_RE.search(script.narration or ""):
            leftovers.append("(narration)")
        if leftovers:
            out.fail(
                f"Roman ({code})",
                "Urdu likhai bach gayi: " + ", ".join(item[:40] for item in leftovers[:3]),
            )
        else:
            out.ok(f"Roman ({code})", "koi Urdu harf nahi bacha")

        source_arabic = [beat for beat in story["beats"] if beat.get("arabic")]
        kept = [card for card in script.cards if card.arabic]
        if source_arabic and not kept:
            out.fail(f"Roman ({code})", "Arabic asal Roman me badal gaya — aisa nahi hona chahiye")
        elif source_arabic:
            out.ok(f"Roman ({code})", f"{len(kept)} Arabic asal jaisa hi hai")


def _check_captions(story, cfg, out: Result) -> None:
    for code in sorted(LANGS):
        lang = get_lang(code)
        script = build_script(story, lang, cfg, 0)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "captions.ass"
            try:
                build_captions(
                    script.cards,
                    30.0,
                    path,
                    header_text=lang.get("header_text") or cfg.channel_name,
                    title=script.title,
                    text_font=lang.get("text_font") or "Noto Naskh Arabic",
                )
                payload = path.read_text(encoding="utf-8")
            except Exception as exc:  # noqa: BLE001
                out.fail(f"Captions ({code})", str(exc))
                continue

        if "[Events]" not in payload or "Dialogue:" not in payload:
            out.fail(f"Captions ({code})", "caption file khaali hai")
        elif "{font}" in payload or "{" + "title" + "}" in payload:
            out.fail(f"Captions ({code})", "ASS template ka placeholder bacha reh gaya")
        else:
            font = lang.get("text_font") or "Noto Naskh Arabic"
            if font not in payload:
                out.fail(f"Captions ({code})", f"font {font!r} captions me nahi")
            else:
                out.ok(f"Captions ({code})", f"{payload.count('Dialogue:')} line, font {font}")


def _check_roman_coverage(stories, out: Result) -> None:
    counter: Counter = Counter()
    for story in stories:
        texts = [story["title"], story.get("hook", ""), story.get("lesson", "")]
        texts += [beat["urdu"] for beat in story["beats"]]
        for text in texts:
            counter.update(unknown_words(text))

    total = sum(counter.values())
    if not total:
        out.ok("Roman dictionary", "saare lafz dictionary me hain")
        return

    common = ", ".join(f"{word} ({count})" for word, count in counter.most_common(12))
    if total > 60:
        out.warn(
            "Roman dictionary",
            f"{total} lafz dictionary me nahi — inhe content/roman.json me daal dein: {common}",
        )
    else:
        out.ok("Roman dictionary", f"{total} lafz fallback par hain: {common}")


def main() -> int:
    cfg = load_config()
    out = Result()

    _check_settings(cfg, out)
    _check_talaffuz(out)

    stories_path = Path(ROOT) / "content" / "stories.json"
    if stories_path.exists():
        out.ok("stories.json", str(stories_path.relative_to(ROOT)))
    else:
        out.fail("stories.json", f"nahi mila: {stories_path}")
        return _finish(out)

    try:
        stories = load_stories(stories_path)
    except Exception as exc:  # noqa: BLE001
        out.fail("stories.json", str(exc))
        return _finish(out)

    _check_stories(stories, out)
    _check_script(stories[0], cfg, out)
    _check_captions(stories[0], cfg, out)
    _check_roman_coverage(stories, out)

    return _finish(out)


def _finish(out: Result) -> int:
    print()
    if out.failed:
        print(f"Nateeja: {out.failed} fail, {out.warned} warning — pipeline theek karni hai.")
        return 1
    if out.warned:
        print(f"Nateeja: sab theek, {out.warned} warning (chala sakte hain).")
        return 0
    print("Nateeja: sab theek.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
