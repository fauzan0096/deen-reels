# Deen Reels — ورثة الانبياء

Roz ek **sahabi ka waqiya** — Urdu narration, 1080x1920 video, aur har video
ke aakhir me **asal hawala** (kitab + hadees number + jild/safha).
YouTube aur Facebook par apne aap post ho jata hai.

**Pehli baar set kar rahe ho? → [SETUP.md](SETUP.md)** (15 minute ka checklist).

## Ek video kaise banti hai

1. `content/stories.json` se agla waqiya uthata hai (jo pehle post nahi hua).
2. Story ke `beats` — Urdu narration, har beat ke saath Arabic asal (jahan maujood ho).
3. `edge-tts` (Microsoft ki free voice) se Urdu voiceover — **har jumla alag**,
   darmiyan me chhota sa sukun, aur sanjeeda beat (وفات، ایک صفت، سبق) thori
   dheemi awaaz me (mahol banane ke liye).
4. Har beat ka apna screen, aakhir me "سبق" aur hawala card.
5. ffmpeg se mp4 (1080x1920, captions burned) — shuru me halka hook punch-in.
6. 1280x720 **thumbnail** (hook wala frame + bara title), phir YouTube/Facebook
   par upload — YouTube par custom thumbnail bhi lagti hai. Us ke baad
   `state.json` update.

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

Abhi 14 stories hain (Abu Bakr Siddiq ke 8, Umar bin Khattab ke 6). Nayi jodne ka tareeqa: `content/SOURCES.md`.

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

## Kaam ka tareeqa (approve karne ke baad post)

Workflows wapas lag gaye hain:

- **Render all episodes** — saare hisse ek saath banata hai (Artifacts se
  download kijiye). Kuch post nahi karta, kahin publish nahi karta. Sirf
  haath se chalane par chalta hai.
- **Daily Deen Reel** — roz chalta hai. Kitni videos: repo **Variable
  `VIDEOS_PER_RUN`** = `1` ya `2`.
- **Preflight check** — token/channel check.

**Posting ka switch:** repo **Variable `DRY_RUN`**

- `DRY_RUN = yes` → rozana run sirf video banata hai, **kuch post nahi hota**
  (review ke liye), aur **story aage nahi badhti** — kal phir wahi waqiya aata
  hai jab tak aap `no` na karein.
- `DRY_RUN = no` → rozana run video banata hai aur YouTube/Facebook par **post**
  bhi karta hai; us ke baad agla waqiya.

Yani pehle videos dekhein, theek lagein, phir `DRY_RUN` ko `no` kar dein —
us ke baad roz apne aap post hota rahega.

## Kya cheez pipeline ko ghalti se bachati hai

- **`Checks` workflow** — har push par seconds me: saare modules compile hote
  hain, settings (language, privacy, fonts) jaanchi jati hain, stories poore
  hain ya nahi, dono zubano me script aur captions banti hain ya nahi, aur
  Roman mode me Urdu ka koi lafz bacha to nahi.
- **Video ki aakhri jaanch** — publish se pehle `video_factory/verify.py`
  ffprobe se dekhta hai: file, size, video stream, awaaz, duration, 1080x1920,
  h264, aur awaaz khaali to nahi. Jaanch fail ho to **post nahi hota** aur
  story "posted" mark nahi hoti.
- **`state.json`** — kharab file par pipeline ruk jati hai; chup chaap reset
  nahi hoti (warna saari stories dobara post ho jati hain). Save pehle temp
  file me, phir replace — adhoori file ka khatra nahi.

Hathon se jaanch: `python -m video_factory.selftest`


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

Local par: `python scripts/preflight.py` — batata hai ki token aur channel theek hain ya nahi.

**5. Pehli video**

`DRY_RUN=yes python -m video_factory.main` — video `out/video.mp4` me banti hai,
post nahi hoti. Theek lage to `DRY_RUN` hata kar dobara chalaiye.

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
- `VIDEO_LANG` — `ur` (Urdu likhai + Urdu awaaz) ya `hi` (Roman likhai +
  Hindi awaaz — neeche dekhiye)
- `VOICE` — `ur-PK-AsadNeural` (default) ya `ur-PK-UzmaNeural` (female);
  `hi` par `hi-IN-MadhurNeural` / `hi-IN-SwaraNeural`
