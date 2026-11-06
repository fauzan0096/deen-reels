"""Environment se settings padhta hai.

Sab kuch environment variables se aata hai, taake GitHub Actions ke
Secrets/Variables seedha kaam karein. Local par `.env` file bhi chalegi.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:  # dotenv optional hai, lekin local use ke liye kaam ka hai
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

ROOT = Path(__file__).resolve().parent.parent

if load_dotenv is not None:
    load_dotenv(ROOT / ".env")

WIDTH = 1080
HEIGHT = 1920


def _env(name: str, default: str = "") -> str:
    value = os.environ.get(name)
    if value is None:
        return default
    value = value.strip()
    # JSON se copy karte waqt value ke saath quotes bhi aa jate hain.
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1].strip()
    return value or default


def _env_bool(name: str, default: bool = False) -> bool:
    raw = _env(name, "yes" if default else "no").lower()
    return raw in {"1", "true", "yes", "y", "on", "haan"}


@dataclass
class Config:
    channel_name: str = "ورثة الانبياء"
    lang: str = "ur"
    voice: str = ""
    tts_rate: str = "+0%"
    privacy: str = "public"
    dry_run: bool = False
    ambience: bool = True
    logo: bool = False
    hook_zoom: bool = True

    youtube_client_id: str = ""
    youtube_client_secret: str = ""
    youtube_refresh_token: str = ""
    youtube_category_id: str = "27"  # 27 = Education

    facebook_page_id: str = ""
    facebook_access_token: str = ""

    instagram_user_id: str = ""
    instagram_access_token: str = ""
    media_base_url: str = ""

    meta_api_version: str = "v21.0"

    @property
    def out_dir(self) -> Path:
        return ROOT / "out"

    @property
    def fonts_dir(self) -> Path:
        return ROOT / "assets" / "fonts"

    @property
    def youtube_ready(self) -> bool:
        return bool(
            self.youtube_client_id
            and self.youtube_client_secret
            and self.youtube_refresh_token
        )

    @property
    def facebook_ready(self) -> bool:
        return bool(self.facebook_page_id and self.facebook_access_token)

    @property
    def instagram_ready(self) -> bool:
        return bool(
            self.instagram_user_id
            and self.instagram_access_token
            and self.media_base_url
        )


def load_config() -> Config:
    return Config(
        channel_name=_env("CHANNEL_NAME", "ورثة الانبياء"),
        lang=_env("VIDEO_LANG", "ur").lower(),
        voice=_env("VOICE", ""),
        tts_rate=_env("TTS_RATE", "+0%"),
        privacy=_env("PRIVACY", "public").lower(),
        dry_run=_env_bool("DRY_RUN", False),
        ambience=_env_bool("AMBIENCE", True),
        logo=_env_bool("LOGO", False),
        hook_zoom=_env_bool("HOOK_ZOOM", True),
        youtube_client_id=_env("YOUTUBE_CLIENT_ID"),
        youtube_client_secret=_env("YOUTUBE_CLIENT_SECRET"),
        youtube_refresh_token=_env("YOUTUBE_REFRESH_TOKEN"),
        youtube_category_id=_env("YOUTUBE_CATEGORY_ID", "27"),
        facebook_page_id=_env("FB_PAGE_ID"),
        facebook_access_token=_env("FB_PAGE_ACCESS_TOKEN"),
        instagram_user_id=_env("IG_USER_ID"),
        instagram_access_token=_env("IG_ACCESS_TOKEN"),
        media_base_url=_env("PUBLIC_MEDIA_BASE_URL"),
        meta_api_version=_env("META_API_VERSION", "v21.0"),
    )
