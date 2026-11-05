# Ashara Mubashara — 10 din ka plan

Wo das sahaba jin ke baare me hadees me jannat ki khushkhabri aayi
("عشرة مبشرة بالجنة"). Har din **ek sahabi**, ek video (~1 minute).

## Har video ka dhancha (har sahabi ke liye wahi)

1. **تعارف** — poora naam aur nasab (kis ke bete, kis qabeela se)
2. **پیدائش** — kab aur kahan paida hue (jahan riwayat me ho)
3. **رسول ﷺ سے نسبت** — Islam kab qubool kiya, Nabi ﷺ se kya rishta
4. **اہم واقعہ** — ek bara waqiya, Arabic matn ke saath
5. **ایک صفت** — un ki ek khaas sift (jaise sachai, sakhawat, amanat)
6. **وفات** — kab aur kahan wafat hue
7. **بڑے کام** — un ki ek bari khidmat

## Kitabein (sirf yahi)

- **Sahih al-Bukhari** (صحيح البخاري — ط السلطانية) aur **Sahih Muslim**
  (صحيح مسلم — ت عبد الباقي): waqiya ka asal matn aur hadees number.
- **Siyar A'lam al-Nubala**, **Al-Isabah**, **Al-Isti'ab**: nasab, paidaish,
  wafat aur sifaat ki tafseel.
- Hadees ki **grading apne tor par nahi** — jo kitab me likhi hai wahi jayegi.
- Jo baat kisi kitab me na mile, wo **likhi hi nahi jayegi** (andaza nahi).

## Din ke hisaab se

1. ابو بکر صدیق رضی اللہ عنہ
2. عمر بن خطاب رضی اللہ عنہ
3. عثمان بن عفان رضی اللہ عنہ
4. علی بن ابی طالب رضی اللہ عنہ
5. طلحہ بن عبید اللہ رضی اللہ عنہ
6. زبیر بن العوام رضی اللہ عنہ
7. سعد بن ابی وقاص رضی اللہ عنہ
8. سعید بن زید رضی اللہ عنہ
9. عبد الرحمن بن عوف رضی اللہ عنہ
10. ابو عبیدہ بن الجراح رضی اللہ عنہ

## Kaam ka tareeqa

1. Us sahabi ka baab Shamela se parhna (Sahihain + tarajim).
2. `content/stories.json` me story jodna — har beat par `label`
   (تعارف، پیدائش، اہم واقعہ...).
3. Hawala screen par rehta hai: kitab + hadees number + jild/safha.

Story ka format:

```json
{
  "id": "abu-bakr",
  "title": "ابو بکر صدیق رضی اللہ عنہ",
  "hook": "...",
  "beats": [
    { "label": "تعارف", "urdu": "...", "arabic": "..." },
    { "label": "پیدائش", "urdu": "..." },
    { "label": "اہم واقعہ", "urdu": "...", "arabic": "..." }
  ],
  "lesson": "...",
  "source": { "book": "«صحيح مسلم»", "ref": "حدیث ۲۳۸۳، ج ۴ ص ۱۸۵۴" }
}
```

## Status

- Dhancha tayyar hai: labels, hawala, ~1 minute video, ek din ek sahabi.
- Har sahabi ka matn **ek ek kar ke** Shamela se parh kar likha jayega —
  dekhe baghair kuch nahi likha jata.
