"""Poore pipeline ka entry point.

Chalaiye:
    python -m video_factory.main

Har run ka video GitHub par artifact aur "latest" release dono me jata hai.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import traceback
from pathlib import Path

from .config import ROOT, Config, load_config
from .i18n import get_lang
from .render import (
    build_slideshow,
    ensure_tools,
    media_duration,
    mix_ambience,
    render,
)
from .script_builder import Script, build_script, source_line
from .state import load, mark_posted, save
from .stories import load_stories, next_story
from .tts import synthesize
from .uploaders.base import UploadResult
from .visuals import (
    IMAGE_SUFFIXES,
    build_captions,
    card_timings,
    custom_backgrounds,
    ensure_logo,
    make_background,
)

STATE_PATH = ROOT / "state.json"
STORIES_PATH = ROOT / "content" / "stories.json"


def log(message: str) -> None:
    print(message, flush=True)


# Jin surkhion (labels) par awaaz thori dheemi aur sanjeeda ho.
SOLEMN_LABELS = {"ایک صفت", "وفات", "دفن", "شہادت", "سبق"}


def _rate_with(rate: str, delta: int) -> str:
    """'+0%' me -6 jod kar '-6%' banana."""
    try:
        base = int((rate or "+0%").strip().replace("%", "").replace("+", ""))
    except ValueError:
        base = 0
    return f"{base + delta:+d}%"


def build_voiceover(cards, voice: str, out_dir: Path, rate: str):
    """Har card ki alag awaaz, darmiyan me saans ka waqfa.

    Isi se "mahol" banta hai: jumla khatam, chhota sa sukun, phir agla jumla.
    Sanjeeda beat (وفات، ایک صفت، سبق) thori dheemi boli jati hai.
    """
    work = out_dir / "voice_parts"
    work.mkdir(parents=True, exist_ok=True)
    files: list = []
    timings: list = []
    words: list = []
    cursor = 0.0
    silences: dict = {}

    def silence(seconds: float) -> Path:
        key = round(seconds, 2)
        if key not in silences:
            path = work / f"sil_{int(key * 100):03d}.wav"
            if not path.exists():
                subprocess.run(
                    [
                        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                        "-t", f"{key:.2f}", "-c:a", "pcm_s16le", str(path),
                    ],
                    capture_output=True,
                )
            silences[key] = path
        return silences[key]

    for index, card in enumerate(cards):
        text = (card.spoken or card.text or "").strip()
        if not text:
            timings.append((cursor, cursor))
            continue

        delta = -6 if (card.label or "") in SOLEMN_LABELS else 0
        mp3 = work / f"card{index:02d}.mp3"
        wav = work / f"card{index:02d}.wav"
        transcript = synthesize(text, voice, mp3, _rate_with(rate, delta))
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(mp3), "-ar", "24000", "-ac", "1",
                "-c:a", "pcm_s16le", str(wav),
            ],
            capture_output=True,
        )
        dur = media_duration(wav)
        timings.append((cursor, cursor + dur))
        words.extend((start + cursor, end + cursor) for start, end in transcript.words)
        files.append(wav)

        if index < len(cards) - 1:
            gap = 1.0 if index >= len(cards) - 2 else 0.45
            files.append(silence(gap))
            cursor += dur + gap
        else:
            cursor += dur

    if not files:
        raise RuntimeError("Voiceover ke liye koi text nahi mila")

    listing = work / "list.txt"
    listing.write_text(
        "\n".join(f"file '{item.resolve()}'" for item in files) + "\n",
        encoding="utf-8",
    )
    output = out_dir / "voice_full.m4a"
    subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0", "-i", str(listing),
            "-c:a", "aac", "-b:a", "128k", "-ar", "24000", str(output),
        ],
        capture_output=True,
        text=True,
    )
    if not output.exists() or output.stat().st_size < 1000:
        raise RuntimeError("Purani awaaz jod nahi payi")

    return output, timings, words, media_duration(output)


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


def render_story(
    cfg: Config,
    lang: dict,
    story: dict,
    ordinal: int,
    total: int,
    out_dir: Path,
) -> dict:
    """Ek story ka video: TTS → ambience → background → captions → render.

    Post ya state ka koi kaam nahi — `main` (rozana) aur `batch` (sab ek saath)
    dono isi ko use karte hain.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    voice = cfg.voice or lang["voice"]
    script = build_script(story, lang, cfg, ordinal)

    audio_path = out_dir / "voice.mp3"
    background_path = out_dir / "background.png"
    captions_path = out_dir / "captions.ass"
    video_path = out_dir / "video.mp4"

    log(f"Voiceover ban raha hai ({voice})...")
    timings = None
    words: list = []
    try:
        audio_path, timings, words, duration = build_voiceover(
            script.cards, voice, out_dir, cfg.tts_rate
        )
    except Exception as exc:  # noqa: BLE001
        # Kuch bhi ho jaye, purana tareeqa (pooora narration ek saath).
        log(f"Card-wise awaaz fail: {exc} — poora narration ek saath bana rahe hain.")
        transcript = synthesize(
            script.narration, voice, out_dir / "voice.mp3", cfg.tts_rate
        )
        audio_path = transcript.path
        words = transcript.words
        duration = media_duration(audio_path)

    log(f"Audio duration: {duration:.1f}s")
    if duration > 180:
        log("Dhyan: video 3 minute se lambi hai — story ko chhota kijiye.")

    if cfg.ambience and audio_path:
        log("Halki background awaaz milayi ja rahi hai...")
        audio_path = mix_ambience(
            audio_path, out_dir / "voice_mixed.m4a", duration
        )

    log("Background aur captions ban rahe hain...")
    pictures = custom_backgrounds(Path("assets"))
    if len(pictures) > 1 and all(
        item.suffix.lower() in IMAGE_SUFFIXES for item in pictures
    ):
        log(f"{len(pictures)} tasveerein mili — slideshow (zoom/pan) ban raha hai...")
        background_path = build_slideshow(
            pictures, duration, out_dir / "background_motion.mp4"
        )
    elif pictures:
        background_path = pictures[0]
        log(f"Apna background use ho raha hai: {pictures[0].name}")
    else:
        make_background(background_path)
    if not timings:
        timings = card_timings(script.cards, words, duration)
    build_captions(
        script.cards,
        duration,
        captions_path,
        header_text=cfg.channel_name,
        title=script.title,
        timings=timings,
        words=words,
        source_text=source_line(story),
        sign_text=f"{cfg.channel_name} • حصہ {ordinal + 1}/{total}",
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

    return {
        "video": video_path,
        "script": script,
        "duration": duration,
        "voice": voice,
    }


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

    out_dir = cfg.out_dir
    info = render_story(cfg, lang, story, ordinal, len(stories), out_dir)
    video_path = info["video"]
    script = info["script"]
    duration = info["duration"]
    voice = info["voice"]

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
