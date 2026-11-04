# Nayi story jodne ka tareeqa

Har story aisi honi chahiye jiska **hawala aap khud dekh sakein**. Neeche wahi
tareeqa hai jo is repo ki 6 stories ke liye istemal hua.

## 1. Kitab aur baab dhoondiye

Shamela me (ya jis tool se aap research karte hain) pehle kitab ka id nikalye,
phir us baab ka jo us sahabi ke baare me hai:

- `shamela_resolve` — kitab ka id (misal: «صحيح مسلم» = 1727، «صحيح البخاري» = 1681)
- `shamela_search_titles` — baab ka title_id (misal: «باب من فضائل جليبيب»)

## 2. Poora matn padhiye

- `shamela_get_book_section(book_id, title_id)` se baab ka matn padhiye.
- `shamela_get_page(book_id, page_id)` se us safhe ka poora matn.

**Sirf wahi likhiye jo aap ne padha hai.** Agar matn me lafz "جلبيب" hai to wahi
rakhiye, apni taraf se badal kar "جليبيب" na kijiye — ya dono jaga ek jaisa rakhiye.

## 3. Hawala banaiye

- `shamela_get_citation(book_id, page_id)` — kitab ka naam aur jild/safha deta hai.
- Hadees ka number matn ke saath hi likha hota hai (misal: `٢٤٧٢`), use bhi shamil kijiye.

Hawala aisa likhiye:

```
"ref": "حدیث ۲۴۷۲، ج ۴ ص ۱۹۱۸"
```

Agar jild ya safha maloom na ho to **sirf wahi likhiye jo maloom hai** — andaza
lagaya hua number kabhi na likhiye.

## 4. Story ko JSON me daaliye

`content/stories.json` ke `stories` array me ek naya object:

```json
{
  "id": "unique-short-id",
  "title": "نام — رضی اللہ عنہ",
  "subtitle": "ایک جملہ",
  "hook": "شروع کرنے والا جملہ (اپنے الفاظ)",
  "beats": [
    { "urdu": "اپنے الفاظ میں ایک بات", "arabic": "عین حدیث کا ٹکڑا" }
  ],
  "lesson": "ایک مختصر سبق",
  "source": {
    "book": "«صحيح مسلم»",
    "author": "مسلم بن الحجاج",
    "ref": "حدیث ٢٤٧٢، ج ٤ ص ١٩١٨",
    "note": "باب من فضائل جليبيب"
  }
}
```

Niyam:

- `beats` me `urdu` lazmi hai; `arabic` jahan asal lafz maujood hain wahan dijiye.
- Ek beat 2–4 line se lamba na ho — lambi kahani ko 4–6 beats me todiye.
- `lesson` ek nateeja hai, sharah nahi. Kisi aalim ka qaul likh rahe hain to uska
  naam bhi dijiye.
- `id` unique ho (chhote English letters, jaise `julaybib`).

## 5. Test kijiye

```bash
DRY_RUN=yes python -m video_factory.main
```

`out/video.mp4` dekh lijiye — text screen par theek aa raha hai, hawala poora hai.

## Kya na kijiye

- Internet ki kisi anonymous site se "story" utha kar hawala apne se mat jodiye.
- Hadees ki sanad par apne tor par "صحیح/ضعیف" mat likhiye — jo kitab me hai wahi.
- Jis waqiya me ikhtilaf ho, use chhod dijiye — 60 second ki video me wo samjhaya
  nahi ja sakta.
