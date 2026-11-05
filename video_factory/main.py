"""Poore pipeline ka entry point.

Chalaiye:
    python -m video_factory.main

Har run ka video GitHub par artifact aur "latest" release dono me jata hai.
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path

from .config import ROOT, Config, load_config
from .i18n import get_lang
from .render import ensure_tools, media_duration, mix_ambience, render
from .script_builder import Script, build_script, source_line
from .state import load, mark_posted, save
from .stories import load_stories, next_story
from .tts import synthesize
from .uploaders.base import UploadResult
from .visuals import build_captions, card_timings, ensure_logo, make_background

STATE_PATH = ROOT / "state.json"
STORIES_PATH = ROOT / "content" / "stories.json"


def log(message: str) -> None:
    print(message, flush=True)


def publish(cfg: Config, video_path: Path, script: Script) -> list:
    results: list = []

    if cfg.dry_run:
        log("DRY_RUN on hai — koi upload nahi hoga.")
        return results

    if cfg.youtube_ready:
        try:
            from .uploaders import youtube

            video_id = youtube.upload(
                video_path, script.title, script.description, script.tags, cfg
            )
            results.append(
                UploadResult("youtube", True, f"https://youtu.be/{video_id}")
            )
        except Exception as exc:  # noqa: BLE001
            results.append(UploadResult("youtube", False, str(exc)))
        log(results[-1].line())

    if cfg.facebook_ready:
        try:
            from .uploaders import facebook

            post_id = facebook.upload(video_path, script.description, cfg, log=log)
            results.append(UploadResult("facebook", True, f"id={post_id}"))
        except Exception as exc:  # noqa: BLE001
            results.append(UploadResult("facebook", False, str(exc)))
        log(results[-1].line())

    if cfg.instagram_ready:
        try:
            from .uploaders import instagram

            media_id = instagram.upload(video_path, script.description, cfg)
            results.append(UploadResult("instagram", True, f"id={media_id}"))
        except Exception as exc:  # noqa: BLE001
            results.append(UploadResult("instagram", False, str(exc)))
        log(results[-1].line())

    if not (cfg.youtube_ready or cfg.facebook_ready or cfg.instagram_ready):
        log(
            "Koi platform configured nahi hai — video ban gayi lekin post nahi hui.\n"
            "README ke 'Platform setup' section se credentials add kijiye."
        )

    return results


def main() -> int:
    os.chdir(ROOT)
    cfg = load_config()
    lang = get_lang(cfg.lang)

    state = load(STATE_PATH)
    stories = load_stories(STORIES_PATH)

    story, ordinal = next_story(stories, state)
    if story is None:
        log(
            "Saari stories post ho chuki hain. content/stories.json me nayi "
            "story jodiye (hawale ke saath)."
        )
        return 1

    log(f"Aaj ka waqiya: {story['title']} — story #{ordinal + 1}")
    log(f"Hawala: {source_line(story)}")

    ensure_tools()

    voice = cfg.voice or lang["voice"]
    script = build_script(story, lang, cfg, ordinal)

    out_dir = cfg.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    audio_path = out_dir / "voice.mp3"
    background_path = out_dir / "background.png"
    captions_path = out_dir / "captions.ass"
    video_path = out_dir / "video.mp4"

    log(f"Voiceover ban raha hai ({voice})...")
    transcript = synthesize(
        script.narration, voice, out_dir / "voice.mp3", cfg.tts_rate
    )
    audio_path = transcript.path
    duration = media_duration(audio_path)
    log(f"Audio duration: {duration:.1f}s")
    if duration > 180:
        log("Dhyan: video 3 minute se lambi hai — story ko chhota kijiye.")

    if cfg.ambience and transcript.path:
        log("Halki background awaaz milayi ja rahi hai...")
        audio_path = mix_ambience(
            transcript.path, out_dir / "voice_mixed.m4a", duration
        )

    log("Background aur captions ban rahe hain...")
    make_background(background_path)
    timings = card_timings(script.cards, transcript.words, duration)
    build_captions(
        script.cards,
        duration,
        captions_path,
        header_text=cfg.channel_name,
        title=script.title,
        timings=timings,
        words=transcript.words,
    )
    logo_path = ensure_logo(Path("assets") / "logo.png") if cfg.logo else None

    log("Video render ho raha hai...")
    render(
        background=background_path,
        audio=audio_path,
        captions=captions_path,
        output=video_path,
        fonts_dir=Path("assets") / "fonts",
        duration=duration,
        logo=logo_path,
    )
    size_mb = video_path.stat().st_size / (1024 * 1024)
    log(f"Video taiyar: {video_path} ({size_mb:.1f} MB)")

    results = publish(cfg, video_path, script)

    metadata = {
        "id": story["id"],
        "title": story["title"],
        "subtitle": story.get("subtitle", ""),
        "source": story["source"],
        "video_title": script.title,
        "description": script.description,
        "tags": script.tags,
        "voice": voice,
        "duration_seconds": round(duration, 2),
        "uploads": [result.__dict__ for result in results],
    }
    (out_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # DRY_RUN sirf test hai — us se story aage nahi badhti. Story tabhi
    # "posted" mark hoti hai jab sach me upload ho jaye (ya koi platform
    # configured hi na ho, kyunki tab manual upload ka mode hai).
    posted_any = any(result.ok for result in results)
    no_platforms = not (
        cfg.youtube_ready or cfg.facebook_ready or cfg.instagram_ready
    )
    if posted_any or no_platforms:
        mark_posted(
            state,
            story["id"],
            {"platforms": [r.platform for r in results if r.ok], "file": video_path.name},
        )
        save(STATE_PATH, state)
        log(f"State update: {story['id']} posted list me add ho gaya.")
    else:
        log("Kuch bhi post nahi hua, isliye state nahi badla (kal phir wahi story aayegi).")

    log("Done.")
    return 0


def run() -> int:
    try:
        return main()
    except Exception as exc:  # noqa: BLE001
        log(f"ERROR: {exc}")
        # Poora traceback bhi, warna line number ka pata nahi chalta.
        log(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(run())
