"""Bhasha ka pack: awaaz, labels, hashtags.

Filhaal sirf Urdu support hai. Naya language add karna ho to yahan ek
entry jodiye — key wahi rakhni hai jo `VIDEO_LANG` me di jayegi.
"""

from __future__ import annotations

URDU = {
    "name": "Urdu",
    "voice": "ur-PK-AsadNeural",
    "female_voice": "ur-PK-UzmaNeural",
    # Awaaz ke liye alag shakl — warna TTS "wasra anbiya" bol deta hai.
    "channel_spoken": "وراثة الأنبياء",
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

LANGS = {"ur": URDU}


def get_lang(code: str) -> dict:
    key = (code or "ur").strip().lower()
    if key not in LANGS:
        supported = ", ".join(sorted(LANGS))
        raise KeyError(f"'{key}' abhi supported nahi hai. Filhaal: {supported}")
    return LANGS[key]
