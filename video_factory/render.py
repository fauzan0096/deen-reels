"""ffmpeg: background + logo + voiceover + halki ambience + captions → mp4."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from .config import HEIGHT, WIDTH


class RenderError(RuntimeError):
    pass


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
    subtitles = f"ass={captions}:fontsdir={fonts_dir}"

    command = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-y"]

    if logo is not None and Path(logo).exists():
        command += [
            "-loop",
            "1",
            "-framerate",
            "30",
            "-i",
            str(background),
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
            "-loop",
            "1",
            "-framerate",
            "30",
            "-i",
            str(background),
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
        "-crf",
        "20",
        "-tune",
        "stillimage",
        "-r",
        "30",
        "-g",
        "60",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
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
