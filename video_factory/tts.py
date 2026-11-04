"""edge-tts se free voiceover (koi API key nahi chahiye)."""

from __future__ import annotations

from pathlib import Path


def synthesize(text: str, voice: str, out_path: Path, rate: str = "+0%") -> Path:
    if not (text or "").strip():
        raise ValueError("TTS ke liye text khali hai")

    try:
        import edge_tts
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "edge-tts install nahi hai. Chalaiye: pip install -r requirements.txt"
        ) from exc

    out_path.parent.mkdir(parents=True, exist_ok=True)

    async def _run() -> None:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(str(out_path))

    import asyncio

    asyncio.run(_run())

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError("Voiceover file ban nahi payi (edge-tts se koi audio nahi mila)")
    return out_path
