"""Saari stories ke videos ek saath banao — dekhne ke liye.

Ek bhi video upload nahi hoti aur state.json nahi badalta. Nateeja:

    out/all/01-abu-bakr-ghar/video.mp4
    out/all/01-abu-bakr-ghar/metadata.json
    ...
    out/all/index.html        (gallery — sab videos browser me chalti hain)

Chalaiye:
    DRY_RUN=yes python -m video_factory.batch
"""

from __future__ import annotations

import html
import json
import os
import traceback
from pathlib import Path

from .config import ROOT, load_config
from .i18n import get_lang
from .main import log, render_story
from .script_builder import source_line
from .stories import load_stories

STORIES_PATH = ROOT / "content" / "stories.json"

GALLERY = """<!doctype html>
<html lang="ur" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>سارے حصے — ورثة الانبياء</title>
<style>
  body { margin: 0; background: #0b1220; color: #e8d9a6;
    font-family: -apple-system, "Noto Naskh Arabic", sans-serif; }
  header { padding: 26px 16px 8px; text-align: center; }
  h1 { font-size: 20px; margin: 0 0 6px; }
  header p { margin: 0; font-size: 13px; opacity: .7; }
  .grid { display: grid; gap: 22px; padding: 18px 16px 40px;
    max-width: 460px; margin: 0 auto; }
  .card { background: #111c31; border-radius: 16px; padding: 14px; }
  h2 { font-size: 17px; margin: 0 0 4px; }
  .sub { margin: 0 0 10px; font-size: 13px; opacity: .75; }
  video { width: 100%; border-radius: 12px; background: #000; }
  .hawala { margin: 10px 0 0; font-size: 13px; opacity: .85; }
</style>
</head>
<body>
<header>
  <h1>سارے حصے</h1>
  <p>{count} ویڈیوز — دیکھیے اور بتائیے کیا ٹھیک ہے</p>
</header>
<main class="grid">
{cards}
</main>
</body>
</html>
"""

CARD = """  <section class="card">
    <h2>{title}</h2>
    <p class="sub">{subtitle}</p>
    <video controls playsinline preload="metadata" src="{file}"></video>
    <p class="hawala">{hawala}</p>
  </section>"""


def build_gallery(items: list, path: Path) -> Path:
    cards = "\n".join(
        CARD.format(
            title=html.escape(item["title"]),
            subtitle=html.escape(item["subtitle"]),
            file=html.escape(item["file"]),
            hawala=html.escape(item["hawala"]),
        )
        for item in items
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        GALLERY.format(count=len(items), cards=cards), encoding="utf-8"
    )
    return path


def main() -> int:
    os.chdir(ROOT)
    cfg = load_config()
    lang = get_lang(cfg.lang)
    stories = load_stories(STORIES_PATH)

    out_root = cfg.out_dir / "all"
    items: list = []

    for ordinal, story in enumerate(stories):
        folder = out_root / f"{ordinal + 1:02d}-{story['id']}"
        log(f"[{ordinal + 1}/{len(stories)}] {story['title']}")
        try:
            info = render_story(cfg, lang, story, ordinal, folder)
        except Exception as exc:  # noqa: BLE001
            log(f"FAIL: {story['id']} — {exc}")
            log(traceback.format_exc())
            continue

        meta = {
            "id": story["id"],
            "title": story["title"],
            "subtitle": story.get("subtitle", ""),
            "hawala": source_line(story),
            "file": f"{folder.name}/video.mp4",
            "duration_seconds": round(info["duration"], 2),
            "video_title": info["script"].title,
        }
        (folder / "metadata.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        items.append(meta)

    gallery = build_gallery(items, out_root / "index.html")
    log(f"Gallery taiyar: {gallery} — {len(items)}/{len(stories)} videos")
    return 0 if items else 1


def run() -> int:
    try:
        return main()
    except Exception as exc:  # noqa: BLE001
        log(f"ERROR: {exc}")
        log(traceback.format_exc())
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
