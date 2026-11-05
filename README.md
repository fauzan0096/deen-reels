# Deen Reels — ورثة الانبياء

Roz ek **sahabi ka waqiya** — Urdu narration, 1080x1920 video, aur har video
ke aakhir me **asal hawala** (kitab + hadees number + jild/safha).
YouTube aur Facebook par apne aap post ho jata hai.

**Pehli baar set kar rahe ho? → [SETUP.md](SETUP.md)** (15 minute ka checklist).

## Ek video kaise banti hai

1. `content/stories.json` se agla waqiya uthata hai (jo pehle post nahi hua).
2. Story ke `beats` — Urdu narration, har beat ke saath Arabic asal (jahan maujood ho).
3. `edge-tts` (Microsoft ki free voice) se Urdu voiceover.
4. Har beat ka apna screen, aakhir me "سبق" aur hawala card.
5. ffmpeg se mp4 (1080x1920, captions burned).
6. YouTube / Facebook par upload, phir `state.json` update.

Video me jo bhi Arabic likha ya bola jata hai wo seedha `stories.json` se aata hai —
koi AI us waqt kuch likhta nahi.

## Content ka usool (sabse ahem)

Har story ke saath `source` dena **lazmi** hai, warna pipeline story load hi nahi karti.
Usul yeh hain:

- Story **Sahihain (صحيح البخاري / صحيح مسلم)** ya kisi mustanad kitab se ho.
- Hawala: **kitab ka naam + hadees number + jild/safha** — jaisa Shamela dikhati hai.
- Hadees ki **sanad/grading apne tor par nahi likhni** — jo tool/kitab me likha hai wahi jayega.
- Tarjuma apne alfaz me ho sakta hai, lekin **Arabic quote harf-ba-harf** ho.
- `lesson` sirf ek chhota nateeja hai — tafseer ya sharah ka dawa nahi.

Abhi 8 stories hain (Abu Bakr Siddiq ka poora silsila). Nayi jodne ka tareeqa: `content/SOURCES.md`.

## Kya chahiye

- Python 3.10+
- ffmpeg (`brew install ffmpeg` ya `sudo apt-get install -y ffmpeg`)
- Internet (voiceover + uploads)

## Local par chala kar dekhna

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
DRY_RUN=yes python -m video_factory.main
```

Video: `out/video.mp4`, details: `out/metadata.json`.
`DRY_RUN=yes` = video banegi, post nahi hogi.

## Roz automatic (GitHub Actions) — free

1. Ye folder GitHub par repo bana kar push kijiye.
2. Repo → **Settings → Actions → General → Workflow permissions** →
   **Read and write permissions** (state commit karne ke liye zaroori).
3. **Settings → Secrets and variables → Actions** me credentials daaliye.
4. **Actions** → **Preflight check** → **Run workflow** (kuch post nahi hoga,
   sirf batayega ki setup theek hai ya nahi).
5. **Actions** → **Daily Deen Reel** → **Run workflow**, pehle `dry_run` on rakh kar.

Default timing `02:30 UTC` = `08:00 IST`. Badalna ho to
`.github/workflows/daily.yml` me cron line badal dijiye (cron UTC me hota hai).

## Platform setup

Jitne platforms configure karenge, utni jagah post hoga. Sirf YouTube se shuru
karna sabse aasan hai.

### YouTube — step by step

Sab kuch browser se hota hai, phone se bhi. Teen cheezein chahiye: Google Cloud
project, refresh token, aur GitHub secrets.

**1. Google Cloud project (ek baar)**

1. [console.cloud.google.com](https://console.cloud.google.com/) → naya project (naam: `deen-reels`).
2. **APIs & Services → Library** → "YouTube Data API v3" → **Enable**.
3. **OAuth consent screen** → External → app ka naam + apna email → Save.
   Test users me apna Gmail add kijiye.
4. **Credentials → Create credentials → OAuth client ID**:
   - Phone se token lena hai → **Web application**, aur **Authorized redirect URI**:
     `https://developers.google.com/oauthplayground`
   - Computer par `scripts/youtube_auth.py` chalayenge → **Desktop app**
5. Client ID aur Client secret copy kar lijiye.

**2. Refresh token — do tareeqe**

*Phone / sirf browser:*

