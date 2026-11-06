# Skills — kya apnaya

Uploaded skills (3D cartoon short, presenter intro editor, shorts/YouTube agent
packs) padhe gaye the. Wo zyada tar doosre format ke liye the — Remotion/three.js
cartoon, presenter footage, brand graphics — is liye files hata di gayi aur sirf
wo usool rakhe gaye jo is channel par lagte hain. Ye note wahi nichor hai.

## Apnaye gaye

- **Hook pehle:** pehli line me poora wahi "absurd" ya hairat wali baat
  (`stories.json` -> `hook`). Har video isi se shuru hota hai.
- **Captions sab se aakhir me** aur safe area ke andar — captions video par
  burn hoti hain, background ke upar, kisi cheez ke neeche nahi.
- **Koi static hold nahi:** video background chalta hai, aakhir me freeze hota
  hai (logo ke liye) — beech me rukta nahi.
- **Hawala hamesha:** har video ke aakhir me kitab + hadees/panna.
- **Thumbnail:** har video ka apna `thumbnail.jpg` (1280x720) — hook wale frame
  par bara title aur channel ka naam (`video_factory/thumbnail.py`, libass se
  likha jata hai taake Urdu/Arabic shaping theek rahe). Ek hi video par lagta
  hai, site par poster banta hai, YouTube par custom thumbnail ki tarah jata
  hai (`thumbnails.set`), aur hisse ke folder me alag file rehta hai.
- **Hashtags aur description:** title + hook + beats + sabaq + hawala + dua,
  aakhir me hashtags — bhasha ke hashtags, sahabi ka naam (`#AbuBakr`,
  `#Umar`) aur hissa number (`#Part3`). YouTube ke tags bhi isi se bante hain.
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

- Hook ke waqt punch-in: ab `HOOK_ZOOM` (default `yes`) se pehle ~2 second me
  halka zoom (1.0 → 1.05) lagta hai; ffmpeg par na chale to pipeline khud bina
  zoom render kar leti hai.
