"""Bhasha ka pack: awaaz, labels, hashtags.

Do pack hain: `ur` (Urdu likhai + Urdu awaaz) aur `hi` (Roman likhai +
Hindi awaaz — Urdu voice kai lafz galat bolti hai). Naya language add karna
ho to yahan ek entry jodiye — key wahi rakhni hai jo `VIDEO_LANG` me di
jayegi.
"""

from __future__ import annotations

URDU = {
    "name": "Urdu",
    "voice": "ur-PK-AsadNeural",
    "female_voice": "ur-PK-UzmaNeural",
    # Awaaz ke liye alag shakl — warna TTS "wasra anbiya" bol deta hai.
    "channel_spoken": "وَرَثَةُ الْاَنْبِیَاء",
    "next_lines": [
        "اگلے حصے میں اس واقعے کا باقی حصہ ہے — چینل سبسکرائب کر لیں تاکہ کچھ نہ چھوٹے۔",
        "کہانی ابھی ختم نہیں ہوئی — اگلا حصہ دیکھنے کے لیے سبسکرائب کر لیں۔",
    ],
    "label_story": "صحابہ کرام کی سیرت",
    "label_lesson": "سبق",
    "label_source": "حوالہ",
    "intro_template": "{channel} میں خوش آمدید۔ آج کا واقعہ توجہ سے سنیں۔",
    "outro_lines": [
        "اگر ویڈیو پسند آئی ہو تو Like کریں، Share کریں اور Subscribe کر لیں۔",
        "ایسی ہی باتیں روز ملتی ہیں۔ Like، Share اور Subscribe ضرور کریں۔",
        "ان بزرگوں کی سیرت سے سبق لیں، اور چینل کو Subscribe کر لیں۔",
    ],
    "closing": "اللہ ہم سب کو ان بزرگوں کی سیرت پر چلنے کی توفیق دے۔ آمین",
    "cta": "Like • Share • Subscribe",
    "daily_line": "روزانہ ایک صحابی کا واقعہ، مستند حوالے کے ساتھ۔",
    "hashtags": [
        "#Shorts",
        "#صحابہ_کرام",
        "#سیرت_صحابہ",
        "#اسلامی_ویڈیوز",
        "#Seerah",
        "#Sahaba",
        "#DeenReels",
    ],
    "tags": [
        "seerah",
        "sahaba stories",
        "islamic history",
        "urdu islamic video",
        "sahaba",
        "صحابہ",
        "سیرت",
        "اسلام",
    ],
}

# Roman likhai + Hindi awaaz. `roman` True ka matlab: narration aur captions
# `video_factory/roman.py` se Roman me badle jayenge, aur awaaz hi-IN hogi.
# Screen ke text ke liye Noto Sans (Latin) font — Arabic asal Naskh me hi rehta hai.
HI_ROMAN = {
    "name": "Hindi (Roman)",
    "roman": True,
    "voice": "hi-IN-MadhurNeural",
    "female_voice": "hi-IN-SwaraNeural",
    "header_text": "Warasat-ul-Ambiya",
    "channel_spoken": "Warasat ul Ambiya",
    "text_font": "Noto Sans",
    "next_lines": [
        "Agle hisse mein is waqiye ka baaki hissa hai — channel subscribe kar "
        "lein taake kuch chhoot na jaye.",
        "Kahani abhi khatam nahi hui — agla hissa dekhne ke liye subscribe "
        "kar lein.",
    ],
    "label_story": "Sahaba ki seerat",
    "label_lesson": "Sabaq",
    "label_source": "Hawala",
    "intro_template": "{channel} mein khush aamdeed. Aaj ka waqia tawajjuh se sunein.",
    "outro_lines": [
        "Agar video pasand aayi ho to Like karein, Share karein aur Subscribe kar lein.",
        "Aisi hi baatein roz milti hain. Like, Share aur Subscribe zaroor karein.",
        "In buzurgon ki seerat se sabaq lein, aur channel ko Subscribe kar lein.",
    ],
    "closing": "Allah hum sab ko in buzurgon ki seerat par chalne ki taufeeq de. Aameen.",
    "cta": "Like • Share • Subscribe",
    "daily_line": "Rozana ek sahabi ka waqia, mustanad hawale ke saath.",
    "hashtags": [
        "#Shorts",
        "#Sahaba",
        "#Seerat",
        "#Seerah",
        "#DeenReels",
        "#IslamicShorts",
    ],
    "tags": [
        "seerah",
        "sahaba stories",
        "islamic history",
        "hindi islamic video",
        "sahaba",
    ],
    # Sanjeeda beat — awaaz thori dheemi. Naam wahi jo label Roman me banta hai.
    "solemn_labels": {
        "ek sifat",
        "wafaat",
        "dafan",
        "shahadat",
        "sabaq",
        "Sabaq",
    },
    "sign_template": "{channel} • Hissa {n}/{total}",
}

LANGS = {"ur": URDU, "hi": HI_ROMAN}


def get_lang(code: str) -> dict:
    key = (code or "ur").strip().lower()
    if key not in LANGS:
        supported = ", ".join(sorted(LANGS))
        raise KeyError(f"'{key}' abhi supported nahi hai. Filhaal: {supported}")
    return LANGS[key]
