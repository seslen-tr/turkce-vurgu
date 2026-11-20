# Değişiklikler

## 0.1.8 — TDK taramasının tamamı, şapkalı yazım

- 0.1.7'de TDK sözlüğü sorgulara yanıt vermez olunca kalan kayıtlar da soruldu: türev sözcüklerin kökleri (162 kök)
  ve uzun ünlüsü olmayan 524 kayıt. Ekte uzayan kök 51 → 117: "ihtimali" → "ihtimaːli", "iptali", "kabulü",
  "evladım" (TDK evla:dı), "selamı", "telaşı", "ahlakı", "istiklali", "imkânı", "zekâtı", "harekâtı". Yalın
  biçimde uzun: "kâhin" → "caːhin", "lades" → "laːdes", "hâk", "nakdî", "rahîm", "muhafazakâr" (muha:fazakâr);
  ince l: "klimatoloji", "kolonyal", "teşkilat". Kök sorgusundan: "tesisatçı", "vasi", "tabiiyet".
- Şapkalı yazım, şapkasız biçimi okunuş sözlüğündeyse sözlüğe uyar (önceden yalnız kuralla okunuyordu):
  "istiklâl" → "isticlal" (önceden "isticlaːɫ": sondaki l kalın, a uzun; TDK istiklal, l ince), "ilân" → "iːlan",
  "hâle" → "haːle". Şapka ekteyse ya da şapkasız biçim sözlükte yoksa kural okur: "hâlâ", "kâr" değişmez.
  Ekte uzayan kök şapkalı da şapkasız da yazılsa uzar: "zekâtı" = "zekatı" → "zecaːtɯ".
- ğ'den önceki ünlüye TDK'da olmayan uzunluk eklenmez: "mübalağa" Vikisözlük okunuşuna döndü ("mybaːlaa").

## 0.1.7 — TDK telaffuzu, ekte uzama

- Okunuş sözlüğü (Vikisözlük) TDK Güncel Türkçe Sözlük'ün telaffuz bilgisiyle karşılaştırıldı: uzun ünlülü 964
  kayıttan 650'si uyumluydu; TDK'nın açıkça verdiği yerlerde 57 kayıt düzeltildi (yalnız uzunluk ve ince l/k/g;
  öteki sesler aynı). Vikisözlük'te vurgulu hece uzun sanılmıştı: "acemice" → "adʒemidʒe" (önceden
  "adʒemiːdʒe"; TDK "acemi'ce"), "palyaço", "aterina" (yalnız vurgu veren telaffuzda yalnız vurgulu hecenin
  uzunluğu silinir: "memnuniyetle"de kökün uzunluğu, memnu:niyet, kalır); kalın okunan ince l:
  "eflatun" → "eflaːtun", "latife", "gilaburu"; sondaki uzun î: "hayalî", "hakiki", "tedavi", "telafi",
  "istisnai", "şeytanî"; TDK'ya göre yazıldığı gibi okunanlar: "lider", "şut", "niçin", "ezan", "yahni". ğ
  uzatması (değer → deːeɾ) ve ünlü-ünlü arasındaki uzunluk korunur: "cezaevi"nde TDK yalnız vurgu veriyor ama ː
  silinince model iki ünlüyü kaynaştırıyordu ("cezavi"). Düzeltmeler `degerlendirme/tdk_okunus.tsv`'de;
  `sozluk_uret.py` Vikisözlük okunuşunun üstüne yazar.
- Ünlüyle başlayan ekte kökün son ünlüsü uzar (TDK: icat "i:cat", icadı "i:ca:dı"): "icadı" → "iːdʒaːdɯ"
  (önceden "iːdʒadɯ"), "ilanı", "padişahı", "merakı", "mirası", "itibarı", "azabı"; 51 kök (`veri/ek_uzun.tsv`).
  Ünsüzle başlayan ekte kısa kalır ("ilanlar"). Yalın biçimde TDK'nın kısa verdiği son ünlü kısaldı: "merak" →
  "meɾak", "azap", "hicap".