- `TTS_RATE` — raftaar, jaise `+5%` / `-5%`
- `PRIVACY` — `public` | `unlisted` | `private`
- `DRY_RUN` — `yes` par sirf video banti hai

### Talaffuz (awaaz me har lafz sahi)

Urdu voice Arabic naam aur deeni istilah bina harakat ke aksar galat bolti hai
("عمر" ko "amar", "قریش" ko "qaraish"). `video_factory/talaffuz.py` me aise
~200 lafz ki **harakat wali shakl** hai, aur Urdu adad (13 → "تیرہ") bhi lafzon
me badle jate hain. Ye sirf **awaaz** par lagta hai — screen par wahi Urdu
rehti hai jo `stories.json` me hai.

Koi lafz phir bhi galat bole to `content/talaffuz.json` me theek kar dein:

    {"words": {"عمر": "عُمَر"}}

Wahan ka entry hamesha andar wale lafz par bhaari padta hai. Theek karne ke
baad `python -m video_factory.selftest` chala kar dekh sakte hain.

### Roman (Hindi awaaz) mode — option

Urdu default hai. Urdu awaaz kuch lafz phir bhi galat bole to `VIDEO_LANG = hi`
se Roman likhai + Hindi awaaz wala mode chal jata hai:

- narration wahi `content/stories.json` se aati hai, magar **Roman** me —
  Urdu harf → Latin harf (`video_factory/roman.py`). Koi naya matlab nahi
  jodta, sirf likhai badalti hai.
- awaaz `hi-IN-MadhurNeural` — Hindi voice Roman lafz theek parhti hai.
- screen ke captions bhi Roman, **Noto Sans** font se.
- **Arabic asal** (aayat/hadees ka quote) jaisa hai waisa hi rehta hai,
  Naskh font me — wo kabhi Roman nahi hota.

Kisi lafz ka talaffuz galat lage to `content/roman.json` me theek kar dein:

    {"words": {"ابو بکر": "Abu Bakr"}, "phrases": {"حصہ": "hissa"}}

Wahan ka entry hamesha `roman.py` ke andar wale lafz par bhaari padta hai.

## File structure

```
video_factory/
  config.py          env settings
  i18n.py            Urdu/Roman labels, dua, hashtags
  roman.py           Urdu → Roman (Hindi awaaz ke liye)
  talaffuz.py        awaaz ke liye harakat wale lafz + Urdu adad
  stories.py         stories.json load + validate
  script_builder.py  narration + on-screen cards + title/description
  tts.py             edge-tts voiceover
  visuals.py         background art + ASS captions
  render.py          ffmpeg
  thumbnail.py       1280x720 thumbnail (hook frame + title)
  verify.py          publish se pehle video ki jaanch
  selftest.py        tez jaanch (CI)
  state.py           posted state
  uploaders/         youtube.py, facebook.py, instagram.py
content/
  stories.json       waqiyat + hawale
  talaffuz.json      awaaz ke apne lafz (Urdu mode)
  roman.json         talaffuz ke apne lafz (Roman mode)
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

## Videos dekhna

**Sirf sabse nayi video, ek hi page par:**
`https://fauzan0096.github.io/deen-reels/`

Rozana wala workflow gh-pages par sirf **aakhri bani video** rakhta hai — purani
files har run me hata di jati hain. YouTube jaisi purani video nahi, bas jo abhi
bani hai.

**Purane video hataana:** Actions → **Clean old videos** → *Run workflow*. Ye
GitHub par pade saare releases (latest, parts) aur workflow artifacts delete kar
deta hai, aur site par sirf nayi video rehne deta hai.


Har video par nishan hota hai: upar baayein channel ka naam, neeche daayein
**«ورثة الانبياء • حصہ 3/14»**.

## Imaan-dari ke notes

- Har story ka Arabic text tool (Shamela) se liya gaya hai, haath se nahi likha.
  Phir bhi publish se pehle har video **khud dekh lijiye** — ghalti ho to content
  file me theek kar dijiye.
- Kisi bhi waqiya ke saath **sirf wahi hawala** dijiye jo aap dekh sakein. Andaza
  lagaya hua hadees number ya kitab ka naam kabhi na likhiye.
- `content/stories.json` me 14 stories hain, isliye do hafte chalega;
  nayi jodte rahiye.
