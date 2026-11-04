"""Facebook Page par Reel upload (Graph API).

Chahiye: FB_PAGE_ID, FB_PAGE_ACCESS_TOKEN (page-level, videos scope ke saath).

Pehle Reels API try karte hain; wo na chale to normal page video upload
fallback hai.
"""

from __future__ import annotations

from pathlib import Path

import requests

from ..config import Config


def _graph(version: str, node: str) -> str:
    return f"https://graph.facebook.com/{version}/{node}"


def _raise(response: requests.Response, step: str) -> dict:
    if response.status_code >= 400:
        raise RuntimeError(f"Facebook {step} fail ({response.status_code}): {response.text[:400]}")
    return response.json()


def _upload_reel(video_path: Path, description: str, cfg: Config) -> str:
    version = cfg.meta_api_version
    page_id = cfg.facebook_page_id
    token = cfg.facebook_access_token
    size = Path(video_path).stat().st_size

    start = requests.post(
        _graph(version, f"{page_id}/video_reels"),
        data={"upload_phase": "start", "access_token": token},
        timeout=120,
    )
    payload = _raise(start, "reels start")
    video_id = payload.get("video_id")
    upload_url = payload.get("upload_url")
    if not video_id or not upload_url:
        raise RuntimeError(f"Facebook reels start se adhoora jawab: {payload}")

    with open(video_path, "rb") as handle:
        uploaded = requests.post(
            upload_url,
            headers={
                "Authorization": f"OAuth {token}",
                "offset": "0",
                "file_size": str(size),
                "Content-Type": "application/octet-stream",
            },
            data=handle,
            timeout=1800,
        )
    if uploaded.status_code >= 400:
        raise RuntimeError(
            f"Facebook reels upload fail ({uploaded.status_code}): {uploaded.text[:400]}"
        )

    finish = requests.post(
        _graph(version, f"{page_id}/video_reels"),
        data={
            "upload_phase": "finish",
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": description[:5000],
            "access_token": token,
        },
        timeout=180,
    )
    _raise(finish, "reels finish")
    return str(video_id)


def _upload_page_video(video_path: Path, description: str, cfg: Config) -> str:
    with open(video_path, "rb") as handle:
        response = requests.post(
            _graph(cfg.meta_api_version, f"{cfg.facebook_page_id}/videos"),
            data={
                "description": description[:5000],
                "access_token": cfg.facebook_access_token,
            },
            files={"source": handle},
            timeout=1800,
        )
    payload = _raise(response, "page video upload")
    video_id = payload.get("id")
    if not video_id:
        raise RuntimeError(f"Facebook se video id nahi mili: {payload}")
    return str(video_id)


def upload(video_path: Path, description: str, cfg: Config, log=print) -> str:
    try:
        return _upload_reel(video_path, description, cfg)
    except Exception as exc:  # noqa: BLE001 - fallback chahiye
        log(f"[facebook] Reels fail ({exc}); normal page video try kar rahe hain")
        return _upload_page_video(video_path, description, cfg)
