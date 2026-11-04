"""YouTube upload (YouTube Data API v3).

Chahiye:
  YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN
Refresh token scripts/youtube_auth.py ya OAuth Playground se banta hai.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from ..config import Config

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
ALLOWED_PRIVACY = {"public", "unlisted", "private"}


def _privacy(value: str) -> str:
    value = (value or "").strip().lower()
    return value if value in ALLOWED_PRIVACY else "public"


def _error_text(exc: Exception) -> str:
    """Google ki error ko aise likhta hai jo samajh aaye."""
    status = getattr(exc, "status_code", None)
    text = str(getattr(exc, "content", "") or exc)
    lowered = text.lower()

    if "invalid_grant" in lowered or "invalid grant" in lowered:
        return (
            "Refresh token expire ya cancel ho gaya (Testing mode me 7 din me hota hai). "
            "scripts/youtube_auth.py dobara chalaiye, ya OAuth Playground se naya token lijiye."
        )
    if "quotaexceeded" in lowered:
        return (
            "Aaj ka YouTube API quota khatam ho gaya. Ek upload ~1600 units leta hai "
            "aur default limit 10,000/day hai — kal dobara chalega."
        )
    if "uploadlimitexceeded" in lowered:
        return "Channel ki daily upload limit poori ho gayi hai."
    if "youtubesignuprequired" in lowered:
        return "Is Google account par YouTube channel nahi hai — pehle youtube.com par banaiye."
    if status == 401:
        return "YouTube ne authorize nahi kiya — refresh token dobara banaiye."
    if status == 403:
        return f"YouTube ne mana kar diya (403): {text[:300]}"
    return f"YouTube upload fail: {text[:400]}"


def build_credentials(cfg: Config):
    from google.oauth2.credentials import Credentials

    return Credentials(
        token=None,
        refresh_token=cfg.youtube_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=cfg.youtube_client_id,
        client_secret=cfg.youtube_client_secret,
        scopes=SCOPES,
    )


def upload(
    video_path: Path,
    title: str,
    description: str,
    tags: List[str],
    cfg: Config,
) -> str:
    """Video upload karta hai aur video id lautata hai."""
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    credentials = build_credentials(cfg)
    service = build("youtube", "v3", credentials=credentials, cache_discovery=False)

    body = {
        "snippet": {
            "title": title[:100].replace("<", "").replace(">", ""),
            "description": description[:5000],
            "tags": tags[:30],
            "categoryId": str(cfg.youtube_category_id),
            "defaultLanguage": "ur",
            "defaultAudioLanguage": "ur",
        },
        "status": {
            "privacyStatus": _privacy(cfg.privacy),
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4"
    )
    request = service.videos().insert(
        part="snippet,status", body=body, media_body=media
    )

    response = None
    try:
        while response is None:
            _, response = request.next_chunk()
    except HttpError as exc:
        raise RuntimeError(_error_text(exc)) from exc

    video_id = (response or {}).get("id")
    if not video_id:
        raise RuntimeError("YouTube ne video id nahi di")
    return str(video_id)
