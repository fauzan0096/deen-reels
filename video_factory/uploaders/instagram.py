"""Instagram Reels upload (Instagram Graph API).

Chahiye: IG_USER_ID, IG_ACCESS_TOKEN, PUBLIC_MEDIA_BASE_URL

Instagram ka Reels publishing API video ko URL se kheenchta hai, file
seedha upload nahi hoti. Isliye video ka koi public URL chahiye —
jaise Cloudflare R2 / S3 / koi public bucket. `PUBLIC_MEDIA_BASE_URL`
me wahi base URL daaliye, file ka naam khud jud jayega.
"""

from __future__ import annotations

import time
from pathlib import Path

import requests

from ..config import Config

POLL_ATTEMPTS = 40
POLL_SECONDS = 5


def _graph(version: str, node: str) -> str:
    return f"https://graph.facebook.com/{version}/{node}"


def _json(response: requests.Response, step: str) -> dict:
    if response.status_code >= 400:
        raise RuntimeError(f"Instagram {step} fail ({response.status_code}): {response.text[:400]}")
    return response.json()


def upload(video_path: Path, caption: str, cfg: Config) -> str:
    version = cfg.meta_api_version
    token = cfg.instagram_access_token
    user_id = cfg.instagram_user_id
    base = cfg.media_base_url.rstrip("/")
    if not base:
        raise RuntimeError("PUBLIC_MEDIA_BASE_URL set nahi hai")

    video_url = f"{base}/{Path(video_path).name}"

    created = requests.post(
        _graph(version, f"{user_id}/media"),
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption[:2200],
            "share_to_feed": "true",
            "access_token": token,
        },
        timeout=120,
    )
    creation_id = _json(created, "container").get("id")
    if not creation_id:
        raise RuntimeError("Instagram ne creation id nahi di")

    for _ in range(POLL_ATTEMPTS):
        status = requests.get(
            _graph(version, creation_id),
            params={"fields": "status_code,status", "access_token": token},
            timeout=60,
        )
        payload = _json(status, "status")
        code = payload.get("status_code")
        if code == "FINISHED":
            break
        if code == "ERROR":
            raise RuntimeError(f"Instagram ne video reject ki: {payload}")
        time.sleep(POLL_SECONDS)
    else:
        raise RuntimeError("Instagram video processing time out ho gayi")

    published = requests.post(
        _graph(version, f"{user_id}/media_publish"),
        data={"creation_id": creation_id, "access_token": token},
        timeout=120,
    )
    media_id = _json(published, "publish").get("id")
    if not media_id:
        raise RuntimeError("Instagram ne media id nahi di")
    return str(media_id)
