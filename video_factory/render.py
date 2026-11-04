"""ffmpeg se background + voiceover + captions ko mp4 me jodta hai."""

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


def render(
    background: Path,
    audio: Path,
    captions: Path,
    output: Path,
    fonts_dir: Path,
    duration: Optional[float] = None,
) -> Path:
    ensure_tools()
    if duration is None:
        duration = media_duration(audio)

    filter_chain = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        f"format=yuv420p,"
        f"ass={captions}:fontsdir={fonts_dir}"
    )

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "warning",
        "-y",
        "-loop",
        "1",
        "-framerate",
        "30",
        "-i",
        str(background),
        "-i",
        str(audio),
        "-vf",
        filter_chain,
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
