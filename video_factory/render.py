"""ffmpeg: background + logo + voiceover + halki ambience + captions → mp4."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from .config import HEIGHT, WIDTH


class RenderError(RuntimeError):
    pass


VIDEO_SUFFIXES = {".mp4", ".mov", ".webm", ".m4v"}


def _background_input(background: Path) -> list:
    """Image ho to loop karke, video ho to sirf ek baar chalta hai."""
    if Path(background).suffix.lower() in VIDEO_SUFFIXES:
        return ["-i", str(background)]
    return ["-loop", "1", "-framerate", "30", "-i", str(background)]


def build_slideshow(images, duration: float, output: Path) -> Path:
    """Kai tasveerein → halki zoom/pan ke saath ek background video."""
    ensure_tools()
    pictures = [Path(item) for item in images if Path(item).exists()]
    if not pictures:
        raise RenderError("Slideshow ke liye koi tasveer nahi mili")

    per = max(2.0, float(duration) / len(pictures))
    work = output.parent / "slides"
    work.mkdir(parents=True, exist_ok=True)

    clips = []
    for index, picture in enumerate(pictures):
        clip = work / f"clip{index:02d}.mp4"
        if index % 2 == 0:
            zoom = "'min(1.0+0.0009*on,1.18)'"
        else:
            zoom = "'max(1.18-0.0009*on,1.0)'"
        command = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-loop",
            "1",
            "-framerate",
            "30",
            "-t",
            f"{per:.2f}",
            "-i",
            str(picture),
            "-vf",
            (
                f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
                f"crop={WIDTH}:{HEIGHT},"
                f"zoompan=z={zoom}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                f":d=1:s={WIDTH}x{HEIGHT}:fps=30,format=yuv420p"
            ),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "22",
            "-an",
            str(clip),
        ]
        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode != 0 or not clip.exists():
            raise RenderError(
                f"Slideshow clip fail ({picture.name}):\n"
                + (completed.stderr or "")[-800:]
            )
        clips.append(clip)

    listing = work / "list.txt"
    listing.write_text(
        "".join(f"file '{clip.name}'\n" for clip in clips), encoding="utf-8"
    )
    completed = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(listing),
            "-c",
            "copy",
            str(output),
        ],
        capture_output=True,
        text=True,
        cwd=str(work),
    )
    if completed.returncode != 0 or not output.exists():
        raise RenderError(
            "Slideshow jodne me dikkat:\n" + (completed.stderr or "")[-800:]
        )
    return output


def ensure_tools() -> None:
    missing = [name for name in ("ffmpeg", "ffprobe") if shutil.which(name) is None]
    if missing:
        raise RenderError(
            "ffmpeg/ffprobe nahi mile. Install kijiye: "
            "macOS 'brew install ffmpeg', Ubuntu 'sudo apt-get install -y ffmpeg'."
        )


def media_duration(path: Path) -> float:
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RenderError(f"ffprobe fail hua: {completed.stderr.strip()[:400]}")
    try:
        return float(completed.stdout.strip())
    except ValueError as exc:
        raise RenderError(f"Audio duration padhi nahi gayi: {completed.stdout!r}") from exc


def mix_ambience(voice: Path, output: Path, duration: float) -> Path:
    """Voice ke neeche halki si hawa jaisi awaaz milata hai.

    Kuch bhi galat ho jaye to bas voice file hi wapas kar deta hai — video
    phir bhi ban jayegi.
    """
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(voice),
        "-f",
        "lavfi",
        "-i",
        "anoisesrc=color=pink:amplitude=0.4",
        "-filter_complex",
        "[1:a]lowpass=f=500,tremolo=f=0.12:d=0.45,volume=0.05[amb];"
        "[0:a][amb]amix=inputs=2:duration=first:dropout_transition=0[a]",
        "-map",
        "[a]",
        "-t",
        f"{max(1.0, duration):.2f}",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "44100",
        str(output),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0 or not output.exists() or output.stat().st_size < 1000:
        return voice
    return output


def render(
    background: Path,
    audio: Path,
    captions: Path,
    output: Path,
    fonts_dir: Path,
    duration: Optional[float] = None,
    logo: Optional[Path] = None,
) -> Path:
    ensure_tools()
    if duration is None:
        duration = media_duration(audio)

    scale_crop = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT}"
    )
    # Video background: khatam hone par aakhri frame par ruk jaye (logo end me
    # reh jaye, beech me ghoom kar na aaye).
    if Path(background).suffix.lower() in VIDEO_SUFFIXES:
        scale_crop += f",tpad=stop_mode=clone:stop_duration={max(1.0, duration) + 2:.1f}"
    subtitles = f"ass={captions}:fontsdir={fonts_dir}"

    command = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-y"]

    if logo is not None and Path(logo).exists():
        command += [
            *_background_input(background),
            "-i",
            str(audio),
            "-i",
            str(logo),
            "-filter_complex",
            (
                f"[0:v]{scale_crop},format=yuv420p[bg];"
                "[2:v]scale=250:-1[lg];"
                "[bg][lg]overlay=x=W-w-55:y=70[ov];"
                f"[ov]{subtitles},format=yuv420p[v]"
            ),
            "-map",
            "[v]",
            "-map",
            "1:a",
        ]
    else:
        command += [
            *_background_input(background),
            "-i",
            str(audio),
            "-vf",
            f"{scale_crop},format=yuv420p,{subtitles}",
        ]

    command += [
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-b:v",
        "800k",
        "-maxrate",
        "1100k",
        "-bufsize",
        "1600k",
        "-vsync",
        "cfr",
        "-r",
        "30",
        "-g",
        "30",
        "-c:a",
        "aac",
        "-b:a",
        "96k",
        "-ar",
        "44100",
        "-shortest",
        "-movflags",
        "+faststart",
        "-pix_fmt",
        "yuv420p",
        str(output),
    ]

    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RenderError("ffmpeg fail hua:\n" + (completed.stderr or "")[-1500:])
    if not output.exists() or output.stat().st_size < 10_000:
        raise RenderError("Video file ban nahi payi")

    return output
