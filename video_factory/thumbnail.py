"""Thumbnail — hook wala frame + bara title, 1280x720.

YouTube ko custom thumbnail 16:9 chahiye (1280x720, 2 MB se kam). Vertical
video ka beech ka hissa crop hota hai, phir usi libass se likha jata hai jo
captions likhta hai — is liye Urdu/Arabic shaping theek rehti hai (PIL nahi
kar sakta).
"""

from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

from .config import Config
from .render import ensure_tools, media_duration
from .script_builder import Script

THUMB_W = 1280
THUMB_H = 720
MAX_BYTES = 2 * 1024 * 1024
MIN_BYTES = 20_000

ASS = """[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Header,{font},34,&HCCFFFFFF,&H00FFFFFF,&H00120F0A,&H00000000,0,0,0,0,100,100,2,0,1,2,1,7,40,40,0,1
Style: Title,{font},74,&H00FFFFFF,&H00808080,&H00120F0A,&H96000000,0,0,0,0,100,100,0,0,1,4,3,5,60,60,0,1
Style: Arabic,Noto Naskh Arabic,42,&H00F5E9D0,&H000000FF,&H00120F0A,&H96000000,0,0,0,0,100,100,0,0,1,3,2,5,60,60,0,1
Style: Sign,{font},30,&H80E6EEF2,&H000000FF,&H00120F0A,&H00000000,0,0,0,0,100,100,1,0,1,1,0,3,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
{dialogues}
"""


def _clean(text: str) -> str:
    return (
        (text or "")
        .replace("{", "")
        .replace("}", "")
        .replace("\r", " ")
        .replace("\n", " ")
        .strip()
    )


def _wrap(text: str, width: int) -> str:
    lines = textwrap.wrap(_clean(text), width=width) or [""]
    return "\\N".join(lines)


def _dialogue(style: str, position: str, text: str) -> str:
    return (
        "Dialogue: 0,0:00:00.00,0:00:10.00,"
        f"{style},,0,0,0,,{{\\an{position}}}{text}"
    )


def thumbnail_text(script: Script, lang: dict, cfg: Config) -> str:
    """Thumbnail ka poora ASS — ffmpeg ke `ass` filter ko dene ke liye."""
    header = _wrap(lang.get("header_text") or cfg.channel_name, 30)
    title = _wrap(script.cards[0].text if script.cards else script.title, 24)

    arabic = ""
    for card in script.cards:
        if card.arabic and len(_clean(card.arabic)) <= 90:
            arabic = _wrap(card.arabic, 40)
            break

    dialogues = [
        _dialogue("Header", "7", header),
        _dialogue("Title", "5\\pos(640,320)", title),
    ]
    if arabic:
        dialogues.append(_dialogue("Arabic", "5\\pos(640,470)", arabic))
    dialogues.append(_dialogue("Sign", "3\\pos(1240,690)", _wrap(script.title, 40)))

    return ASS.format(
        width=THUMB_W,
        height=THUMB_H,
        font=lang.get("text_font") or "Noto Naskh Arabic",
        dialogues="\n".join(dialogues),
    )


def build_thumbnail(
    video: Path,
    script: Script,
    lang: dict,
    cfg: Config,
    output: Path,
    at: float = 1.5,
) -> Path:
    """Video ke hook wale frame se 1280x720 JPG thumbnail banata hai."""
    ensure_tools()
    if not video.exists():
        raise RuntimeError(f"Thumbnail ke liye video nahi mili: {video}")

    duration = media_duration(video)
    moment = max(0.4, min(at, duration * 0.3 if duration else at))

    output.parent.mkdir(parents=True, exist_ok=True)
    ass_path = output.with_suffix(".ass")
    ass_path.write_text(thumbnail_text(script, lang, cfg), encoding="utf-8")

    fonts = Path("assets") / "fonts"
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{moment:.2f}",
        "-i",
        str(video),
        "-frames:v",
        "1",
        "-vf",
        (
            f"scale={THUMB_W}:{THUMB_H}:force_original_aspect_ratio=increase,"
            f"crop={THUMB_W}:{THUMB_H},"
            f"ass={ass_path}:fontsdir={fonts}"
        ),
        "-q:v",
        "3",
        str(output),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0 or not output.exists():
        raise RuntimeError(
            "Thumbnail ban nahi payi: " + (completed.stderr or "")[-800:]
        )

    size = output.stat().st_size
    if size < MIN_BYTES:
        raise RuntimeError(f"Thumbnail bahut chhoti hai ({size} bytes)")
    if size > MAX_BYTES:
        # YouTube 2 MB se bara thumbnail nahi leta — dobara zyada compress.
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(output),
                "-q:v",
                "6",
                str(output),
            ],
            capture_output=True,
            text=True,
        )
        if output.stat().st_size > MAX_BYTES:
            raise RuntimeError("Thumbnail 2 MB se chhoti nahi ho payi")

    ass_path.unlink(missing_ok=True)
    return output
