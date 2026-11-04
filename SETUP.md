# SETUP — 15 minute, ek baar

Coding nahi karni. Sirf clicking hai. Phone se bhi ho jayega.

**Total: 6 hisse.** Jo main kar sakta hoon wo (1) hai; baaki tumhare account me hai.

---

## 1. GitHub repo (main kar sakta hoon)

Repo abhi GitHub par nahi hai. Bolo to main commit kar ke repo bana kar push kar dunga.
Khud karna ho to: GitHub par naya repo → is folder ko push.

**Iske baad:** Settings → Actions → General → Workflow permissions →
**Read and write permissions** → Save.
_(Ye zaroori hai, warna bot apni "kaun si story ja chuki hai" list save nahi kar payega.)_

---

## 2. Google Cloud project — sabse lamba hissa (~8 min)

[console.cloud.google.com](https://console.cloud.google.com) kholein.
**Card / billing nahi chahiye** — YouTube Data API free hai.

1. **Project banao:** upar project dropdown → **New project** → naam `deen-reels` →
   **Create**. Ban jane ke baad usi project ko select karna na bhoolein.
2. **API on karo:** ☰ menu → **APIs & Services → Library** →
   "YouTube Data API v3" search → **Enable**.
3. **OAuth consent screen:**
   - Naye console me ye page **Google Auth Platform** ke naam se khulta hai
     (APIs & Services → OAuth consent screen bhi wahi page kholta hai).
   - Pehli baar **Get started** dikhega → App name: `Deen Reels`,
     support email: apna Gmail → Audience: **External** → contact email →
     **Create**.
   - Phir **Audience → Test users → Add users** → apna Gmail → **Save**.
     (Ye qadam chhoot gaya to aage "access blocked" aayega.)
4. **Client banao:** **Clients** (purane console me **Credentials**) →
   **Create client** → Application type: **Web application** → naam `deen-reels` →
   **Authorized redirect URIs → Add URI** →
   `https://developers.google.com/oauthplayground` → **Create**.
5. Popup me **Client ID** aur **Client secret** copy kar lo. (Baad me
   Clients page se dobara dekh sakte ho.)

> Redirect URI me aage peeche kuch na lagao — na space, na `/` — bas itna hi.

---

## 3. Refresh token — 3 clicks

1. [developers.google.com/oauthplayground](https://developers.google.com/oauthplayground) kholein.
2. Upar right me **gear icon (⚙)** → **Use your own OAuth credentials** par tick →
   Client ID + Client secret paste → Close.
3. Left side list me neeche **YouTube Data API v3** → `.../auth/youtube.upload` par tick
   → **Authorize APIs** → apna Gmail → _"Google hasn't verified this app"_ aayega →
   **Advanced** → **Go to deen-reels (unsafe)** → Allow.
4. **Exchange authorization code for tokens** dabao.
5. Neeche jawab me `"refresh_token": "1//..."` likha hoga — wo copy kar lo.
   (Ye sirf ek baar dikhta hai.)

> Ye "unsafe" warning normal hai — app tumhara hi hai, tum hi use kar rahe ho.

---

## 4. GitHub me 3 secrets daalo

Repo → **Settings → Secrets and variables → Actions** → **New repository secret**:

| Naam | Kahan se |
| --- | --- |
| `YOUTUBE_CLIENT_ID` | step 2.5 |
| `YOUTUBE_CLIENT_SECRET` | step 2.5 |
| `YOUTUBE_REFRESH_TOKEN` | step 3.5 |

Chaho to **Variables** tab me `CHANNEL_NAME` bhi daal do — video par yehi naam aayega.

---

## 5. Check — kuch post nahi hoga

**Actions** → **Preflight check** → **Run workflow** → ~1 minute.

- Green tick = sab theek, channel ka naam bhi dikhega.
- Red cross = jo line me `FAIL` likha hai, wahi cheez theek karni hai.

---

## 6. Pehli video

**Actions** → **Daily Deen Reel** → **Run workflow**.
`dry_run` pehle se tick hai — is baar kuch post nahi hoga, sirf video banegi.

Run khatam hone par neeche **Artifacts → reel** se `video.mp4` download kar ke dekh lo.
Theek lage to dobara chalao, is baar `dry_run` ka tick hata kar — video YouTube par
chali jayegi.

Uske baad roz subah 8 baje (IST) khud chalti rahegi.

---

## Baad me dikkat aaye to

| Jo dikhe | Matlab | Hal |
| --- | --- | --- |
| `invalid_grant` | token expire (Testing mode) | step 3 dobara |
| `quotaExceeded` | aaj ki limit khatam | kal chala do |
| `youtubeSignupRequired` | is account par channel nahi | youtube.com par channel banao |
| Preflight me `YouTube credentials` FAIL | secrets missing/galat naam | step 4 dobara |
| Video bani par post nahi hui | ya `DRY_RUN=yes` tha, ya token galat | logs padho |

**Token har hafte expire hone se bachne ke liye:** Google Cloud →
**OAuth consent screen** → **Publish app**. App "In production" chala jayega,
token nahi marega. Verified nahi hoga (warning aayega) — apne account ke liye theek hai.

---

## Kya-mushkil hai, sach me?

- **Google Cloud (step 2):** sabse zyada clicking, ~8 minute. Ek baar ka kaam.
- **Token (step 3):** 3 minute, ek baar (Publish app kar lo to dobara nahi).
- **Secrets (step 4):** 2 minute.
- **Code, video, upload, rozana schedule:** ho chuka hai, dobara nahi karna.
