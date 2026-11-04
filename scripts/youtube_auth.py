"""Ek baar chalane wala helper: YouTube ka refresh token banata hai.

Steps:
  1. Google Cloud Console me project banaiye, "YouTube Data API v3" enable kijiye.
  2. OAuth consent screen bhar dijiye, phir "Credentials" -> "Create credentials"
     -> "OAuth client ID" -> Application type: Desktop app.
  3. JSON download karke is repo me `client_secret.json` naam se rakhiye.
  4. Chalaiye:  python scripts/youtube_auth.py
  5. Browser me Google account se allow kijiye; terminal me refresh token milega.
     Usko GitHub Secrets me YOUTUBE_REFRESH_TOKEN ke naam se daal dijiye.

Dhyan: agar OAuth app "Testing" state me hai, refresh token 7 din me expire
ho jata hai. Toh har hafte dobara chalana padega — ya app ko production me
publish karke verification karwa lijiye.
"""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="YouTube refresh token banane ke liye")
    parser.add_argument(
        "--client-secret",
        default="client_secret.json",
        help="OAuth desktop client ka JSON (default: client_secret.json)",
    )
    args = parser.parse_args()

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Pehle dependencies install kijiye: pip install -r requirements.txt")
        return 1

    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    flow = InstalledAppFlow.from_client_secrets_file(args.client_secret, scopes)
    credentials = flow.run_local_server(
        port=0, access_type="offline", prompt="consent"
    )

    if not credentials.refresh_token:
        print("Refresh token nahi mila. Google account se app ka access hata kar dobara try kijiye.")
        return 1

    print("\nYe values GitHub Secrets me daaliye:")
    print(f"YOUTUBE_CLIENT_ID={flow.client_config.get('client_id', '')}")
    print(f"YOUTUBE_CLIENT_SECRET={flow.client_config.get('client_secret', '')}")
    print(f"YOUTUBE_REFRESH_TOKEN={credentials.refresh_token}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
