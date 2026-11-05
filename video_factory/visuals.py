"""Background scene, logo, aura narration ke saath synced (karaoke) captions.

Scene: raat ka sehra — sitare, hilal, ret ke tiley, khajoor ke darakht aur
door ek basti ka silhouette. Koi insaan nahi, bas us zamane ka mahaul.

Urdu/Arabic shaping libass karta hai, isliye text ASS me likhte hain aur
ffmpeg ke `ass` filter se burn karte hain. Fonts `assets/fonts` se aate hain.
"""

from __future__ import annotations

import math
import random
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFilter

from .config import HEIGHT, WIDTH
from .script_builder import Card

CONTENT_CENTER = 960

ASS_HEADER = """[Script Info]
Title: {title}
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Header,Noto Naskh Arabic,32,&HCCFFFFFF,&H00FFFFFF,&H00120F0A,&H00000000,0,0,0,0,100,100,2,0,1,2,1,7,55,55,0,1
Style: Label,Noto Naskh Arabic,36,&H99E6EEF2,&H000000FF,&H00120F0A,&H00000000,0,0,0,0,100,100,2,0,1,2,1,5,50,50,0,1
Style: Title,Noto Naskh Arabic,84,&H00FFFFFF,&H00808080,&H00120F0A,&H96000000,0,0,0,0,100,100,0,0,1,4,3,5,50,50,0,1
Style: Arabic,Noto Naskh Arabic,56,&H00F5E9D0,&H000000FF,&H00120F0A,&H96000000,0,0,0,0,100,100,0,0,1,3,2,5,50,50,0,1
Style: Body,Noto Naskh Arabic,62,&H00FFFFFF,&H008A8A8A,&H00120F0A,&H96000000,0,0,0,0,100,100,0,0,1,3,2,5,50,50,0,1
Style: Sub,Noto Naskh Arabic,44,&HCCE6EEF2,&H008A8A8A,&H00120F0A,&H00000000,0,0,0,0,100,100,0,0,1,2,1,5,50,50,0,1
Style: Footer,Noto Naskh Arabic,30,&H99D9E2E6,&H000000FF,&H00120F0A,&H00000000,0,0,0,0,100,100,1,0,1,2,1,5,50,50,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


# ---------------------------------------------------------------- background


def _palm(draw: ImageDraw.ImageDraw, x: float, base_y: float, height: float, colour) -> None:
    trunk: List[Tuple[float, float]] = []
    for index in range(0, 21):
        t = index / 20
        trunk.append((x + 18 * math.sin(t * 1.6) - 6 * t, base_y - height * t))
    draw.line(trunk, fill=colour, width=13, joint="curve")

    top_x, top_y = trunk[-1]
    for angle in range(-165, -10, 22):
        rad = math.radians(angle)
        draw.line(
            [(top_x, top_y), (top_x + 125 * math.cos(rad), top_y + 125 * math.sin(rad))],
            fill=colour,
            width=6,
        )


def _town(draw: ImageDraw.ImageDraw, x: float, y: float, colour) -> None:
    draw.rectangle([x, y - 34, x + 150, y], fill=colour)
    draw.ellipse([x + 28, y - 52, x + 82, y - 10], fill=colour)
    draw.rectangle([x + 118, y - 82, x + 132, y], fill=colour)
    draw.ellipse([x + 111, y - 100, x + 139, y - 70], fill=colour)


def make_background(path: Path) -> Path:
    """Raat ka sehra: asmaan, sitare, hilal, tiley, khajoor aur door basti."""
    image = Image.new("RGB", (WIDTH, HEIGHT), (6, 8, 18))
    draw = ImageDraw.Draw(image)

    horizon = int(HEIGHT * 0.76)

    # asmaan: gehri raat se ufq ke garam rang tak
    for y in range(horizon):
        t = (y / max(1, horizon)) ** 0.9
        colour = (
            int(8 + (74 - 8) * t),
            int(12 + (56 - 12) * t),
            int(34 + (70 - 34) * t),
        )
        draw.line([(0, y), (WIDTH, y)], fill=colour)

    # sitare
    stars = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    pen = ImageDraw.Draw(stars)
    rng = random.Random(7)
    for _ in range(260):
        sx = rng.uniform(0, WIDTH)
        sy = rng.uniform(0, horizon * 0.82)
        radius = rng.choice([1, 1, 1, 2, 2, 3])
        alpha = rng.randint(70, 210)
        pen.ellipse([sx - radius, sy - radius, sx + radius, sy + radius], fill=(255, 250, 235, alpha))
    image = Image.alpha_composite(image.convert("RGBA"), stars)

    # hilal (baayein taraf, taake upar right wale logo se na takraye)
    cx, cy = 250, 330
    moon_only = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    mask = Image.new("L", (WIDTH, HEIGHT), 0)
    mask_pen = ImageDraw.Draw(mask)
    mask_pen.ellipse([cx - 90, cy - 90, cx + 90, cy + 90], fill=255)
    mask_pen.ellipse([cx - 30, cy - 106, cx + 148, cy + 74], fill=0)
    moon_only.paste((255, 236, 190, 235), (0, 0), mask)
    image = Image.alpha_composite(image, moon_only)

    # tiley (teen teh)
    layers = [
        (horizon + 30, 24, (44, 34, 28)),
        (horizon + 120, 38, (30, 22, 20)),
        (horizon + 230, 52, (18, 13, 13)),
    ]
    for index, (base_y, amp, colour) in enumerate(layers):
        points: List[Tuple[float, float]] = []
        for x in range(0, WIDTH + 20, 20):
            y = (
                base_y
                + amp * math.sin(x / 260 + index * 1.7)
                + amp * 0.45 * math.sin(x / 90 + index)
            )
            points.append((x, y))
        points += [(WIDTH, HEIGHT), (0, HEIGHT)]
        draw.polygon(points, fill=colour)

    # door basti ka silhouette (log nahi, sirf imaraat)
    _town(draw, 250, horizon + 96, (16, 12, 14))
    _town(draw, 620, horizon + 108, (13, 10, 12))

    # khajoor ke darakht kinaron par
    _palm(draw, 60, HEIGHT - 40, 620, (10, 8, 10))
    _palm(draw, WIDTH - 90, HEIGHT - 10, 540, (10, 8, 10))

    # text ke peeche halka parda, taake likhai saaf parhi jaye
    scrim = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    scrim_pen = ImageDraw.Draw(scrim)
    scrim_pen.rounded_rectangle([55, 260, WIDTH - 55, 1680], radius=56, fill=(0, 0, 0, 132))
    scrim = scrim.filter(ImageFilter.GaussianBlur(50))
    image = Image.alpha_composite(image, scrim)

    # kinare gehre
    edges = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    edge_pen = ImageDraw.Draw(edges)
    for y in range(HEIGHT):
        edge = min(y, HEIGHT - 1 - y)
        if edge < 380:
            alpha = int(150 * (1 - edge / 380) ** 1.6)
            edge_pen.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, alpha))
    image = Image.alpha_composite(image, edges)

    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(path, format="PNG", optimize=True)
    return path


# ---------------------------------------------------------------------- logo


BACKGROUND_NAMES = (
    "background.mp4",
    "background.mov",
    "background.webm",
    "background.jpg",
    "background.jpeg",
    "background.png",
)


def custom_background(assets_dir: Path) -> Optional[Path]:
    """assets me rakha apna background (photo ya video), agar maujood ho.

    `assets/background.mp4` ya `assets/background.jpg` rakho — bana hua
    sehra background use nahi hoga, tumhara apna chalega.
    """
    for name in BACKGROUND_NAMES:
        candidate = assets_dir / name
        if candidate.exists() and candidate.stat().st_size > 0:
            return candidate
    return None


def _square_points(cx: float, cy: float, radius: float, angle_deg: float):
    points = []
    for index in range(4):
        angle = math.radians(angle_deg + 90 * index)
        points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return points


def ensure_logo(path: Path) -> Path:
    """Sunehri muhar (8-kone wala sitara).

    Apna logo lagana ho to `assets/logo.png` replace kar dijiye — us waqt ye
    function kuch nahi karta.
    """
    if path.exists() and path.stat().st_size > 0:
        return path

    size = 512
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pen = ImageDraw.Draw(image)
    gold = (214, 176, 94, 235)

    pen.ellipse([12, 12, size - 12, size - 12], outline=gold, width=12)
    pen.ellipse([64, 64, size - 64, size - 64], outline=(214, 176, 94, 150), width=4)

    centre = size / 2
    for angle in (0, 45):
        pen.polygon(_square_points(centre, centre, 138, angle), outline=gold, width=9)

    pen.ellipse([centre - 18, centre - 18, centre + 18, centre + 18], fill=gold)

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")
    return path


# ------------------------------------------------------------------ captions


def _timestamp(centis: int) -> str:
    centis = max(0, int(centis))
    hours, rest = divmod(centis, 360000)
    minutes, rest = divmod(rest, 6000)
    seconds, frac = divmod(rest, 100)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{frac:02d}"


def _clean(text: str) -> str:
    return (
        (text or "")
        .replace("{", "")
        .replace("}", "")
        .replace("\r", " ")
        .replace("\n", " ")
        .strip()
    )


def _per_line(size: int) -> int:
    return max(12, int(900 / (size * 0.62)))


def _wrap(text: str, per_line: int) -> str:
    words = (text or "").split()
    if not words:
        return ""
    lines: List[str] = []
    current: List[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        if current and len(candidate) > per_line:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return "\\N".join(lines)


def _karaoke(text: str, durations: Sequence[int], per_line: int) -> str:
    """Har lafz ko uske bolne ke waqt par roshan karta hai."""
    words = _clean(text).split()
    if not words:
        return ""
    parts: List[str] = []
    line_len = 0
    for index, word in enumerate(words):
        dur = max(1, int(durations[index])) if index < len(durations) else 20
        if line_len and line_len + 1 + len(word) > per_line:
            parts.append("\\N")
            line_len = 0
        elif parts:
            parts.append(" ")
            line_len += 1
        parts.append(f"{{\\k{dur}}}{word}")
        line_len += len(word)
    return "".join(parts)


def _blocks(card: Card) -> List[Tuple[str, int, int, str]]:
    """(style, size, per_line, text) — upar se neeche."""
    blocks: List[Tuple[str, int, int, str]] = []
    if card.label:
        blocks.append(("Label", 36, 34, card.label))
    if card.arabic:
        size = 56
        if len(card.arabic) > 140:
            size = 46
        elif len(card.arabic) > 80:
            size = 50
        blocks.append(("Arabic", size, _per_line(size), card.arabic))
    if card.text:
        short = not card.arabic and len(card.text) < 60
        if short:
            size = 84
        elif len(card.text) > 260:
            size = 50
        elif len(card.text) > 170:
            size = 56
        else:
            size = 62
        blocks.append(("Title" if short else "Body", size, _per_line(size), card.text))
    if card.sub:
        blocks.append(("Sub", 44, _per_line(44), card.sub))
    if card.footer:
        blocks.append(("Footer", 30, _per_line(30), card.footer))
    return blocks


def _layout(card: Card) -> List[dict]:
    prepared = []
    for style, size, per_line, text in _blocks(card):
        wrapped = _wrap(_clean(text), per_line)
        if not wrapped:
            continue
        lines = wrapped.count("\\N") + 1
        height = int(round(lines * size * 1.5 + 14))
        prepared.append(
            {
                "style": style,
                "size": size,
                "per_line": per_line,
                "text": text,
                "wrapped": wrapped,
                "height": height,
            }
        )

    total = sum(item["height"] for item in prepared)
    y = CONTENT_CENTER - total / 2
    placed: List[dict] = []
    for item in prepared:
        block = dict(item)
        block["y"] = int(round(y + item["height"] / 2))
        placed.append(block)
        y += item["height"]
    return placed


def card_timings(
    cards: Sequence[Card], words: Sequence[Tuple[float, float]], duration: float
) -> Optional[List[Tuple[float, float]]]:
    """Har card ka shuru/aakhir, bolne ke waqt ke hisaab se."""
    if not words or not cards:
        return None

    counts = [max(1, len(_clean(card.spoken).split())) for card in cards]
    total = sum(counts)
    if total <= 0:
        return None

    count_words = len(words)
    spans: List[Tuple[float, float]] = []
    cursor = 0
    for count in counts:
        start_index = min(count_words - 1, int(round(cursor * count_words / total)))
        cursor += count
        end_index = min(count_words - 1, int(round(cursor * count_words / total)) - 1)
        end_index = max(start_index, end_index)
        spans.append((words[start_index][0], words[end_index][1]))

    fixed: List[Tuple[float, float]] = []
    last_end = 0.0
    for start, end in spans:
        start = max(start, last_end)
        end = max(end, start + 0.4)
        if start >= duration:
            start = max(0.0, duration - 0.6)
        end = min(max(end, start + 0.4), duration)
        fixed.append((start, end))
        last_end = end
    return fixed


def _word_slices(
    cards: Sequence[Card], words: Sequence[Tuple[float, float]]
) -> List[List[Tuple[float, float]]]:
    """Har card ke liye narration ke lafzon ka hissa."""
    if not words or not cards:
        return []

    counts = [max(1, len(_clean(card.spoken).split())) for card in cards]
    total = sum(counts)
    count_words = len(words)
    slices: List[List[Tuple[float, float]]] = []
    cursor = 0
    for count in counts:
        start = min(count_words, int(round(cursor * count_words / total)))
        cursor += count
        end = min(count_words, int(round(cursor * count_words / total)))
        slices.append(list(words[start : max(start + 1, end)]))
    return slices


def _dialogue(start_cs: int, end_cs: int, style: str, text: str) -> str:
    return (
        f"Dialogue: 0,{_timestamp(start_cs)},{_timestamp(end_cs)},"
        f"{style},,0,0,0,,{text}"
    )


def build_captions(
    cards: List[Card],
    duration: float,
    path: Path,
    header_text: str,
    title: str = "Deen Reels",
    timings: Optional[Sequence[Tuple[float, float]]] = None,
    words: Optional[Sequence[Tuple[float, float]]] = None,
) -> Path:
    total_cs = max(1, int(round(duration * 100)))

    if timings and len(timings) == len(cards):
        spans_cs = [
            (max(0, int(round(start * 100))), min(total_cs, int(round(end * 100))))
            for start, end in timings
        ]
    else:
        weights = [max(1, len(_clean(card.spoken))) for card in cards]
        scale = total_cs / float(sum(weights) or 1)
        spans_cs = []
        cursor = 0
        for weight in weights:
            start = cursor
            end = min(total_cs, cursor + int(round(weight * scale)))
            if end <= start:
                end = min(total_cs, start + 50)
            spans_cs.append((start, end))
            cursor = end

    slices = _word_slices(cards, words or [])

    events: List[str] = [
        _dialogue(
            0,
            total_cs,
            "Header",
            f"{{\\an7\\pos(55,95)}}{_wrap(_clean(header_text), 34)}",
        )
    ]

    for index, (card, (start, end)) in enumerate(zip(cards, spans_cs)):
        if start >= total_cs or end <= start:
            continue

        displayed = _clean(card.text).split()
        karaoke: Optional[List[int]] = None
        if slices and index < len(slices):
            chunk = slices[index]
            if chunk and len(chunk) == len(displayed):
                durations = [
                    max(1, int(round((finish - begin) * 100))) for begin, finish in chunk
                ]
                total = sum(durations)
                span = max(1, end - start)
                if total > span:
                    factor = span / total
                    durations = [max(1, int(round(value * factor))) for value in durations]
                karaoke = durations

        for block in _layout(card):
            body = block["wrapped"]
            if karaoke and block["text"] == card.text:
                body = _karaoke(card.text, karaoke, block["per_line"])
            events.append(
                _dialogue(
                    start,
                    end,
                    block["style"],
                    f"{{\\fad(200,200)\\an5\\pos(540,{block['y']})}}{body}",
                )
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = ASS_HEADER.format(title=_clean(title)) + "\n".join(events) + "\n"
    path.write_text(payload, encoding="utf-8")
    return path
