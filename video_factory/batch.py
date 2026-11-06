"""Saari stories ke videos ek saath banao — dekhne aur download karne ke liye.

Ek bhi video upload nahi hoti aur state.json nahi badalta. Nateeja:

    out/all/index.html              — gallery (sab videos ek page par)
    out/all/download.html           — seedhe download links
    out/all/01-abu-bakr-ghar/index.html   — ek episode ka apna page
    out/all/01-abu-bakr-ghar/video.mp4
    out/all/01-abu-bakr-ghar/metadata.json

Chalaiye:
    DRY_RUN=yes python -m video_factory.batch
"""

from __future__ import annotations

import html
import json
import os
import subprocess
import time
import traceback
from pathlib import Path

from .config import ROOT, load_config
from .i18n import get_lang
from .main import log, render_story
from .script_builder import source_line
from .stories import load_stories

STORIES_PATH = ROOT / "content" / "stories.json"

STYLE = """
  body {{ margin: 0; background: #0b1220; color: #e8d9a6;
    font-family: -apple-system, "Noto Naskh Arabic", sans-serif; }}
  a {{ color: #e8d9a6; }}
  h1 {{ font-size: 19px; margin: 0 0 6px; text-align: center; }}
  p {{ margin: 0; font-size: 13px; opacity: .8; text-align: center; }}
  video {{ width: 100%; border-radius: 12px; background: #000; }}
  .dl {{ display: inline-block; background: #e8d9a6; color: #0b1220;
    padding: 13px 22px; border-radius: 999px; font-size: 16px;
    font-weight: 600; text-decoration: none; }}
"""

GALLERY = """<!doctype html>
<html lang="ur" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>سارے حصے — ورثة الانبياء</title>
<style>
""" + STYLE + """
  header {{ padding: 26px 16px 8px; text-align: center; }}
  header p {{ font-size: 13px; opacity: .7; }}
  .grid {{ display: grid; gap: 22px; padding: 18px 16px 40px;
    max-width: 460px; margin: 0 auto; }}
  .card {{ background: #111c31; border-radius: 16px; padding: 14px; }}
  h2 {{ font-size: 17px; margin: 0 0 4px; text-align: right; }}
  .sub {{ margin: 0 0 10px; font-size: 13px; opacity: .75; text-align: right; }}
  .hawala {{ margin: 10px 0 12px; font-size: 13px; opacity: .85;
    text-align: right; }}
  .row {{ display: flex; gap: 10px; align-items: center; }}
  .open {{ background: #1c2b45; color: #e8d9a6; border-radius: 999px;
    padding: 10px 16px; font-size: 14px; text-decoration: none; }}
  .top {{ display: flex; justify-content: center; gap: 16px; margin-bottom: 6px; }}
</style>
</head>
<body>
<header>
  <h1>سارے حصے</h1>
  <p>{count} ویڈیوز — شروع سے آخر تک، ترتیب سے</p>
  <p><a href="download.html">سیدھے ڈاؤن لوڈ لنکس</a></p>
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
    <video controls playsinline preload="none" poster="{poster}" src="{file}"></video>
    <p class="hawala">{hawala}</p>
    <p style="margin-top:12px">
      <a class="dl" href="{file}" download="{download}">ڈاؤن لوڈ</a>
      <a href="{page}">صرف یہ حصہ</a>
    </p>
  </section>"""

EPISODE = """<!doctype html>
<html lang="ur" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{ margin: 0; background: #0b1220; color: #e8d9a6;
    font-family: -apple-system, "Noto Naskh Arabic", sans-serif;
    display: flex; flex-direction: column; align-items: center;
    gap: 14px; padding: 20px 16px 44px; }}
  h1 {{ font-size: 18px; margin: 0; text-align: center; }}
  video {{ width: 100%; max-width: 420px; border-radius: 14px;
    background: #000; }}
  a {{ color: #e8d9a6; }}
  .dl {{ display: inline-block; background: #e8d9a6; color: #0b1220;
    padding: 14px 24px; border-radius: 999px; font-size: 17px;
    font-weight: 600; text-decoration: none; }}
  .note {{ font-size: 12px; opacity: .7; text-align: center;
    max-width: 380px; }}
  .nav {{ display: flex; gap: 18px; font-size: 14px; }}
</style>
</head>
<body>
  <h1>{title}</h1>
  <p class="note">{subtitle}</p>
  <video controls playsinline preload="metadata" src="video.mp4"></video>
  <a class="dl" href="video.mp4" download="{download}">ویڈیو ڈاؤن لوڈ کریں</a>
  <p class="note">{hawala}</p>
  <p class="note">آئی فون پر ڈاؤن لوڈ: ویڈیو چلائیں، Share بٹن دبائیں،
    پھر «Save to Files» منتخب کریں۔</p>
  <div class="nav">{nav}</div>
</body>
</html>
"""

DOWNLOADS = """<!doctype html>
<html lang="ur" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ڈاؤن لوڈ — ورثة الانبياء</title>
<style>
""" + STYLE + """
  header {{ padding: 26px 16px 10px; text-align: center; }}
  ol {{ max-width: 460px; margin: 0 auto; padding: 0 26px 48px 26px; }}
  li {{ margin: 0 0 14px; font-size: 15px; }}
  li a {{ display: block; padding: 12px 14px; background: #111c31;
    border-radius: 12px; text-decoration: none; }}
  li span {{ display: block; font-size: 12px; opacity: .7; }}
</style>
</head>
<body>
<header>
  <h1>ڈاؤن لوڈ</h1>
  <p>ہر حصہ الگ فائل — ترتیب سے</p>
</header>
<ol>
{items}
</ol>
</body>
</html>
"""