1. [developers.google.com/oauthplayground](https://developers.google.com/oauthplayground) kholein.
2. Gear icon (settings) → **Use your own OAuth credentials** → client id + secret daalein.
3. Left list me **YouTube Data API v3** → `https://www.googleapis.com/auth/youtube.upload`
   → **Authorize APIs** → Gmail se sign in → "unverified app" par *Advanced → Go to …*.
4. **Exchange authorization code for tokens** dabaiye → `refresh_token` copy kar lijiye.

*Computer:*

```bash
python scripts/youtube_auth.py      # client_secret.json repo me rakhiye
```

**3. GitHub secrets**

Repo → **Settings → Secrets and variables → Actions → New repository secret**:

- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

Chaha to **Variables** tab me `CHANNEL_NAME` bhi daal dijiye (video par yehi naam dikhega).

**4. Check kijiye (kuch post nahi hoga)**

**Actions → Preflight check → Run workflow**. Green tick = sab theek.
Local par bhi: `python scripts/preflight.py`.

**5. Pehli video**

**Actions → Daily Deen Reel → Run workflow** → `dry_run` par tick → run ke baad
**Artifacts → reel** se `video.mp4` download kar ke dekh lijiye. Theek lage to
`dry_run` hata kar dobara chalaiye.

> **Token expiry:** OAuth app jab tak "Testing" me hai, refresh token **7 din** me
> expire hota hai (har hafte naya token daalna padega). Isse bachne ke liye
> **OAuth consent screen → Publish app** kar dijiye — app "In production" chala
> jayega aur token nahi expire hoga. App verified nahi hoga (warning screen aayega)
> lekin apne hi account ke liye ye theek hai.

> **Quota:** ek upload ~1600 units leta hai, default limit 10,000/day hai —
> roz ek video ke liye kaafi hai.

### Facebook Page

1. [developers.facebook.com](https://developers.facebook.com/) par app (type: Business).
2. **Facebook Login** product add kijiye.
3. [Graph API Explorer](https://developers.facebook.com/tools/explorer/) me app select karke
   `pages_manage_posts`, `pages_read_engagement`, `publish_video` ke saath
   **Get Page Access Token** lijiye.
4. Short-lived token ko long-lived me badaliye:

   ```
   GET /oauth/access_token?grant_type=fb_exchange_token
       &client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=TOKEN
   ```

5. Secrets: `FB_PAGE_ID` (page → About → Page ID), `FB_PAGE_ACCESS_TOKEN`.

Pipeline pehle Page **Reels** API try karta hai, na chale to normal page video.

### Instagram (baad me)

Instagram ka Reels API file leta hi nahi — video ka **public URL** chahiye
(Cloudflare R2 / S3). Setup ke liye `IG_USER_ID`, `IG_ACCESS_TOKEN` aur
`PUBLIC_MEDIA_BASE_URL` chahiye. Jab tak public host na ho, Instagram chhod dijiye.

## Settings

`.env` (local) ya GitHub me Secret/Variable:

- `CHANNEL_NAME` — video par dikhne wala naam
- `VIDEO_LANG` — filhaal sirf `ur`
- `VOICE` — `ur-PK-AsadNeural` (default) ya `ur-PK-UzmaNeural` (female)
- `TTS_RATE` — raftaar, jaise `+5%` / `-5%`
- `PRIVACY` — `public` | `unlisted` | `private`
- `DRY_RUN` — `yes` par sirf video banti hai

## File structure

```
video_factory/
  config.py          env settings
  i18n.py            Urdu labels, dua, hashtags
  stories.py         stories.json load + validate
  script_builder.py  narration + on-screen cards + title/description
  tts.py             edge-tts voiceover
  visuals.py         background art + ASS captions
  render.py          ffmpeg
  state.py           posted state
  uploaders/         youtube.py, facebook.py, instagram.py
content/
  stories.json       waqiyat + hawale
  SOURCES.md         nayi story jodne ka tareeqa
assets/fonts/        Noto Naskh Arabic + Noto Sans (OFL)
scripts/
  youtube_auth.py    refresh token (computer par)
  preflight.py       setup ka check
```

## Apne background (tasveerein ya video)

Bana hua sehra background nahi chahiye to apni tasveerein daal do:

- `assets/backgrounds/` folder banao aur wahan `1.jpg`, `2.jpg`, `3.jpg`... rakho
  → pipeline unki **slideshow** banayegi, har tasveer par halka zoom/pan (motion).
- Ya ek hi file: `assets/background.jpg` (photo) / `assets/background.mp4` (video loop).
- Tasveer vertical (1080x1920) ho to sabse acha; warna beech se crop hogi.
- Tasveerein apni hon ya free license wali — kisi aur ki video se frame utha kar na lagao.

## Imaan-dari ke notes

- Har story ka Arabic text tool (Shamela) se liya gaya hai, haath se nahi likha.
  Phir bhi publish se pehle har video **khud dekh lijiye** — ghalti ho to content
  file me theek kar dijiye.
- Kisi bhi waqiya ke saath **sirf wahi hawala** dijiye jo aap dekh sakein. Andaza
  lagaya hua hadees number ya kitab ka naam kabhi na likhiye.
- `content/stories.json` me 8 stories hain, isliye ek hafte se zyada chalega;
  nayi jodte rahiye.
