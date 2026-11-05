# Skills — kya apnaya, kya nahi

Repo me uploaded skills padhe gaye (`SKILL.md` — cartoon 3D short, `SKILL 2.md` —
Hassan intro editor, `meri-skills-sab-ek-file.md`). Ye channel in se alag hai
(koi presenter footage nahi, koi Remotion/three.js nahi), is liye sirf wo
usool liye jo yahan lagte hain:

## Apnaye gaye

- **Hook pehle:** pehli line me poora wahi "absurd" ya hairat wali baat
  (`stories.json` -> `hook`). Har video isi se shuru hota hai.
- **Captions sab se aakhir me** aur safe area ke andar — captions video par
  burn hoti hain, background ke upar, kisi cheez ke neeche nahi.
- **Koi static hold nahi:** video background chalta hai, aakhir me freeze hota
  hai (logo ke liye) — beech me rukta nahi.
- **Hawala hamesha:** har video ke aakhir me kitab + hadees/panna.
- **Thumbnail:** har hisse ka `thumbnail.jpg` video ke hook wale frame se banta
  hai (`video_factory/batch.py` -> `make_thumbnail`). Gallery me poster ki
  tarah aur release me alag file ki tarah milta hai.
- **Nishan:** har video par channel + hissa number (`حصہ 3/14`).

## Nahi lagte (yahan matlab nahi)

- 3D cartoon world, Remotion/three.js, ink pass, DOF, bloom — wo unke cartoon
  format ke liye hai; hamara format: saada background + Urdu narration + Arabic
  matn.
- Presenter-led intro editing (face-safe cards, inset, brand logos, GitHub repo
  screen recordings) — hamare videos me presenter nahi.
- "No captions" wala rule unke style ka hai — hamare channel me captions
  zaroori hain (Urdu sunne wale bhi hain).

## Jo aage lag sakta hai

- YouTube thumbnail upload (is ke liye `youtube.upload` scope me
  `thumbnails.set` add karna padega).
- Hook ke waqt halka punch-in (zoom 1.0 -> 1.05) — abhi background video chalta
  hai, is liye chhoda nahi gaya.
