# turkce-vurgu

Türkçe metni, ses sentezi (TTS) modellerinin girdisi olan **vurgu işaretli IPA okunuşa**
çevirir. espeak gerektirmez, bağımlılığı yoktur.

```python
from turkce_vurgu import g2p

g2p("Ankara'ya gitmedik ama yarın gideceğiz, değil mi?", vurgu=True)
# 'ˈankaɾaja ˈɟitmedic ˈama ˈjaɾɯn ɟidedʒeˈiz, deˈil mi?'
```

```
python -m turkce_vurgu "Sapanca gölünün kıyısında yürürken İstanbul'u düşündüm."
saˈpandʒa ɟølyˈnyn kɯjɯsɯnˈda jyˈɾyɾcen isˈtanbuɫu dyʃynˈdym.
```

## Neden

Açık kaynak Türkçe ses modelleri okunuşu çoğunlukla espeak ile çıkarır. espeak'in
Türkçesinde vurgu çoğu zaman yanlıştır (ˈAnkara yerine Anˈkara, geˈliyor yerine
geliˈyor), k/g/l incelmesi eksiktir. Lisansı da GPL olduğu için ticari ürüne girmesi
zordur. Bu paket MIT lisanslıdır ve Türkçe kurallarla çalışır.

## Ne yapar

**Okunuş (G2P)**
- k, g, l ön ünlüyle incelir: `kâr → caːɾ`, `göl → ɟøl`, `ilk → ilc`.
- Uzun ünlüler korunur (â, î, û). ğ önceki ünlüyü uzatır ya da düşer: `dağ → daː`, `ağaç → aatʃ`.
- Sayılar, yüzdeler, ondalıklar ve sık kısaltmalar sözcüğe açılır:
  `%12,5 → yüzde on iki virgül beş`, `1.250 km → bin iki yüz elli kilometre`.
- Yazımda görünmeyen uzun ünlüler ve kural dışı ince l/k/g için okunuş sözlüğü (1.488 sözcük,
  Vikisözlük): `nadir → naːdiɾ`, `malum → maːlum`, `metal → metal` (ince l), `kilometre → cilometɾe`.
  Ekli biçimlerde kök sözlükten, ekler kurallarla okunur.
- Noktalama korunur; modeller duraklama ve tonlamayı noktalamadan öğrenir.

**Sözcük vurgusu** (`vurgu=True`): vurgulu hecenin önüne `ˈ` konur. Kurallar Türkçe vurgu
literatüründen alınmıştır (kaynaklar aşağıda). Yöntem Oflazer & Inkelas'ınkiyle aynıdır:
sözcükteki bütün vurgu adayları toplanır, **en soldaki kazanır**, aday yoksa son hece vurgulanır.

| Aday | Örnek | Kaynak |
|---|---|---|
| Varsayılan: son hece; ekler eklendikçe vurgu sona kayar | kitapˈlar, kitaplarˈdan, bırakaˈcak | I&O 140 |
| Sözlüksel vurgulu kök; ek alsa da vurgu kökte kalır | loˈkantaya, tarˈhanada, ˈşimdi, ˈorada | G&K 27–29, Ink ex.64 |
| Vurgu almayan ekler: vurgu ekten önceki hecede (olumsuzluk -mA-, ek-eylem -(y)DI / -(y)mIş / -(y)sA / -(y)Im, -DIr, -(y)ken, -(y)lA, -CA, -leyin, -CAsInA, emir -(y)In) | ˈgitmedik, oˈkumayacak, okulˈdaymışlar, öğrenˈciyim, kiraˈlıktır, araˈbayla, güˈzelce, ˈtürkçe | I&O 141, Ink ex.61–62, G&K 32–34 |
| Vurgu çeken ekler: vurgu ekin ilk hecesinde (-Iyor, -ArAk, -IncE, -(y)Iver, -(y)Akal, -mAksIzIn) | geˈliyor, yaˈparak, geˈlince, tuˈtuver, bakˈmaksızın | Ink ex.54, 61; G&K |
| Olumsuz geniş zaman vurgulanır | gelˈmez, bakˈmazdık, yazˈmayız | G&K |
| Yer adları ve yabancı adlar: Sezer kuralı (Türkçe kişi adları hariç; -istan, -hane hariç) | ˈAnkara'ya, İsˈtanbul'u, Saˈpanca, hindisˈtan, Ahmeˈt'e | Sezer 1981, I&O 143–150 |
| Vurgusuz sözcükler | soru eki mi (misin, midir…), de/da, ki, ya, bile, ise, ile | G&K |

Özel adlar büyük harf ve kesme işaretinden tanınır (`Serdivan'daki`, cümle ortasında
`Zeynep`). Türkiye illeri ve bazı ilçeler cümle başında da tanınır.

Yazımdan çözülemeyen ikiliklerde vurgulanabilir okuma (son hece) seçilir. Örnekler:
- GİTme ("gitme!") / gitME ("gitmek");
- -(y)Im ek-eylemi / iyelik;
- yüklem -lAr / çoğul -lAr.

## Doğruluk

**Literatürdeki örnekler** (`tests/literatur.tsv`). Kaynaklarda vurgusu verilmiş 123 sözcük ve
çekimli biçim; her satırda kaynağı yazar:

| Grup | Doğru |
|---|---|
| Ek ve kök kuralları (çekimli biçimler) | 90 / 90 |
| Sezer kuralı (yer adları, yabancı adlar) | 30 / 33 |
| **Toplam** | **120 / 123 (%97,6)** |

