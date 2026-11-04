"""Background art (PIL) + ASS captions.

Urdu/Arabic shaping libass karta hai, isliye text ko ASS me likhte hain aur
ffmpeg ke `ass` filter se burn karte hain. Fonts `assets/fonts` se aate hain.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFilter

from .config import HEIGHT, WIDTH
from .script_builder import Card

CONTENT_TOP = 340
CONTENT_BOTTOM = 1560
CONTENT_CENTER = (CONTENT_TOP + CONTENT_BOTTOM) // 2

ASS_HEADER = """[Script Info]
Title: {title}
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Header,Noto Sans,30,&H66FFFFFF,&H00FFFFFF,&H00120F0A,&H00000000,0,0,0,0,100,100,3,0,1,2,1,5,60,60,0,1
Style: Title,Noto Naskh Arabic,70,&H00FFFFFF,&H000000FF,&H00120F0A,&H96000000,0,0,0,0,100,100,0,0,1,4,3,5,70,70,0,1
Style: Label,Noto Naskh Arabic,34,&H99E6EEF2,&H000000FF,&H00120F0A,&H00000000,0,0,0,0,100,100,2,0,1,2,1,5,60,60,0,1
Style: Arabic,Noto Naskh Arabic,48,&H00F5E9D0,&H000000FF,&H00120F0A,&H96000000,0,0,0,0,100,100,0,0,1,3,2,5,60,60,0,1
Style: Body,Noto Naskh Arabic,46,&H00FFFFFF,&H000000FF,&H00120F0A,&H96000000,0,0,0,0,100,100,0,0,1,3,2,5,60,60,0,1
Style: Sub,Noto Naskh Arabic,36,&HCCE6EEF2,&H000000FF,&H00120F0A,&H00000000,0,0,0,0,100,100,0,0,1,2,1,5,60,60,0,1
Style: Footer,Noto Naskh Arabic,26,&H99D9E2E6,&H000000FF,&H00120F0A,&H00000000,0,0,0,0,100,100,1,0,1,2,1,5,50,50,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# (ASS style, font size, chars per line)
Block = Tuple[str, int, int]


def make_background(
    path: Path,
    top: tuple = (16, 42, 58),
    bottom: tuple = (5, 12, 19),
    accent: tuple = (32, 116, 128),
) -> Path:
    """1080x1920 gradient + halka geometric pattern + text scrim."""
    image = Image.new("RGB", (WIDTH, HEIGHT), bottom)
    draw = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        t = (y / (HEIGHT - 1)) ** 0.85
        colour = tuple(int(round(a + (b - a) * t)) for a, b in zip(top, bottom))
        draw.line([(0, y), (WIDTH, y)], fill=colour)

    pattern = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    pen = ImageDraw.Draw(pattern)
    step = 150
    for row in range(-1, HEIGHT // step + 2):
        for col in range(-1, WIDTH // step + 2):
            cx = col * step + (step // 2 if row % 2 else 0)
            cy = row * step
            radius = 46 + ((row + col) % 3) * 10
            pen.arc(
                [cx - radius, cy - radius, cx + radius, cy + radius],
                200,
                340,
                fill=accent + (26,),
                width=3,
            )
    image = Image.alpha_composite(image.convert("RGBA"), pattern)

    scrim = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    scrim_pen = ImageDraw.Draw(scrim)
    scrim_pen.rounded_rectangle([70, 300, WIDTH - 70, 1620], radius=56, fill=(0, 0, 0, 120))
    scrim = scrim.filter(ImageFilter.GaussianBlur(46))
    image = Image.alpha_composite(image, scrim)

    edges = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    edge_pen = ImageDraw.Draw(edges)
    for y in range(HEIGHT):
        edge = min(y, HEIGHT - 1 - y)
        if edge < 380:
            alpha = int(155 * (1 - edge / 380) ** 1.6)
            edge_pen.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, alpha))
    image = Image.alpha_composite(image, edges)

    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(path, format="PNG", optimize=True)
    return path


def _timestamp(centis: int) -> str:
    centis = max(0, int(centis))
    hours, rest = divmod(centis, 360000)
    minutes, rest = divmod(rest, 6000)
    seconds, frac = divmod(rest, 100)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{frac:02d}"


def _clean(text: str) -> str:
    """ASS override blocks `{...}` hote hain, isliye braces hata dete hain."""
    return (
        (text or "")
        .replace("{", "")
        .replace("}", "")
        .replace("\r", " ")
        .replace("\n", " ")
        .strip()
    )


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


def _blocks(card: Card) -> List[Tuple[Block, str]]:
    """Card ko upar se neeche blocks me todta hai."""
    out: List[Tuple[Block, str]] = []
    if card.label:
        out.append((("Label", 34, 34), card.label))
    if card.arabic:
        out.append((("Arabic", 48, 26), card.arabic))
    if card.text:
        style = "Title" if not card.arabic and len(card.text) < 60 else "Body"
        size = 70 if style == "Title" else 46
        out.append(((style, size, 24 if style == "Title" else 26), card.text))
    if card.sub:
        out.append((("Sub", 36, 34), card.sub))
    if card.footer:
        out.append((("Footer", 26, 46), card.footer))
    return out


def _layout(card: Card) -> List[Tuple[str, int, str]]:
    """Blocks ko vertically center karke har ek ka y nikalta hai."""
    prepared = []
    for (style, size, per_line), text in _blocks(card):
        wrapped = _wrap(_clean(text), per_line)
        if not wrapped:
            continue
        lines = wrapped.count("\\N") + 1
        height = int(round(len_size(lines, size)))
        prepared.append((style, wrapped, height))

    total = sum(item[2] for item in prepared)
    y = CONTENT_CENTER - total / 2
    placed: List[Tuple[str, int, str]] = []
    for style, wrapped, height in prepared:
        placed.append((style, int(round(y + height / 2)), wrapped))
        y += height
    return placed


def len_size(lines: int, size: int) -> float:
    return lines * size * 1.5 + 16


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
) -> Path:
    total_cs = max(1, int(round(duration * 100)))
    weights = [max(1, len(_clean(card.spoken))) for card in cards]
    scale = total_cs / float(sum(weights) or 1)

    events: List[str] = [
        _dialogue(
            0,
            total_cs,
            "Header",
            f"{{\\an8\\pos(540,120)}}{_wrap(_clean(header_text), 40)}",
        )
    ]

    cursor = 0
    for card, weight in zip(cards, weights):
        start = cursor
        end = min(total_cs, cursor + int(round(weight * scale)))
        if end <= start:
            end = min(total_cs, start + 50)
        cursor = end
        if start >= total_cs:
            break

        for style, y, wrapped in _layout(card):
            events.append(
                _dialogue(
                    start,
                    end,
                    style,
                    f"{{\\fad(220,220)\\an5\\pos(540,{y})}}{wrapped}",
                )
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = ASS_HEADER.format(title=_clean(title)) + "\n".join(events) + "\n"
    path.write_text(payload, encoding="utf-8")
    return path
