"""edge-tts se free voiceover, saath me har lafz ka waqt bhi.

Word timings isliye chahiye taake caption usi waqt badle jab wo lafz bola
ja raha ho (jaise padha ja raha ho waisa hi screen par aaye).
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

# edge-tts waqt 100-nanosecond ticks me deta hai.
_TICKS_PER_SECOND = 10_000_000


@dataclass
class Transcript:
    path: Path
    words: List[Tuple[float, float]] = field(default_factory=list)

    @property
    def has_timing(self) -> bool:
        return len(self.words) > 0


def synthesize(
    text: str, voice: str, out_path: Path, rate: str = "+0%"
) -> Transcript:
    if not (text or "").strip():
        raise ValueError("TTS ke liye text khali hai")

    try:
        import edge_tts
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "edge-tts install nahi hai. Chalaiye: pip install -r requirements.txt"
        ) from exc

    out_path.parent.mkdir(parents=True, exist_ok=True)
    words: List[Tuple[float, float]] = []

    async def _run() -> None:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        with open(out_path, "wb") as handle:
            async for chunk in communicate.stream():
                kind = chunk.get("type")
                if kind == "audio":
                    handle.write(chunk["data"])
                elif kind in ("WordBoundary", "SentenceBoundary"):
                    offset = float(chunk.get("offset", 0)) / _TICKS_PER_SECOND
                    duration = float(chunk.get("duration", 0)) / _TICKS_PER_SECOND
                    words.append((offset, offset + duration))

    # edge-tts kabhi kabhi beech me fail ho jata hai (rate limit) — 3 koshish.
    error: Exception | None = None
    for attempt in range(1, 4):
        words.clear()
        try:
            asyncio.run(_run())
        except Exception as exc:  # noqa: BLE001
            error = exc
        if out_path.exists() and out_path.stat().st_size > 0:
            break
        time.sleep(4 * attempt)

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError(f"Voiceover ban nahi payi: {error}")

    return Transcript(path=out_path, words=words)