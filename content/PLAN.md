# Plan — ek sahabi, ek silsila

Filhaal repo me **Abu Bakr Siddiq رضی اللہ عنہ ka poora silsila (8 hisse)**
hai, tarteeb se — har hissa ek waqiya aur ek hawala.

## Har video ka dhancha (jahan maujood ho)

1. **تعارف** — poora naam aur nasab
2. **پیدائش** — kab aur kahan paida hue
3. **رسول ﷺ سے نسبت** — Nabi ﷺ se kya rishta
4. **اہم واقعہ** — ek bara waqiya, Arabic matn ke saath
5. **ایک صفت** — un ki ek khaas sift
6. **وفات** — kab aur kahan wafat hue
7. **بڑے کام** — un ki ek bari khidmat

Ek video me 3–4 beats rehte hain (1 minute ki hadd), is liye ek sahabi
ka silsila chand hisson me chalta hai. Har hisse ka apna **ek hawala**
hota hai — video me hamesha nazar aata hai, aur agle hisse ki targheeb
(aakhri line) bhi usi hisse me di jati hai.

## Abu Bakr Siddiq رضی اللہ عنہ — 8 hisse (tarteeb)

| # | Hissa | Asal matn | Hawala |
|---|---|---|---|
| 1 | غار میں — دو کے ساتھ اللہ تیسرا | «ما ظنك باثنين الله ثالثهما» | صحيح مسلم — حدیث 2381، ج 4 ص 1854 |
| 2 | وصال کا دن — «من كان يعبد محمدا» | «فمن كان يعبد محمدا فإن محمدا قد مات...» | السنن الكبير للبيهقي — ج 16 ص 510 |
| 3 | سقیفہ بنو ساعدہ کا فیصلہ | «أنشدكم الله، هل تعلمون أن رسول الله ﷺ أمر أبا بكر أن يصلي بالناس؟» | الاستيعاب — ج 3 ص 970 |
| 4 | نماز اور زکات میں فرق نہیں | «لأقاتلن من فرق بين الصلاة والزكاة، فإن الزكاة حق المال» | صحيح البخاري — حدیث 1399 |
| 5 | سخاوت اور مسجد کا خوخہ | «لا تُبقين في المسجد خوخة إلا خوخة أبي بكر» | صحيح مسلم — حدیث 2382، ج 4 ص 1854 |
| 6 | «خليفة رسول الله» — اور امت کی گواہی | «لست بخليفة الله ... ولكني أنا خليفة رسول الله» | الاستيعاب — ج 3 ص 972 |
| 7 | عام بیعت، اور علی رضی اللہ عنہ کا عذر | «إني آليت ألا أرتدى ردائي إلا إلى صلاة حتى أجمع القرآن» (علی رضی اللہ عنہ) | الاستيعاب — ج 3 ص 972، 974 |
| 8 | وفات، وصیت اور تدفین | «وأوصى أن تغسله أسماء بنت عميس زوجته...» | الاستيعاب — ج 3 ص 977 |

Har hisse ka matn **Shamela se parh kar** likha gaya hai; jo pada nahi gaya wo
likha nahi gaya. Agla silsila: Umar bin Khattab رضی اللہ عنہ (5 hisse).

## Uske baad (isi tarteeb se)

Ashab-e-Ashara ke baaki nau, phir dusre sahaba:

1. عمر بن خطاب رضی اللہ عنہ (5 hisse)
2. عثمان بن عفان رضی اللہ عنہ (5 hisse)
3. علی بن ابی طالب رضی اللہ عنہ (5 hisse)
4. طلحہ بن عبید اللہ رضی اللہ عنہ
5. زبیر بن العوام رضی اللہ عنہ
6. عبد الرحمن بن عوف رضی اللہ عنہ
7. سعد بن ابی وقاص رضی اللہ عنہ
8. سعید بن زید رضی اللہ عنہ
9. عبد اللہ بن مسعود رضی اللہ عنہ

**Note:** «عشرة مبشرة بالجنة» ki list الاستيعاب (ج 3 ص 988) me yehi hai —
daswe naam **عبد اللہ بن مسعود** ہیں، ابو عبیدہ بن الجراح nahi (un ka
zikr fazail me bara hai, magar is fehrist me nahi).

## Kitabein (sirf yahi)

- **Sahih al-Bukhari** aur **Sahih Muslim**: waqiya ka asal matn aur hadees number.
- **Siyar A'lam al-Nubala**, **Al-Isabah**, **Al-Isti'ab**, **Al-Sunan al-Kabir
  lil-Bayhaqi**: nasab, paidaish, wafat, sifaat aur tarajim ki tafseel.
- Hadees ki **grading apne tor par nahi** — jo kitab me likhi hai wahi jayegi.
- Jo baat kisi kitab me na mile, wo **likhi hi nahi jayegi** (andaza nahi).

## Kaam ka tareeqa

1. Us sahabi ka baab Shamela se parhna (Sahihain + tarajim).
2. `content/stories.json` me story jodna — har beat par `label`
   (تعارف، پیدائش، اہم واقعہ...).
3. Hawala screen par rehta hai: kitab + hadees number + jild/safha.

Story ka format:

```json
{
  "id": "abu-bakr-ghar",
  "title": "ابو بکر صدیق",
  "subtitle": "حصہ ۱ — غار میں، دو کے ساتھ اللہ تیسرا",
  "hook": "...",
  "beats": [
    { "label": "تعارف", "urdu": "...", "arabic": "..." },
    { "label": "اہم واقعہ", "urdu": "...", "arabic": "..." }
  ],
  "lesson": "...",
  "next_hint": "اگلے حصے میں: ... — سبسکرائب کر لیں۔",
  "source": { "book": "«صحيح مسلم»", "ref": "حدیث 2381، ج 4 ص 1854" }
}
```
