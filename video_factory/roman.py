"""Urdu → Roman (Latin) — Hindi awaaz ke liye.

Kyun: Urdu ki awaaz (ur-PK) kai lafz galat bolti hai. Is liye ek option ye hai
ki narration Roman me likhi jaye aur Hindi awaaz (hi-IN) usay parhe — Hindi
voice Roman lafz theek parhti hai.

Usool wahi hai jo poore project ka hai: text `content/stories.json` se hi aata
hai. Yahan sirf uska *script* badalta hai (Urdu harf → Latin harf). Koi naya
matlab, koi nayi baat add nahi hoti.

Talaffuz theek rahe is ke liye teen teh:

1. PHRASES — poore juz (رضی اللہ عنہ، صلی اللہ علیہ وسلم، ابو بکر).
2. WORDS   — aksar aane wale lafz, sahi Roman hija ke saath.
3. Upar wali dono me na mile to harf-ba-harf tabdeel (aakhri rasta).

Apna lafz theek karna ho to `content/roman.json` me daal dein:

    {"words": {"ابو بکر": "Abu Bakr"}, "phrases": {"حصہ": "hissa"}}

Wahan ka entry hamesha upar chalta hai.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Tuple

ROOT = Path(__file__).resolve().parent.parent
OVERRIDES_PATH = ROOT / "content" / "roman.json"

URDU_RE = re.compile(r"[\u0600-\u06FF]")

# Screen par chhapne wale ascii, aur Urdu ki punctuation.
_PUNCT = str.maketrans(
    {"۔": ".", "،": ",", "؛": ";", "؟": "?", "٪": "%", "ـ": "-"}
)

_DIGITS = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"
)

# Zabar/zer/pesh waghaira — hija me shamil nahi karte.
_MARKS = "ًٌٍَُِّْٰٖٓٗ"

_CONSONANTS = set("bcdfghjklmnpqrstvwxyz")


# ---------------------------------------------------------------- huroof

_LETTERS: Dict[str, str] = {
    "آ": "aa",
    "ا": "a",
    "ب": "b",
    "پ": "p",
    "ت": "t",
    "ٹ": "t",
    "ث": "s",
    "ج": "j",
    "چ": "ch",
    "ح": "h",
    "خ": "kh",
    "د": "d",
    "ڈ": "d",
    "ذ": "z",
    "ر": "r",
    "ڑ": "r",
    "ز": "z",
    "ژ": "zh",
    "س": "s",
    "ش": "sh",
    "ص": "s",
    "ض": "z",
    "ط": "t",
    "ظ": "z",
    "ع": "",
    "غ": "gh",
    "ف": "f",
    "ق": "k",
    "ک": "k",
    "گ": "g",
    "ل": "l",
    "م": "m",
    "ن": "n",
    "ں": "n",
    "و": "o",
    "ہ": "h",
    "ھ": "h",
    "ء": "",
    "ی": "i",
    "ے": "e",
    "ئ": "i",
    "ؤ": "o",
    "ۃ": "t",
    "ة": "t",
    "ى": "a",
}

# Do harf mil kar ek awaaz: بھ، کھ، چھ ...
_ASPIRATED: Dict[str, str] = {
    "ب": "bh",
    "پ": "ph",
    "ت": "th",
    "ٹ": "th",
    "ج": "jh",
    "چ": "chh",
    "د": "dh",
    "ڈ": "dh",
    "ڑ": "rh",
    "ک": "kh",
    "گ": "gh",
    "ل": "lh",
    "م": "mh",
    "ن": "nh",
}


# ------------------------------------------------------------------ juz

_PHRASES_BUILTIN: Dict[str, str] = {
    "صلی اللہ علیہ وسلم": "sallallahu alaihi wasallam",
    "رضی اللہ عنہم اجمعین": "raziallahu anhum ajmaeen",
    "رضی اللہ عنہم": "raziallahu anhum",
    "رضی اللہ عنہما": "raziallahu anhuma",
    "رضی اللہ عنہا": "raziallahu anha",
    "رضی اللہ عنہ": "raziallahu anhu",
    "خلیفۃ رسول اللہ": "khaleefat ur rasool Allah",
    "خلیفۃ اللہ": "khaleefatullah",
    "امیر المؤمنین": "ameer ul momineen",
    "یا رسول اللہ": "ya rasool Allah",
    "یا خلیفۃ رسول اللہ": "ya khaleefat ur rasool Allah",
    "رسول اللہ": "rasool Allah",
    "ورثة الانبياء": "Warasat-ul-Ambiya",
    "ورثة الانبیاء": "Warasat-ul-Ambiya",
    "ابو بکر صدیق": "Abu Bakr Siddiq",
    "ابو بکر": "Abu Bakr",
    "ابی بکر": "Abi Bakr",
    "عبد اللہ بن ابی قحافہ": "Abdullah bin Abi Kahafa",
    "عبد اللہ بن مسعود": "Abdullah bin Masood",
    "عبد اللہ بن عمر": "Abdullah bin Umar",
    "عبد الرحمن بن عوف": "Abdur Rahman bin Auf",
    "عبد الرحمن بن ابی بکر": "Abdur Rahman bin Abi Bakr",
    "ابو عبیدہ بن الجراح": "Abu Ubaidah bin al-Jarrah",
    "عمر بن خطاب": "Umar bin Khattab",
    "عثمان بن عفان": "Usman bin Affan",
    "علی بن ابی طالب": "Ali bin Abi Talib",
    "ابن عبد البر": "Ibn Abdil Barr",
    "ابو لؤلؤہ": "Abu Lulu",
    "سقیفہ بنو ساعدہ": "Sakeefa Banu Saida",
    "بیعت رضوان": "baiyat-e-Rizwan",
    "عام الفیل": "aam-ul-feel",
    "فجارِ اعظم": "fijar-e-azam",
    "فجار اعظم": "fijar-e-azam",
    "صلح حدیبیہ": "sulh Hudaibiya",
    "ابو حفص": "Abu Hafs",
    "ابو بکر کا خوخہ": "Abu Bakr ka khaukhah",
    "مسجد نبوی": "Masjid-e-Nabvi",
    "عبد الکعبہ": "Abdul Kaaba",
    "بے قرار": "be qaraar",
    "ذی الحجہ": "Zil Hijjah",
}


# ------------------------------------------------------------------ lafz

_WORDS_BUILTIN: Dict[str, str] = {
    # --- jodne wale lafz
    "کے": "ke",
    "کی": "ki",
    "کا": "ka",
    "کو": "ko",
    "میں": "mein",
    "سے": "se",
    "پر": "par",
    "اور": "aur",
    "ہے": "hai",
    "ہیں": "hain",
    "نہیں": "nahi",
    "تھا": "tha",
    "تھی": "thi",
    "تھے": "the",
    "ہوا": "hua",
    "ہوئی": "hui",
    "ہوئے": "hue",
    "نے": "ne",
    "وہ": "woh",
    "یہ": "yeh",
    "جو": "jo",
    "تو": "to",
    "بھی": "bhi",
    "کہ": "keh",
    "ہو": "ho",
    "کر": "kar",
    "کیا": "kiya",
    "کرنے": "karne",
    "کرتے": "karte",
    "کرتا": "karta",
    "کرتی": "karti",
    "کرے": "kare",
    "کریں": "karein",
    "کروں": "karoon",
    "کرنا": "karna",
    "کرلیں": "kar lein",
    "گیا": "gaya",
    "گئی": "gayi",
    "گئے": "gaye",
    "دیا": "diya",
    "دی": "di",
    "لیا": "liya",
    "لیے": "liye",
    "آیا": "aaya",
    "آئی": "aayi",
    "آئے": "aaye",
    "آ": "aa",
    "بن": "ban",
    "بنا": "bana",
    "بنے": "bane",
    "بنایا": "banaya",
    "رہا": "raha",
    "رہی": "rahi",
    "رہے": "rahe",
    "جاتا": "jaata",
    "جاتی": "jaati",
    "جاتے": "jaate",
    "جائے": "jaaye",
    "جا": "ja",
    "رکھا": "rakha",
    "رکھی": "rakhi",
    "رکھے": "rakhe",
    "رکھیں": "rakhein",
    "دے": "de",
    "لگا": "laga",
    "لگی": "lagi",
    "لگے": "lage",
    "لگائی": "lagayi",
    "پڑا": "pada",
    "پڑی": "padi",
    "سکتا": "sakta",
    "سکتے": "sakte",
    "چاہے": "chahe",
    "چاہتا": "chahta",
    "ہونا": "hona",
    "ہوگا": "hoga",
    "ہوگی": "hogi",
    "چلے": "chale",
    "چلا": "chala",
    "چلی": "chali",
    "ملا": "mila",
    "ملی": "mili",
    "ملے": "mile",
    "سنو": "suno",
    "سنے": "sune",
    "سننے": "sunne",
    "سنا": "suna",
    "سنین": "sunein",
    "سنیں": "sunein",
    "دیکھا": "dekha",
    "دیکھے": "dekhe",
    "دیکھ": "dekh",
    "دیکھیں": "dekhein",
    "پوچھا": "poocha",
    "کہا": "kaha",
    "کہتے": "kehte",
    "کہتا": "kehta",
    "کہتی": "kehti",
    "کہیں": "kahein",
    "بتایا": "bataya",
    "بتاؤ": "batao",
    "بتائیں": "batayein",
    "فرمایا": "farmaya",
    "فرماتے": "farmate",
    "فرمانے": "farmanay",
    "فرمایا،": "farmaya,",
    "ارشاد": "irshad",
    "بیان": "bayan",
    "روایت": "riwayat",
    "لکھتے": "likhte",
    "لکھا": "likha",
    "لکھیں": "likhein",
    "کھڑا": "khada",
    "کھڑے": "khade",
    "بیٹھا": "baitha",
    "بیٹھے": "baithe",
    "گرے": "gire",
    "ٹوٹ": "toot",
    "ہلے": "hile",
    "ہل": "hil",
    "ٹوٹا": "toota",
    # --- aanay wale lafz
    "ساتھ": "saath",
    "بعد": "baad",
    "پہلے": "pehle",
    "پھر": "phir",
    "اب": "ab",
    "ابھی": "abhi",
    "آج": "aaj",
    "کل": "kal",
    "یہی": "yahi",
    "وہی": "wahi",
    "اسی": "usi",
    "اسیں": "usain",
    "ایک": "ek",
    "دو": "do",
    "تین": "teen",
    "چار": "chaar",
    "پانچ": "paanch",
    "چھ": "chhah",
    "سات": "saat",
    "آٹھ": "aath",
    "نو": "nau",
    "دس": "das",
    "گیارہ": "gyaarah",
    "بارہ": "baarah",
    "تیرہ": "terah",
    "چودہ": "chaudah",
    "پندرہ": "pandrah",
    "بیس": "bees",
    "تیس": "tees",
    "چالیس": "chalees",
    "پچاس": "pachaas",
    "ساٹھ": "saath",
    "ستر": "sattar",
    "نوے": "nawwe",
    "سو": "sau",
    "ہزار": "hazaar",
    "لاکھ": "laakh",
    "سب": "sab",
    "کچھ": "kuch",
    "بہت": "bahut",
    "صرف": "sirf",
    "مگر": "magar",
    "لیکن": "lekin",
    "اگر": "agar",
    "جب": "jab",
    "کب": "kab",
    "کیوں": "kyun",
    "کیسے": "kaise",
    "کیسا": "kaisa",
    "کون": "kaun",
    "کس": "kis",
    "کسی": "kisi",
    "کہاں": "kahaan",
    "یہاں": "yahaan",
    "وہاں": "wahaan",
    "پاس": "paas",
    "قریب": "kareeb",
    "دور": "door",
    "آگے": "aage",
    "پیچھے": "peeche",
    "اوپر": "oopar",
    "نیچے": "neeche",
    "اندر": "andar",
    "باہر": "bahar",
    "دائیں": "daayen",
    "بائیں": "baayen",
    "سامنے": "saamne",
    "بند": "band",
    "کھلا": "khula",
    "کھول": "khol",
    "لمبا": "lamba",
    "گہرا": "gehra",
    "بڑا": "bada",
    "بڑے": "bade",
    "بڑی": "badi",
    "چھوٹا": "chhota",
    "چھوٹی": "chhoti",
    "پہلا": "pehla",
    "پہلی": "pehli",
    "آخری": "aakhri",
    "آخر": "aakhir",
    "پورا": "poora",
    "پوری": "poori",
    "سارا": "saara",
    "سارے": "saare",
    "خاص": "khaas",
    "عام": "aam",
    "عظیم": "azeem",
    # --- deeni lafz
    "اللہ": "Allah",
    "نبی": "nabi",
    "رسول": "rasool",
    "محمد": "Muhammad",
    "اسلام": "Islam",
    "ایمان": "imaan",
    "دین": "deen",
    "دنیا": "duniya",
    "آخرت": "aakhirat",
    "دعا": "dua",
    "دعائیں": "duaayein",
    "نماز": "namaaz",
    "روزہ": "roza",
    "زکات": "zakaat",
    "حج": "hajj",
    "مال": "maal",
    "حق": "haqq",
    "خلافت": "khilafat",
    "خلیفہ": "khaleefa",
    "خلیفۃ": "khaleefat",
    "امیر": "ameer",
    "امت": "ummat",
    "مومن": "momin",
    "مومنین": "momineen",
    "مسلمان": "musalman",
    "کافر": "kaafir",
    "کافروں": "kaafiron",
    "کفار": "kuffar",
    "مشرک": "mushrik",
    "مشرکوں": "mushrikon",
    "مشرکین": "mushrikeen",
    "مسجد": "masjid",
    "مدینہ": "Madina",
    "مکہ": "Makkah",
    "قریش": "Quraish",
    "عرب": "Arab",
    "غار": "ghaar",
    "ہجرت": "hijrat",
    "مہاجر": "muhajir",
    "مہاجرین": "muhajireen",
    "انصار": "ansaar",
    "صحابہ": "sahaba",
    "صحابی": "sahabi",
    "بزرگوں": "buzurgon",
    "بزرگ": "buzurg",
    "سیرت": "seerat",
    "واقعہ": "waqia",
    "واقعے": "waqiye",
    "واقعات": "waqiaat",
    "حصہ": "hissa",
    "حصے": "hisse",
    "حدیث": "hadees",
    "کتاب": "kitaab",
    "جلد": "jild",
    "صفحہ": "safha",
    "باب": "baab",
    "سنہ": "sanah",
    "ہجری": "hijri",
    "سال": "saal",
    "برس": "baras",
    "ماہ": "maah",
    "دن": "din",
    "رات": "raat",
    "صبح": "subah",
    "شام": "shaam",
    "جمعہ": "Juma",
    "وقت": "waqt",
    "صفت": "sifat",
    "سبق": "sabaq",
    "حوالہ": "hawala",
    "لقب": "lakab",
    "نسبت": "nisbat",
    "تعارف": "taaruf",
    "پیدائش": "paidaish",
    "قبیلہ": "kabeela",
    "قبیلے": "kabeelay",
    "قبیلوں": "kabeelon",
    "بیعت": "baiyat",
    "جنگ": "jang",
    "قتل": "katal",
    "طعنے": "tane",
    "طعنہ": "tana",
    "زخم": "zakhm",
    "خون": "khoon",
    "تلوار": "talwaar",
    "کمان": "kamaan",
    "تیر": "teer",
    "نیزہ": "naiza",
    "کندھے": "kandhe",
    "حلقے": "halqe",
    "طواف": "tawaaf",
    "وادی": "waadi",
    "راستہ": "raasta",
    "راستے": "raaste",
    "یتیم": "yateem",
    "بیوہ": "bewa",
    "ماتم": "maatam",
    "عزت": "izzat",
    "فخر": "fakhr",
    "جھگڑا": "jhagda",
    "شرفاء": "shurafa",
    "تاریخ": "tareekh",
    "دیوان": "deewan",
    "قاضی": "kaazi",
    "عطا": "ata",
    "سبقت": "sabqat",
    "خدمت": "khidmat",
    "محبت": "mohabbat",
    "امتحان": "imtihaan",
    "انکار": "inkaar",
    "فرق": "fark",
    "وجوب": "wujoob",
    "سخاوت": "sakhaawat",
    "خوخہ": "khaukhah",
    "خوخے": "khaukhe",
    "گواہی": "gawaahi",
    "تواضع": "tawazu",
    "منصب": "mansab",
    "عظمت": "azmat",
    "عذر": "uzr",
    "قسم": "kasam",
    "چادر": "chaadar",
    "مصحف": "mushaf",
    "لوح": "lauh",
    "لوحوں": "lauhon",
    "جمع": "jama",
    "رحم": "rahm",
    "رحمت": "rahma",
    "حد": "had",
    "سفیر": "safeer",
    "سفارت": "sifarat",
    "عدل": "adl",
    "سخت": "sakht",
    "کمزور": "kamzor",
    "مضبوط": "mazboot",
    "طاقت": "taakat",
    "ہیبت": "haibat",
    "رعب": "rob",
    "دل": "dil",
    "زبان": "zabaan",
    "ہاتھ": "haath",
    "پاؤں": "paon",
    "سر": "sar",
    "سینہ": "seena",
    "سینے": "seene",
    "آنکھ": "aankh",
    "آنکھیں": "aankhein",
    "قدم": "kadam",
    "قدموں": "kadmon",
    "لوگ": "log",
    "لوگوں": "logon",
    "آدمی": "aadmi",
    "شخص": "shakhs",
    "مرد": "mard",
    "مردوں": "mardon",
    "عورت": "aurat",
    "عورتوں": "aurton",
    "عورتیں": "aurtein",
    "بیوی": "biwi",
    "بیٹا": "beta",
    "بیٹی": "beti",
    "بیٹے": "bete",
    "بچہ": "bachcha",
    "بچے": "bachche",
    "والد": "walid",
    "والدہ": "walida",
    "ماں": "maa",
    "باپ": "baap",
    "قوم": "kaum",
    "گھر": "ghar",
    "دروازہ": "darwaza",
    "دروازے": "darwaze",
    "کعبہ": "Kaaba",
    "قبر": "kabr",
    "جنت": "jannat",
    "دوزخ": "dozakh",
    "قیامت": "qayamat",
    "موت": "maut",
    "زندگی": "zindagi",
    "شہادت": "shahadat",
    "وفات": "wafaat",
    "وصال": "visaal",
    "دفن": "dafan",
    "تدفین": "tadfeen",
    "غسل": "ghusal",
    "جنازہ": "janaza",
    "وصیت": "wasiyat",
    "بات": "baat",
    "باتیں": "baatein",
    "جملہ": "jumla",
    "لفظ": "lafz",
    "معنی": "maani",
    "مطلب": "matlab",
    "سوال": "sawaal",
    "جواب": "jawaab",
    "دلیل": "daleel",
    "دلیلیں": "daleelein",
    "فیصلہ": "faisla",
    "فیصلے": "faisle",
    "حیرت": "hairat",
    "خوشی": "khushi",
    "ڈر": "dar",
    "محبت": "mohabbat",
    "کینہ": "keena",
    "صبر": "sabr",
    "شکر": "shukr",
    "حمد": "hamd",
    "ثبات": "sabaat",
    "قرار": "qaraar",
    "سکینہ": "sakeena",
    "ہدایت": "hidaayat",
    "توفیق": "taufeeq",
    "آمین": "Aameen",
    "سلام": "salaam",
    "خوش": "khush",
    "آمادہ": "aamada",
    "خوش آمدید": "khush aamdeed",
    # --- naam
    "صدیق": "Siddiq",
    "فاروق": "Farooq",
    "عمر": "Umar",
    "خطاب": "Khattab",
    "عثمان": "Usman",
    "عفان": "Affan",
    "علی": "Ali",
    "طالب": "Talib",
    "ابی": "Abi",
    "عبد": "Abd",
    "ابن": "bin",
    "بنت": "bint",
    "بنو": "Banu",
    "قحافہ": "Kahafa",
    "اسماء": "Asma",
    "عمیس": "Umais",
    "عائشہ": "Aisha",
    "طلحہ": "Talha",
    "صہیب": "Suhaib",
    "مغیرہ": "Mughira",
    "شعبہ": "Shuba",
    "لؤلؤہ": "Lulu",
    "عوف": "Auf",
    "مالک": "Malik",
    "مسعود": "Masood",
    "میمون": "Maimoon",
    "عمرو": "Amr",
    "حفص": "Hafs",
    "حنتمہ": "Hantama",
    "ہاشم": "Hashim",
    "مخزوم": "Makhzoom",
    "عدی": "Adi",
    "کعب": "Kaab",
    "تیم": "Taim",
    "سلمیٰ": "Salma",
    "صخر": "Sakhar",
    "عامر": "Aamir",
    "عزی": "Uzza",
    "رباح": "Rabah",
    "قرط": "Qurt",
    "رزاح": "Razah",
    "نقیل": "Naqeel",
    "ابراہیم": "Ibrahim",
    "اسحاق": "Ishaq",
    "یعقوب": "Yaqoob",
    "موسیٰ": "Moosa",
    "عیسیٰ": "Eesa",
    "بدر": "Badr",
    "احد": "Uhud",
    "خندق": "Khandaq",
    "خیبر": "Khaibar",
    "حنین": "Hunain",
    "حدیبیہ": "Hudaibiya",
    "سقیفہ": "Sakeefa",
    "ساعدہ": "Saida",
    "رضوان": "Rizwan",
    "الفیل": "Feel",
    "فجار": "Fijar",
    "اعظم": "Azam",
    "قریشی": "Quraishi",
    "عدوی": "Adawi",
    # --- hawala
    "صحيح": "Sahih",
    "بخاری": "Bukhari",
    "مسلم": "Muslim",
    "الاستيعاب": "al-Istiyaab",
    "السنن": "as-Sunan",
    "الكبير": "al-Kabeer",
    "للبيهقي": "lil-Baihaqi",
    "أسد": "Asad",
    "الغابة": "Ghaaba",
    "أسد الغابة": "Asadul Ghaabah",
    "الزکاة": "Zakaat",
    "الزكاة": "Zakaat",
    "فضائل": "Fazail",
    "الصحابة": "Sahaba",
    "الزکاة کے": "zakaat ke",
    # --- story ke aam lafz (dosra hissa)
    "ان": "in",
    "تھیں": "theen",
    "ہوں": "hon",
    "ہوتا": "hota",
    "ہوتی": "hoti",
    "ہوتے": "hote",
    "لیں": "lein",
    "دیں": "dein",
    "ہمیں": "humein",
    "تمہیں": "tumhein",
    "انہیں": "unhein",
    "اپنا": "apna",
    "اپنے": "apne",
    "اپنی": "apni",
    "انہوں": "unhon",
    "اس": "us",
    "جس": "jis",
    "جن": "jin",
    "اسے": "use",
    "کوئی": "koi",
    "آپ": "aap",
    "تمہارا": "tumhara",
    "سروں": "saron",
    "طرف": "taraf",
    "گمان": "gumaan",
    "ایسا": "aisa",
    "ایسے": "aise",
    "تیسرا": "teesra",
    "بھروسہ": "bharosa",
    "ہی": "hi",
    "کلمہ": "kalma",
    "سنبھال": "sambhaal",
    "سبسکرائب": "subscribe",
    "دشمن": "dushman",
    "دشمنی": "dushmani",
    "جاہلیت": "jahiliyat",
    "بدل": "badal",
    "غزوہ": "ghazwa",
    "شرکت": "shirkat",
    "ساتھی": "saathi",
    "پہاڑ": "pahad",
    "نبوی": "nabvi",
    "حالت": "haalat",
    "عبادت": "ibadat",
    "جان": "jaan",
    "زندہ": "zinda",
    "آیت": "aayat",
    "گزر": "guzar",
    "چکا": "chuka",
    "چکے": "chuke",
    "ذکر": "zikr",
    "واسطے": "waaste",
    "جانتے": "jaante",
    "حکم": "hukm",
    "پڑھانے": "parhane",
    "پڑھتے": "parhte",
    "پڑھی": "parhi",
    "پڑھائی": "parhayi",
    "ہاں": "haan",
    "بیشک": "beshak",
    "مقام": "maqaam",
    "ہٹانے": "hatane",
    "راضی": "raazi",
    "عرض": "arz",
    "کیونکہ": "kyunkeh",
    "قائم": "qaayam",
    "امانت": "amaanat",
    "سمجھ": "samajh",
    "خرچ": "kharch",
    "بڑھتا": "barhta",
    "بہترین": "behtareen",
    "درست": "durust",
    "دیر": "der",
    "امارت": "amaarat",
    "ناگوار": "naagawar",
    "اوڑھوں": "audhoon",
    "یکجا": "yakja",
    "بہانے": "bahaane",
    "حجرے": "hujre",
    "اترے": "utre",
    "انجام": "anjaam",
    "سلسلہ": "silsila",
    "مکمل": "mukammal",
    "بنیاد": "bunyaad",
    "کنیت": "kuniyat",
    "پیدا": "paida",
    "مخالف": "mukhaalif",
    "ظاہر": "zaahir",
    "نتیجہ": "nateeja",
    "ہمیشہ": "hamesha",
    "مطابق": "mutabik",
    "مقرر": "muqarrar",
    "رائے": "raaye",
    "قیدیوں": "qaidiyon",
    "پردے": "parde",
    "شراب": "sharaab",
    "حرمت": "hurmat",
    "پچھلی": "pichhli",
    "امتوں": "ummaton",
    "بعید": "ba-eed",
    "بولتی": "bolti",
    "صف": "saff",
    "خالی": "khaali",
    "کتراتے": "katraate",
    "للکار": "lalkaar",
    "رنگ": "rang",
    "گندمی": "gandumi",
    "داڑھی": "daadhi",
    "گھنی": "ghani",
    "بال": "baal",
    "جھڑے": "jhaday",
    "برابر": "baraabar",
    "محض": "mahaz",
    "وجہ": "wajah",
    "ورنہ": "warna",
    "شریک": "shareek",
    "بھیجنے": "bhejne",
    "ارادہ": "iraada",
    "معلوم": "maloom",
    "چھپ": "chhup",
    "سوائے": "siwaaye",
    "سیدھے": "seedhe",
    "سردار": "sardaar",
    "کمزوروں": "kamzoron",
    "خواب": "khwaab",
    "تینوں": "teenon",
    "چیزیں": "cheezein",
    "چیزوں": "cheezon",
    "بلند": "buland",
    "ملامت": "malaamat",
    "ڈرتے": "darte",
    "شہید": "shaheed",
    "مانگی": "maangi",
    "غلام": "ghulaam",
    "ناف": "naaf",
    "قاتل": "kaatil",
    "ثابت": "saabit",
    "ذی": "zil",
    "بتائی": "batayi",
    "گزری": "guzri",
    "لٹکائی": "latkayi",
    "پکڑا": "pakra",
    "کیے": "kiye",
    "کہانی": "kahani",
    "زیادہ": "zyada",
    "پہلو": "pehlu",
    "قبائل": "qabail",
    "دینے": "dene",
    "ہٹ": "hat",
    "فتح": "fatah",
    "جمادی": "Jamadi",
    "آخرہ": "Aakhirah",
    "محدث": "muhaddas",
    "اعسر": "aasar",
    "یسر": "yasar",
    "نسب": "nasab",
    "خوشخبری": "khushkhabri",
}


def _load_overrides() -> Tuple[Dict[str, str], Dict[str, str]]:
    """`content/roman.json` — user ke apne theek kiye hue lafz."""
    if not OVERRIDES_PATH.exists():
        return {}, {}
    try:
        data = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}, {}
    if not isinstance(data, dict):
        return {}, {}
    words = {
        str(key): str(value)
        for key, value in (data.get("words") or {}).items()
    }
    phrases = {
        str(key): str(value)
        for key, value in (data.get("phrases") or {}).items()
    }
    return words, phrases


_OVERRIDE_WORDS, _OVERRIDE_PHRASES = _load_overrides()

WORDS: Dict[str, str] = {**_WORDS_BUILTIN, **_OVERRIDE_WORDS}
PHRASES: Dict[str, str] = {**_PHRASES_BUILTIN, **_OVERRIDE_PHRASES}

# Lambe juz pehle, warna "رضی اللہ عنہ" chhoti entry se toot jayega.
_PHRASES_SORTED = sorted(
    PHRASES.items(), key=lambda item: len(item[0]), reverse=True
)


def _strip_marks(word: str) -> str:
    return "".join(char for char in word if char not in _MARKS)


def _translit_word(word: str) -> str:
    """Harf-ba-harf: Urdu harf → Latin harf.

    Urdu chhoti (short) awaazein likhi hi nahi jatin, is liye do harf
    aage-peeche aane par beech me halka "a" daal dete hain — warna Hindi
    awaaz "ghr" jaisa lafz bolne se ruk jati hai.
    """
    out: list = []
    prev_cons = False
    index = 0
    length = len(word)

    while index < length:
        char = word[index]
        if char in _MARKS:
            index += 1
            continue

        following = word[index + 1] if index + 1 < length else ""

        if following == "ھ" and char in _ASPIRATED:
            piece = _ASPIRATED[char]
            index += 2
        elif char in _LETTERS:
            piece = _LETTERS[char]
            index += 1
        else:
            out.append(char)
            prev_cons = False
            index += 1
            continue

        if not piece:
            continue

        if prev_cons and piece[0] in _CONSONANTS:
            out.append("a")

        out.append(piece)
        prev_cons = piece[-1] in _CONSONANTS

    return "".join(out)


def _split_edges(token: str) -> Tuple[str, str, str]:
    """Aage/peeche ki punctuation alag, beech ka Urdu hissa alag."""
    start = 0
    while start < len(token) and not URDU_RE.match(token[start]):
        start += 1
    end = len(token)
    while end > start and not URDU_RE.match(token[end - 1]):
        end -= 1
    return token[:start], token[start:end], token[end:]


def _convert_token(token: str) -> str:
    head, core, tail = _split_edges(token)
    if not core:
        return token
    key = _strip_marks(core)
    roman = WORDS.get(core) or WORDS.get(key)
    if roman is None:
        roman = _translit_word(key)
    return f"{head}{roman}{tail}"


def to_roman(text: str) -> str:
    """Urdu/Arabic text ko Roman (Latin) me badal deta hai.

    Jo pehle se Latin hai (jaise "Like • Share") waisa hi rehta hai.
    """
    if not text:
        return ""

    text = text.translate(_DIGITS).translate(_PUNCT)
    text = text.replace("ﷺ", "صلی اللہ علیہ وسلم")
    text = text.replace("«", "").replace("»", "")

    for urdu, roman in _PHRASES_SORTED:
        if urdu in text:
            text = text.replace(urdu, roman)

    return " ".join(_convert_token(token) for token in text.split(" "))