## 0.1.6 — şapkasız alıntı, ince l

- Şapkasız yazılan alıntı sözcük şapkalı gibi okunur: "hikaye" → "hicaːje" (önceden "hikaje"), "dükkan" →
  "dyccan", "rüzgar" → "ɾyzɟaɾ", "mekan", "imkan", "tezgah", "yadigar", "zekat", "katip", "hükumet", "mahkum";
  ekli biçimler de ("hikayede", "dükkanı"). Kaynak: sözlükte k/g/l'den sonra â ya da û olan kökler (Vikisözlük);
  şapkalı yazımın Vikisözlük okunuşu kullanılır, yoksa kural. Birkaç uzun ünlülü sözcük de: "dahil" → "daːhil",
  "halen", "derhal", "adeta". Eşsesliler bağlamsız ayırt edilemez, yazıldığı gibi kalır: kar / kâr, hala / hâlâ,
  kanun / kânun, ala / âlâ, hal / hâl, adet / âdet. Şapkasız yazımın kendi Vikisözlük kaydı varsa o geçer (`sapka.py`).
- Ek ünlüsü ince alıntılarda l incedir: "gol" → "ɡol" (önceden "ɡoɫ"; "golü"), "petrol", "kalp", "futbol",
  "voleybol", "usul", "ihmal", "helal"; Batı alıntılarında şapka yalnız l'yi inceltir, ünlü kısadır: "plan" →
  "plan" (önceden "pɫan"), "plaj", "plak", "parlamento".
- Yumuşayan kök, sözlükte daha uzun kök varsa aranmaz: "kalbur" "kalp" + ek sanılmaz.
- Vikisözlük okunuş sınavında 13 sözcükte bilerek ayrılır (PER %2,94 → %2,95): Vikisözlük "gol", "futbol",
  "ihmal", "voleybol", "iştigal" için kalın l, "dahil", "aciz" için kısa ünlü, "bekar" için kalın k yazar; TDK'de
  ekleri ince ("golü", "ihmali"), yazımı "dâhil", "âciz", "bekâr". Literatür ve Vikisözlük vurgu sınavı değişmedi.

## 0.1.5 — büyük harfli sıradan sözcük

- Büyük harfle yazılan sıradan sözcük özel ad vurgusu (Sezer) almaz: "Bugün Pazar" → "paˈzar" (önceden "ˈpazar"),
  "Büyük Millet Meclisi" → "milˈlet medʒliˈsi", "Dünya Sağlık Örgütü'nde" → "saːˈɫɯk øɾɟytynˈde", başlık ve
  etiketlerde "Madde", "Komut", "Yorum", "Abone". Kökü yalnız sözlükte olan ya da hem sözlükte hem özel ad
  listesinde olup il / kişi adı olmayan sözcük kesmesizse sıradandır; kesmeli yazım özel ad kalır ("Mısır'a"); gün ve
  ay adı hep sıradandır (`GUN_AY`). Altı makalenin 3122 sözcüğünde 82 sözcüğün vurgusu düzeldi.
- Cümle başındaki özel ad, sözlükte sıradan karşılığı yoksa özel ad sayılır: "Rusya ile" → "ˈrusja" (önceden
  "rusˈja"), "Japonya", "Roma".
- Sıradan sözcük de olan il adı (ordu, aydın, ağrı, tokat) yalnız büyük harf ya da kesmeyle il adıdır: "ordusu" →
  "orduˈsu" (önceden "ˈordusu").

## 0.1.4 — ek zinciri

- Sözlük kökünden sonrası baştan sona ad ya da eylem eki olmalı (önceden yalnız başına bakılıyordu, kökten sonra ne
  gelirse "ek" sayılıyordu): "Hatay'da" → "ˈhatajda" (önceden "hata"+"yda": "hataːjda"), "kilisede" → "ciˈlisede"
  ("kilis"+"ede": "ˈcilisede"), "Galatasaray" ("gala"+"tasaray": "ˈɡalatasaray"), "Adapazarı", "Cezayir", "gazino",
  "animasyon" sahte uzun ünlüsüz. Sözlükte daha uzun bir kök varsa ("kilise", "selanik") kısa kök uygulanmaz.