Sezer grubundaki 3 hata (santaMOnika, monTAna, papaDOpulos) Sezer kuralının kaynaktaki
tanımıyla da çelişiyor; Inkelas bu adları kural dışı örnek olarak veriyor. Kaynaklar arasında
çelişen 2 örnek ve bağlam gerektiren 6 örnek ölçüye katılmadı.

**Vikisözlük** (`degerlendirme/vikisozluk.py`, 9.030 sözcük, 5 katlı çapraz doğrulama).
Vikisözlük'ün okunuş şablonu vurgu belirtilmezse son heceyi kendiliğinden işaretler. Bu
yüzden yalnız son hece dışındaki işaretler güvenilir altın veridir.
- **Son hecesi vurgulu sıradan sözcüklerde** (adlar, sıfatlar, eylemler) kurallar
  %98,6–98,9 oranında aynı yeri bulur.
- **Son hece dışı vurgulu sözcükler** (1.234 sözcük, çoğu yabancı kökenli): sözlüğe
  girmemiş bir sözcüğün vurgusunu kurallar ancak özel adlarda tahmin edebilir (%62). Bu
  vurgu tanım gereği sözlükseldir. Bilinenler `turkce_vurgu/veri/istisna.tsv`
  sözlüğündedir (1.203 sözcük).

Karşılaştırma için: espeak-ng'nin Türkçe vurgusu Vikisözlük'le yalnız %55 oranında aynı
hecede buluşur ([Ghostwriter-Dict](https://github.com/Prosincerity/Ghostwriter-Dict) ölçümü).

## Kaynaklar

- **I&O:** S. Inkelas & C. O. Orgun (2003). Turkish stress: a review. *Phonology* 20:139–161.
- **Ink:** S. Inkelas (1999). Exceptional stress-attracting suffixes in Turkish: representations
  versus the grammar. *The Prosody-Morphology Interface*, 134–187.
- **G&K:** A. Göksel & C. Kerslake (2005). *Turkish: A Comprehensive Grammar*, s. 26–34.
- **Sezer:** E. Sezer (1981). On non-final stress in Turkish. *Journal of Turkish Studies* 5:61–69.
- **O&I:** K. Oflazer & S. Inkelas. A finite state pronunciation lexicon for Turkish.
- B. Kabak & I. Vogel (2001). The phonological word and stress assignment in Turkish. *Phonology* 18.
- J. Woodard (2015). Stress rules for Turkish language learners. *GIALens* 9(1).
- H. Yawney (2018). *Toronto Working Papers in Linguistics* 40.
- Vikisözlük (Wiktionary) Türkçe maddeleri, [kaikki.org](https://kaikki.org/dictionary/Turkish/)
  dökümü (wiktextract), CC BY-SA 4.0.

**Semboller**: Çıktı yalnız StyleTTS2'nin (ve Kokoro'nun) 178 sembollük listesindeki
sembolleri kullanır. Bu modellerin önceden eğitilmiş metin gömmeleri doğrudan kullanılabilir.

## Bilinen sınırlar

- Kurallar sözcük düzeyindedir. Cümle vurgusu (odak) ses modelinin işidir.
- Tam bir biçimbilim çözümleyicisi yoktur. Ekler sözcük sonundaki kalıplardan tanınır; bir
  ekin gerçekten ek olduğu Vikisözlük kök ve eylem listeleriyle sınanır (güzel+ce ✓,
  düşün+ce ✗). Belirsiz durumlarda son hece kullanılır.
- Sözlükte olmayan yabancı kökenli sözcüklerin vurgusu tahmin edilemez (son hece varsayılır).
  Kaynaklı eklemeler `turkce_vurgu/vurgu.py` içindeki `LITERATUR` listesine yapılır.

## İlgili projeler

- **[turkce-plbert](../turkce-plbert):** bu paketin vurgulu okunuşuyla eğitilmiş Türkçe PL-BERT.
  StyleTTS2/Kokoro gibi modellerde tonlamayı besler.

## Test

```
python -m unittest discover -s tests
```

## English summary

Rule-based Turkish grapheme-to-phoneme conversion with **lexical stress marking**
(IPA `ˈ`), for TTS front-ends. It has no dependencies, is espeak-free and MIT-licensed.
It handles palatal k/g/l, long vowels, soft-g, and number and abbreviation expansion. Stress
assignment follows the linguistic literature (Inkelas & Orgun 2003; Inkelas 1999; Göksel &
Kerslake 2005; Sezer 1981) using the Oflazer & Inkelas leftmost-wins algorithm. It combines
lexically stressed roots (1,203 entries from Wiktionary, CC BY-SA), pre-stressing and
stress-attracting suffixes, and Sezer stress for place and foreign names.
- On 123 stress examples cited in the literature, 120 are correct (97.6%).
- On final-stressed common words from Wiktionary, the rules agree 98.6–98.9% of the time.
- For comparison, espeak-ng agrees with Wiktionary on the stressed syllable in only 55% of words.

The output uses only StyleTTS2/Kokoro symbols. A Turkish PL-BERT trained on this G2P lives
in the sister project `turkce-plbert`.

## Lisans

Kod MIT, bkz. [LICENSE](LICENSE). `turkce_vurgu/veri/` altındaki sözlük dosyaları
Vikisözlük'ten türetildiği için **CC BY-SA 4.0**'tır (`degerlendirme/sozluk_uret.py` üretir).
