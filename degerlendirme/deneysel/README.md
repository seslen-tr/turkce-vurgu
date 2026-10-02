# Deneysel: Zemberek motoru (02.10.2026)

`zemberek_motoru.py` vurgu kurallarını kalıplar yerine Zemberek'in biçimbirim çözümlemesine
uygular. Kurallar ve en-soldaki-kazanır algoritması `turkce_vurgu/vurgu.py` ile aynıdır.
Literatür sınavında (`tests/literatur.tsv`) **kalıp motorundan kötü** çıktığı için pakete
alınmadı:

| | ek/kök kuralları | Sezer |
|---|---|---|
| kalıp motoru (varsayılan) | 90 / 90 | 30 / 33 |
| Zemberek motoru | 83 / 90 | 21 / 33 |

Başlıca nedenler:
- Türemiş yer adlarını (Torbalı, Sirkeci, Kavaklı, Boyacı) cins ad türetmesi olarak çözümlüyor
  (torba+lı). Literatüre göre bunlar yer adı olarak Sezer vurgusu alır (Ink ex.11).
- Ek-eylemli biçimlerde (gelseymiş, geldilerse) bağlam ayrımcısı yanlış çözümlemeyi seçiyor.
- Bağlam ayrımcısı olumsuz emir ile adı da ayıramadı ("Kitabı okuma, önce gitme dedim"
  cümlesinde ikisini de ad seçti).

Hız: sözcük başına ~25 ms (bağlamlı), ilk yükleme ~3,5 sn.

İleride denenebilir: büyük harf ve kesme işaretini Prop ipucu olarak vermek; yalnız kalıp
motorunun belirsiz kaldığı sözcüklerde Zemberek'e danışmak.
