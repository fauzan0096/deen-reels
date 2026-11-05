"""Bhasha ka pack: awaaz, labels, hashtags.

Filhaal sirf Urdu support hai. Naya language add karna ho to yahan ek
entry jodiye — key wahi rakhni hai jo `VIDEO_LANG` me di jayegi.
"""

from __future__ import annotations

URDU = {
    "name": "Urdu",
    "voice": "ur-PK-AsadNeural",
    "female_voice": "ur-PK-UzmaNeural",
    "label_story": "صحابہ کرام کی سیرت",
    "label_lesson": "سبق",
    "label_source": "حوالہ",
    "intro_template": "{channel} میں خوش آمدید۔ آج کا واقعہ توجہ سے سنیں۔",
    "outro_lines": [
        "اگر یہ واقعہ پسند آیا تو چینل کو سبسکرائب کریں اور اگلے واقعے کا انتظار کریں۔",
        "ایسی ہی سیرت کی باتیں روز ملتی ہیں — چینل سبسکرائب کر لیں تاکہ کچھ چھوٹے نہ جائیں۔",
        "یاد رکھیں: ہمیں ان بزرگوں کی سیرت سے سبق لینا ہے۔ چینل کو سبسکرائب کر کے ساتھ رہیں۔",
    ],
    "closing": "اللہ ہم سب کو ان بزرگوں کی سیرت پر چلنے کی توفیق دے۔ آمین",
    "cta": "ایسے اور واقعات کے لیے چینل کو سبسکرائب کریں۔",
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
