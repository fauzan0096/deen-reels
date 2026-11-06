"""Video publish karne se pehle ki aakhri jaanch.

Sabse mehnga galti ye hai ke kharab ya khaali video YouTube/Facebook par chali
jaye — wahan se hataana mushkil hota hai. Is liye upload se pehle ffprobe se
video ki haqeeqat dekhi jati hai: file, size, video stream, awaaz, duration,
resolution, aur awaaz ki awaaz (volume) khaali to nahi.

Ye module sirf padhta hai — kuch badalta nahi.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .config import HEIGHT, WIDTH

MIN_BYTES = 200_000
MIN_SECONDS = 5.0
MAX_SECONDS = 240.0
MIN_MEAN_VOLUME = -45.0  # dB — is se dheemi awaaz ka matlab voiceover hi nahi
DURATION_TOLERANCE = 2.5


@dataclass
class Report:
    ok: bool = True
    problems: List[str] = field(default_factory=list)
    width: int = 0
    height: int = 0
    duration: float = 0.0
    has_video: bool = False
    has_audio: bool = False
    mean_volume: Optional[float] = None

    def summary(self) -> str:
        return (
            f"{self.width}x{self.height}, {self.duration:.1f}s, "
            f"video={'yes' if self.has_video else 'no'}, "
            f"audio={'yes' if self.has_audio else 'no'}"
        )


def _probe(path: Path) -> dict:
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError("ffprobe fail hua: " + (completed.stderr or "")[:400])
    try:
        return json.loads(completed.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"ffprobe ka jawab samajh nahi aaya: {exc}") from exc


def mean_volume(path: Path) -> Optional[float]:
    """Awaaz ka aam level (dB). Khaali/silent voiceover pakadne ke liye."""
    completed = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-map",
            "0:a:0",
            "-af",
            "volumedetect",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    match = re.search(
        r"mean_volume:\s*(-?\d+(?:\.\d+)?)\s*dB", completed.stderr or ""
    )
    return float(match.group(1)) if match else None


def check_video(path: Path, expected_duration: Optional[float] = None) -> Report:
    """Video ko jaanchta hai aur masle ki list lautata hai (khaali = theek)."""
    report = Report()
    video = Path(path)

    if not video.exists():
        report.problems.append("Video file maujood nahi hai")
        report.ok = False
        return report

    size = video.stat().st_size
    if size < MIN_BYTES:
        report.problems.append(
            f"File bahut chhoti hai ({size / 1024:.0f} KB) — video adhoori lagti hai"
        )

    data = _probe(video)
    streams = data.get("streams") or []
    video_streams = [item for item in streams if item.get("codec_type") == "video"]
    audio_streams = [item for item in streams if item.get("codec_type") == "audio"]

    report.has_video = bool(video_streams)
    report.has_audio = bool(audio_streams)

    if not report.has_video:
        report.problems.append("Video stream nahi mili")
    if not report.has_audio:
        report.problems.append("Awaaz (audio stream) nahi hai — video khamosh hai")

    if video_streams:
        stream = video_streams[0]
        try:
            report.width = int(stream.get("width") or 0)
            report.height = int(stream.get("height") or 0)
        except (TypeError, ValueError):
            report.width = report.height = 0
        if (report.width, report.height) != (WIDTH, HEIGHT):
            report.problems.append(
                f"Size {report.width}x{report.height} hai, "
                f"{WIDTH}x{HEIGHT} (vertical) chahiye"
            )
        codec = str(stream.get("codec_name") or "")
        if codec and codec != "h264":
            report.problems.append(f"Video codec {codec} hai, h264 chahiye")

    format_info = data.get("format") or {}
    try:
        report.duration = float(format_info.get("duration") or 0)
    except (TypeError, ValueError):
        report.duration = 0.0
    if report.duration <= 0 and video_streams:
        try:
            report.duration = float(video_streams[0].get("duration") or 0)
        except (TypeError, ValueError):
            report.duration = 0.0

    if report.duration <= 0:
        report.problems.append("Video ki duration padhi nahi gayi")
    else:
        if report.duration < MIN_SECONDS:
            report.problems.append(
                f"Video sirf {report.duration:.1f}s ki hai — awaaz adhoori lagti hai"
            )
        if report.duration > MAX_SECONDS:
            report.problems.append(
                f"Video {report.duration:.0f}s ki hai — {MAX_SECONDS:.0f}s se lambi "
                "video Reels/Shorts ke liye theek nahi"
            )
        if expected_duration and abs(report.duration - expected_duration) > DURATION_TOLERANCE:
            report.problems.append(
                f"Video ({report.duration:.1f}s) aur awaaz ({expected_duration:.1f}s) "
                "ka waqt match nahi karta"
            )

    if report.has_audio:
        report.mean_volume = mean_volume(video)
        if report.mean_volume is None:
            report.problems.append("Awaaz ka level padha nahi ja saka")
        elif report.mean_volume < MIN_MEAN_VOLUME:
            report.problems.append(
                f"Awaaz khaali/dheemi hai (mean volume {report.mean_volume:.0f} dB) — "
                "voiceover ban hi nahi payi lagti hai"
            )

    report.ok = not report.problems
    return report
