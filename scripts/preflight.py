"""YouTube setup ka check — kuch post kiye bina sab kuch verify karta hai.

Chalaiye:
    python scripts/preflight.py

GitHub Actions par bhi chalta hai (workflow: "Preflight check").
Exit code 0 = sab theek, 1 = kuch theek nahi hai.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from video_factory.config import load_config  # noqa: E402
from video_factory.i18n import LANGS  # noqa: E402
from video_factory.stories import load_stories  # noqa: E402

OK = "OK  "
BAD = "FAIL"
INFO = "INFO"

_results: List[Tuple[str, str, str]] = []


def record(status: str, name: str, detail: str = "") -> None:
    _results.append((status, name, detail))


def failed() -> bool:
    return any(status == BAD for status, _, _ in _results)


def _youtube_error(exc: Exception) -> str:
    text = str(exc)
    lowered = text.lower()

    if "invalid_grant" in lowered or "invalid grant" in lowered:
        return (
            "Refresh token expire ya cancel ho gaya. "
            "scripts/youtube_auth.py dobara chalaiye (ya OAuth Playground se naya token lijiye)."
        )
    if "quotaexceeded" in lowered:
        return "Aaj ka API quota khatam hai. Kal dobara try kijiye."
    if "youtubesignuprequired" in lowered:
        return "Is Google account par YouTube channel nahi hai — pehle youtube.com par channel banaiye."
    return text[:300]


def print_report() -> None:
    width = max(len(name) for _, name, _ in _results) + 2
    print()
    for status, name, detail in _results:
        print(f"  [{status}] {name.ljust(width)} {detail}")
    print()

    names = [name for status, name, _ in _results if status == BAD]
    if names:
        print("Kuch cheezein theek karni hain:")
        for name in names:
            print(f"  - {name}")
        print("\nREADME ka 'YouTube' section dekhiye.")
    else:
        print("Sab theek hai. Ab Actions se 'Daily Deen Reel' chala kar pehli video dekhiye.")


def main() -> int:
    cfg = load_config()

    version = sys.version_info
    record(
        OK if version >= (3, 10) else BAD,
        "Python 3.10+",
        f"{version.major}.{version.minor}.{version.micro}",
    )

    for tool in ("ffmpeg", "ffprobe"):
        found = shutil.which(tool)
        record(OK if found else BAD, tool, found or "install kijiye (brew / apt-get)")

    fonts_dir = ROOT / "assets" / "fonts"
    needed = ["NotoNaskhArabic-Regular.ttf", "NotoSans-Regular.ttf"]
    missing = [name for name in needed if not (fonts_dir / name).exists()]
    record(
        OK if not missing else BAD,
        "Fonts",
        "assets/fonts theek hai" if not missing else f"missing: {', '.join(missing)}",
    )

    try:
        stories = load_stories(ROOT / "content" / "stories.json")
        record(OK, "Stories", f"{len(stories)} waqiya, sab me hawala maujood")
    except Exception as exc:  # noqa: BLE001
        record(BAD, "Stories", str(exc))

    record(
        OK if cfg.lang in LANGS else BAD,
        "VIDEO_LANG",
        f"{cfg.lang} (supported: {', '.join(sorted(LANGS))})",
    )
    record(
        OK if cfg.privacy in {"public", "unlisted", "private"} else BAD,
        "PRIVACY",
        cfg.privacy,
    )

    have_creds = bool(
        cfg.youtube_client_id and cfg.youtube_client_secret and cfg.youtube_refresh_token
    )
    if not have_creds:
        record(
            BAD,
            "YouTube credentials",
            "YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET / YOUTUBE_REFRESH_TOKEN set nahi hain",
        )
        print_report()
        return 1

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError as exc:  # pragma: no cover
        record(BAD, "Google libraries", f"pip install -r requirements.txt ({exc})")
        print_report()
        return 1

    credentials = Credentials(
        token=None,
        refresh_token=cfg.youtube_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=cfg.youtube_client_id,
        client_secret=cfg.youtube_client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )

    try:
        credentials.refresh(Request())
    except Exception as exc:  # noqa: BLE001
        record(BAD, "YouTube refresh token", _youtube_error(exc))
        print_report()
        return 1
    record(OK, "YouTube token", "naya access token mil gaya")

    try:
        service = build("youtube", "v3", credentials=credentials, cache_discovery=False)
        response = service.channels().list(part="snippet,statistics", mine=True).execute()
    except Exception as exc:  # noqa: BLE001
        record(BAD, "YouTube channel", _youtube_error(exc))
        print_report()
        return 1

    items = response.get("items") or []
    if not items:
        record(
            BAD,
            "YouTube channel",
            "is account par koi channel nahi mila — pehle youtube.com par channel banaiye",
        )
        print_report()
        return 1

    channel = items[0]
    name = (channel.get("snippet") or {}).get("title") or "(bina naam)"
    stats = channel.get("statistics") or {}
    record(
        OK,
        "YouTube channel",
        f"{name} — {stats.get('videoCount', '0')} videos, "
        f"{stats.get('subscriberCount', '?')} subscribers",
    )

    others = []
    if cfg.facebook_ready:
        others.append("facebook")
    if cfg.instagram_ready:
        others.append("instagram")
    record(
        INFO,
        "Doosre platforms",
        ", ".join(others) if others else "koi nahi (YouTube akela chalega)",
    )

    print_report()
    return 1 if failed() else 0


if __name__ == "__main__":
    sys.exit(main())