- Vikisözlük okunuş sınavı PER %3,04 → %2,94; literatür vurgusu aynı (kural 90/90, Sezer 30/33).
- Yeni: `vurgu._ek_zinciri(kalan)`.

## 0.1.3 — turkce-normalize tabanı

- `[tam]` turkce-normalize ≥ 0.1.7 ister. Önceki taban (0.1.4) yükseltmede eski sürümü bırakıyordu (`pip install -U`
  kurulu bağımlılığı gerekmedikçe yükseltmez), o sürümden sonraki düzeltmeler gelmiyordu: bitişik kısaltma
  ("TBMM" → "tebememe"), alan adı ("github.com" → "githab nokta kom"), "saat"siz noktalı saat ("06.45'te"), baştaki
  sıfır ("TR-042"), "dört" yumuşaması ("4'e" → "dörde"), ekli Roma rakamı ("Bölüm III'te").
- CITATION.cff sürümü güncellendi (0.1.1'de kalmıştı).

## 0.1.2 — tire ve biçim işaretleri

- `normallestir`: yalnız boşluklu tire ve uzun çizgi duraklama (virgül) olur; sözcük içi tire boşluk ("ar-ge" →
  "ar ge"; önceden "ar, ge" diye duraklayarak okunuyordu).
- Biçim işaretleri (`# * _ < > | ~ ^ ` / …`) ve HTML yorumu, etiketi okunuşa girmez: modele giderse anlamsız ses
  çıkıyordu ("<!--"). Madde ayırıcı nokta (·, •) duraklama olur.
- Türkçede olmayan harf (sözlükte olmayan yabancı sözcük) en yakın Türkçe sese çevrilir: x → ks, w → v, q → k
  ("LibriVox" → "librivoks").

## 0.1.1

- var/yok + ek-eylem kökten vurgulanır: VARmış, YOKmuş, VARdır, YOKtu, YOKsa.
- Ad + ek-eylem -mIş vurgu almaz: güZELmiş, çoCUKmuş (eylemden sonra zaman eki olarak kalır: gelMİŞ).
- Cümle ya da yan cümle sonundaki yalın eylem+mA olumsuz emir okunur: acele ETme., KORKma! (yerleşik adlar hariç: dondurMA).
- "harika" ilk heceden: HArika.
- Yeterlik -(y)Abil ve -(y)AmA: -(y)A hecesi (oLAbilirim, alıNAmaz; G&K 30). Ünlü gövde + geniş zaman -r + -sIn/-DI/-sA/-ken: isTERsin. "peki" ilk heceden (PEki).
- Okunuş sözlüğündeki kök ünlüyle başlayan ekte yumuşasa da sözlükten okunur: evlat → evladım (ince l kalır), t/p/ç → d/b/c.
- Ölçüler: literatür sınavı değişmedi (120 / 123, %97,6); Vikisözlük son hece dışı vurgu %22,5 → %22,7.
- README: örnek çıktısı düzeltildi (`ɟideˈdʒeiz`); kurulum, API ve düzen bölümleri eklendi.

## 0.1.0 — ilk açık sürüm

- İlk yayın. Ayrıntılı ölçümler README'de.
- Bağımlılıksız Türkçe G2P (k/g/l incelmesi, uzun ünlüler, yumuşak g, sayı ve kısaltma okuma, 1.488 sözcüklük okunuş sözlüğü).
- Kaynaklı sözcük vurgusu (en soldaki aday kazanır): sözlüksel kökler (1.203 sözcük), vurgu almayan ve vurgu çeken ekler, olumsuz emir -mA- + -(y)In(Iz), Sezer kuralı.
- İsteğe bağlı turkce-normalize (`[tam]` eki); komut satırı `python -m turkce_vurgu`.