def _nav(items: list, index: int) -> str:
    links = ['<a href="../index.html">سارے حصے</a>']
    if index > 0:
        links.append(f'<a href="../{items[index - 1]["dir"]}/">پچھلا حصہ</a>')
    if index + 1 < len(items):
        links.append(f'<a href="../{items[index + 1]["dir"]}/">اگلا حصہ</a>')
    return " ".join(links)


def make_thumbnail(video: Path, out: Path, at: float = 1.2) -> Path | None:
    """Video ke ek frame se thumbnail — text video ke andar hi ban chuka hai
    (Arabic shaping libass karta hai, PIL nahi kar sakta)."""
    if not video.exists():
        return None
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{at:.2f}",
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-q:v",
            "3",
            str(out),
        ],
        capture_output=True,
        text=True,
    )
    return out if out.exists() and out.stat().st_size > 1000 else None


def build_episode_pages(items: list, out_root: Path) -> None:
    for index, item in enumerate(items):
        (out_root / item["dir"] / "index.html").write_text(
            EPISODE.format(
                title=html.escape(item["title"]),
                subtitle=html.escape(item["subtitle"]),
                hawala=html.escape(item["hawala"]),
                download=html.escape(item["download"]),
                nav=_nav(items, index),
            ),
            encoding="utf-8",
        )


def build_gallery(items: list, path: Path) -> Path:
    cards = "\n".join(
        CARD.format(
            title=html.escape(item["title"]),
            subtitle=html.escape(item["subtitle"]),
            hawala=html.escape(item["hawala"]),
            file=html.escape(item["file"]),
            page=html.escape(f"{item['dir']}/index.html"),
            download=html.escape(item["download"]),
            poster=html.escape(item.get("poster", "")),
        )
        for item in items
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        GALLERY.format(count=len(items), cards=cards), encoding="utf-8"
    )
    return path


def build_downloads(items: list, path: Path) -> Path:
    rows = "\n".join(
        f'  <li><a href="{html.escape(item["file"])}" '
        f'download="{html.escape(item["download"])}">{html.escape(item["title"])}'
        f'<span>{html.escape(item["subtitle"])} — {html.escape(item["hawala"])}</span>'
        f"</a></li>"
        for item in items
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(DOWNLOADS.format(items=rows), encoding="utf-8")
    return path


def main() -> int:
    os.chdir(ROOT)
    cfg = load_config()
    lang = get_lang(cfg.lang)
    stories = load_stories(STORIES_PATH)

    out_root = cfg.out_dir / "all"
    total = len(stories)
    items: list = []
    failed: list = []

    for ordinal, story in enumerate(stories):
        folder = out_root / f"{ordinal + 1:02d}-{story['id']}"
        log(f"[{ordinal + 1}/{total}] {story['title']}")

        info = None
        for attempt in (1, 2):
            try:
                info = render_story(
                    cfg, lang, story, ordinal, total, folder
                )
                break
            except Exception as exc:  # noqa: BLE001
                log(f"FAIL ({attempt}/2): {story['id']} — {exc}")
                log(traceback.format_exc())
        if info is None:
            failed.append(story["id"])
            continue

        item = {
            "id": story["id"],
            "dir": folder.name,
            "title": story["title"],
            "subtitle": story.get("subtitle", ""),
            "hawala": source_line(story),
            "file": f"{folder.name}/video.mp4",
            "download": f"{folder.name}.mp4",
            "duration_seconds": round(info["duration"], 2),
            "video_title": info["script"].title,
        }
        # Thumbnail (hook ka frame) — gallery aur YouTube ke liye.
        thumb = make_thumbnail(info["video"], folder / "thumbnail.jpg")
        if thumb is not None:
            item["poster"] = f"{folder.name}/thumbnail.jpg"
        (folder / "metadata.json").write_text(
            json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        items.append(item)

        # Har hisse ke baad gallery update — beech me ruk bhi jaye to jo ban
        # chuke hain wo mil jayein. Page banane me kuch ghalat ho jaye to
        # videos zaya na hon, sirf gallery purani rahe.
        try:
            build_episode_pages(items, out_root)
            build_gallery(items, out_root / "index.html")
            build_downloads(items, out_root / "download.html")
        except Exception as exc:  # noqa: BLE001
            log(f"Gallery update fail: {exc}")
            log(traceback.format_exc())

        # Bhaari temp files hata do, warna disk bhar jata hai.
        for name in (
            "voice.mp3",
            "voice_mixed.m4a",
            "background.png",
            "background_motion.mp4",
            "captions.ass",
        ):
            (folder / name).unlink(missing_ok=True)

        time.sleep(2)

    gallery = out_root / "index.html"
    downloads = out_root / "download.html"
    log(f"Gallery: {gallery}")
    log(f"Download: {downloads}")
    log(f"Ban gaye: {len(items)}/{total}")
    if failed:
        log("Nahi ban paye: " + ", ".join(failed))
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
