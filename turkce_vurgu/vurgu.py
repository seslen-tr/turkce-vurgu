# -*- coding: utf-8 -*-
"""
TÜRKÇE SÖZCÜK VURGUSU — vurgulu heceyi dilbilim literatüründeki kurallarla bulur.

Kaynaklar (kısaltmalar kodda geçer):
  I&O  Inkelas & Orgun 2003, "Turkish stress: a review", Phonology 20:139–161
  Ink  Inkelas 1999, "Exceptional stress-attracting suffixes in Turkish"
  G&K  Göksel & Kerslake 2005, Turkish: A Comprehensive Grammar, s. 26–34
  O&I  Oflazer & Inkelas, "A finite state pronunciation lexicon for Turkish"
  Sezer 1981, "On non-final stress in Turkish", Journal of Turkish Studies 5:61–69
  Wikt Vikisözlük (kaikki.org dökümü), CC BY-SA 4.0 — veri/istisna.tsv vb.

Algoritma (O&I; I&O "innermost wins"; Ink "leftmost nonneutral wins"):
  1. Sözcükteki vurgu adaylarını topla:
       - sözlüksel vurgulu kök (Wikt istisnaları, literatürde listelenen sözcükler),
       - özel ad kökü: Sezer kuralı (yer adları, yabancı/yeni adlar; Türkçe kişi adları HARİÇ),
       - vurgu çeken ekler (-Iyor, -ArAk, -IncE, -(y)Iver, -mAksIzIn, -sAnA): ekin ilk hecesi,
       - vurgu almayan ekler ve klitikler (olumsuzluk -mA-, ek-eylem -(y)DI/-(y)mIş/-(y)sA,
         -DIr, -(y)ken, -(y)lA, -CA, -leyin, -CAsInA, kişi ekleri…): ekten ÖNCEKİ hece.
  2. En SOLDAKİ aday kazanır.
  3. Aday yoksa son hece (I&O s.140).
Yazımdan çözülemeyen ikilikler (GİTme "gitme!" / gitME "gitmek"; -(y)Im ek-eylem / iyelik;
yüklem -lAr / çoğul) bağlamsız çözülemez: vurgulanabilir okuma (son hece) seçilir. Tek bağlam ipucu:
cümle ya da yan cümle sonundaki yalın eylem+mA olumsuz emirdir (acele ETme., KORKma!).

Hece: her ünlü bir hece; iki ünlü arasındaki tek ünsüz sonraki heceye, birden çoksa yalnız
sonuncusu sonraki heceye geçer (ka-lem, an-ka-ra, türk-çe).
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

UNLU = set("aeıioöuüâîû")
_V = "aeıioöuüâîû"
VERI = Path(__file__).resolve().parent / "veri"

# Vurgusuz sözcükler (klitikler, bağlaçlar): G&K — mI, dA, ki, ya, bile, ise; ile.
VURGUSUZ = {"de", "da", "ki", "ya", "bile", "ise", "ile", "ve"}
_SORU = re.compile(r"^m[ıiuü](y[ıiuü]m|s[ıiuü]n|y[ıiuü]z|s[ıiuü]n[ıiuü]z|d[ıiuü]r|yd[ıiuü]\w*|ym[ıiuü]ş\w*|ş|l[ae]r)?$")

# Literatürde adı geçen sözlüksel vurgulu sözcükler (ˈ vurgulu hecenin başında). Wikt'i tamamlar,
# çelişirse bu kazanır. Kaynak satır sonunda.
LITERATUR = """
ˈşimdi ˈbelki ˈyarın ˈancak ˈhangi ˈhani ˈnasıl ˈniçin ˈbugün ˈbaşbakan ˈbuzdolabı                 # G&K 27–29
loˈkanta ˈbanka isˈkemle ˈtaksi ˈlobi ˈfutbol poliˈtika isˈkele ˈkapkara ˈufacık ˈyayla taˈmamen   # G&K
ˈfakat ˈacaba ˈamca ˈçanta baˈraka ˈnegatif akˈvaryum fabˈrika ˈbazen ˈlütfen ˈzaten              # Yawney 2018
muhˈtemelen ˈnadiren                                                                              # Yawney / Sezer
tarˈhana abˈluka ˈpenaltı kaˈsımpatı deˈreotu                                                     # Ink, I&O
ˈora ˈbura ˈşura ˈnere                                                                            # G&K: -rA (Orada, NEreye)
kasˈtamonu ˈzonguldak ˈerzincan üsˈküdar berˈgama belˈçika mekˈsika afˈrika avˈrupa ingilˈtere berˈmuda  # Sezer istisnaları, I&O 143
eˈminönü ˈsaimbeyli                                                                               # birleşik yer adları, I&O / Woodard
ˈharika                                                                                           # yaygın söyleyiş (Seslen dinleme, 10.2026)
"""
# Sezer kuralının İŞLEMEDİĞİ adlar (I&O 149–151): düzenli kök gibi davranır (son hece, ekler vurgu alır).
SEZERSIZ_SON = re.compile(r"(istan|hane)$")
# Vikisözlük ile dilbilgisi kaynaklarının çeliştiği sözcüklerde kaynak kazanır: son hece (düzenli).
LITERATUR_SON = {"anadolu", "kabakulak", "alışveriş", "bilgisayar"}           # I&O 143; G&K

# Cümle başında da (büyük harf ipucu olmadan) tanınan yer adları: Türkiye illeri ve Sakarya ilçeleri.
YER_ADLARI = set("""
adana adıyaman afyonkarahisar ağrı aksaray amasya ankara antalya ardahan artvin aydın balıkesir bartın
batman bayburt bilecik bingöl bitlis bolu burdur bursa çanakkale çankırı çorum denizli diyarbakır düzce
edirne elazığ erzincan erzurum eskişehir gaziantep giresun gümüşhane hakkari hatay ığdır ısparta istanbul
izmir kahramanmaraş karabük karaman kars kastamonu kayseri kilis kırıkkale kırklareli kırşehir kocaeli
konya kütahya malatya manisa mardin mersin muğla muş nevşehir niğde ordu osmaniye rize sakarya samsun
siirt sinop sivas şanlıurfa şırnak tekirdağ tokat trabzon tunceli uşak van yalova yozgat zonguldak
serdivan sapanca hendek akyazı geyve arifiye erenler ferizli söğütlü karapürçek kaynarca pamukova taraklı
adapazarı
""".split())

# Kökten sonra gelebilecek ek dizisinin başı (masa+lar evet, masa+l → masal hayır).
_EK = re.compile(r"^$|^[aeıiuü]|^(l[ae]|d[ae]|t[ae]|y[ae]|y[ıiuü]|y[dms]|n[ıiuü]n|s[ıiuü]|s[ae]|m[ıiuü]z|n[ıiuü]z|m|n|"
                 r"[dt][ıiuü]r|c[ıiuü]|ç[ıiuü]|c[ae]|ç[ae]|n[ae]|l[ıiuü])")
# Türetilmiş eylem gövdesinin uzantıları (edilgen, dönüşlü, ettirgen, işteş, yeterlik): yap+ıl, yap+tır, anlat+a.
_TUREME = re.compile(r"^(?:[ıiuü]?[ln]|[dt][ıiuü]r|[ıiuü]?ş|[ıiuü]t|t|[ae]r|l[ae]ş|l[ae]|y?[ae])+$")
_KISA_KOK = {"ora", "bura", "şura", "nere"}
_INCE_DEGIL = {"düşünce", "gülünce"}           # -IncE gibi biten ad: düşünCE
# Yalın -mA ile biten, ad olarak yerleşmiş sözcükler: cümle sonunda da emir sayılmaz (dondurMA).
_MA_AD = set("""
dondurma dolma sarma kavurma kızartma haşlama doğrama süzme dokuma kazma
""".split())
# var/yok + ek-eylem: vurgu kökte (VARdı, YOKmuş, VARdır, YOKsa); varmak eyleminin çekimiyle karışmasın diye ayrı.
_VAR_YOK = re.compile(r"^(var|yok)(m[ıu]ş|[dt][ıu]|s[ae]|[dt][ıu]r|ken)(l[ae]r|m|n|k|n[ıu]z|s[ıu]n(?:[ıu]z)?|[ıu]m|[ıu]z)?$")
_ZAMAN = {"sabah", "akşam", "öğle", "öğlen", "gece", "kış", "yaz", "bahar", "güz", "ilkbahar", "sonbahar"}


def _ek_mi(kalan: str) -> bool:
    return bool(_EK.match(kalan))


def heceler(w: str) -> list[int]:
    """Her hecenin başladığı harf konumu."""
    u = [i for i, c in enumerate(w) if c in UNLU]
    if not u:
        return [0]
    bas = [0]
    for onceki, simdi in zip(u, u[1:]):
        bas.append(simdi if simdi - onceki == 1 else simdi - 1)
    return bas


def _konum(isaretli: str) -> int:
    """'loˈkanta' → vurgulu hecenin sırası (1)."""
    i = isaretli.index("ˈ")
    w = isaretli.replace("ˈ", "")
    return max(k for k, b in enumerate(heceler(w)) if b <= i)


@lru_cache(maxsize=1)
def _sozluk() -> dict:
    def oku(ad: str) -> list[str]:
        yol = VERI / ad
        if not yol.exists():
            return []
        return [s for s in yol.read_text(encoding="utf-8").splitlines() if s and not s.startswith("#")]
    istisna: dict[str, int] = {}
    for s in oku("istisna.tsv"):
        w, v, _ = s.split("\t")
        istisna[w] = int(v)
    for satir in LITERATUR.strip().splitlines():
        for isaretli in satir.split("#")[0].split():
            istisna[isaretli.replace("ˈ", "")] = _konum(isaretli)
    for w in LITERATUR_SON:
        istisna.pop(w, None)
    return {"istisna": istisna, "adlar": set(oku("adlar.txt")), "kokler": set(oku("kokler.txt")),
            "fiiller": set(oku("fiiller.txt")), "ozel": set(oku("ozel.txt"))}


def _hece(bas: list[int], i: int) -> int:
    """i. harfin bulunduğu hece."""
    return max(k for k, b in enumerate(bas) if b <= i)


def _agir(w: str, bas: list[int], k: int) -> bool:
    son = bas[k + 1] if k + 1 < len(bas) else len(w)
    hece = w[bas[k]:son]
    return hece[-1] not in UNLU or any(c in "âîû" for c in hece)


def sezer(w: str) -> int:
    """Sezer 1981: sondan üçüncü hece ağır ve sondan ikinci hafifse sondan üçüncü; yoksa sondan ikinci."""
    bas = heceler(w)
    n = len(bas)
    if n < 3:
        return 0
    return n - 3 if _agir(w, bas, n - 3) and not _agir(w, bas, n - 2) else n - 2


_YUMUSAMA = str.maketrans("dğbc", "tkpç")


def _fiil_govdesi(s: str, addan: bool = True) -> bool:
    """s bir eylem gövdesi mi: sözlükte, sözlükteki bir gövde + türetme ekleri, ünsüz yumuşamasıyla
    (gid- ← git-), ya da addan -lA ile türemiş (tekme+le). addan=False: yalnız sözlükteki eylemler."""
    sz = _sozluk()
    f = sz["fiiller"]

    def var(g: str) -> bool:
        return g in f or (g[-1:] in "dğbc" and g[:-1] + g[-1].translate(_YUMUSAMA) in f)
    if s and (var(s) or any(var(s[:k]) and _TUREME.match(s[k:]) for k in range(2, len(s)))):
        return True
    return addan and bool(re.search(r"l[ae]$", s)) and (s[:-2] in sz["kokler"] or s[:-2] in sz["ozel"])


def _kok_vurgusu(w: str, ozel_kok: str) -> tuple[int | None, int]:
    """(kök vurgusunun hecesi ya da None, ek kurallarının aranacağı ilk harf)."""
    sz = _sozluk()
    ist = sz["istisna"]
    if w in ist:
        return ist[w], len(w)
    if w in LITERATUR_SON:
        return None, len(w)
    kok = ozel_kok if ozel_kok and w.startswith(ozel_kok) else \
        max((a for a in YER_ADLARI if w.startswith(a) and _ek_mi(w[len(a):])), key=len, default="")
    if kok:
        if kok in ist:
            return ist[kok], len(kok)
        # Türkçe kişi adları düzenli (AhMET bile, AlLİ'yle — G&K); -istan, -hane, tek hece (BonDAN, Ink ex.15)
        if kok in sz["adlar"] or kok in LITERATUR_SON or SEZERSIZ_SON.search(kok) or len(heceler(kok)) < 2:
            return None, len(kok)
        if kok.endswith("iye") and len(heceler(kok)) >= 3:
            return _son_unlu_hecesi(kok, len(kok) - 3), len(kok)               # SulTAniye (I&O 150)
        return sezer(kok), len(kok)
    if w not in sz["kokler"]:     # sözlükte kendi maddesi olan sözcük (kabakulak) kökten vurgu devralmaz
        for k in sorted((k for k in ist if w.startswith(k) and len(k) < len(w)), key=len, reverse=True):
            if (len(k) >= 4 or k in _KISA_KOK) and (_ek_mi(w[len(k):]) or k in sz["fiiller"]):
                return ist[k], len(k)                                         # tarHAnada, geLİverdi
    return None, 0


def _son_unlu_hecesi(w: str, i: int) -> int:
    """i. harften önceki son ünlünün hecesi: ünlüyle başlayan ekte önceki ünsüz eke geçer
    (sul-ta-n+iye → sul-ta-ni-ye), vurgulanan hece yine ekten önceki ünlününkidir."""
    j = max((k for k in range(i) if w[k] in UNLU), default=0)
    return _hece(heceler(w), j)


def _ek_adaylari(w: str, bas: list[int], ilk: int, son: bool = False) -> list[int]:
    """Vurgu çeken ve vurgu almayan eklerin önerdiği heceler; yalnız ilk. harften sonra başlayan ekler.
    son: sözcük cümle ya da yan cümle sonunda (ardından noktalama ya da metin sonu)."""
    sz = _sozluk()
    n = len(bas)
    aday: list[int] = []

    def once(m: re.Match | None, g: int) -> None:          # ekten ÖNCEKİ hece (vurgu almayan ek)
        if m and m.start(g) >= max(ilk, 1):
            aday.append(_son_unlu_hecesi(w, m.start(g)))

    def kendi(m: re.Match | None, g: int) -> None:         # ekin İLK hecesi (vurgu çeken ek)
        if m and m.start(g) >= max(ilk, 1):
            aday.append(_hece(bas, m.start(g)))

    # ── vurgu çeken ekler: ilk hece (Ink ex.54, 61; G&K) ───────────────────────────────────────
    m = re.search(rf"[{_V}](yor)", w)
    if m and m.start(1) - 1 >= ilk:
        aday.append(_hece(bas, m.start(1) - 1))                                      # geLİyor, yüRÜyor
    if n >= 3 and w not in _INCE_DEGIL:
        for desen in (r"(y?[ae])r[ae]k$", r"(y?[ıiuü])nc[ae]$", r"(s[ae])n(?:[ae]|[ıi]z[ae])$"):
            m = re.search(desen, w)                                                  # yaPArak, geLİnce, gelSEne
            if m and _fiil_govdesi(w[:m.start(1)], addan=False):
                kendi(m, 1)
    # birleşik eylemler -(y)Akal, -(y)Agel, -(y)Adur, -(y)Ayaz: ilk hece (G&K: şaŞAkaldım)
    m = re.search(r"(y?[ae])(kal|gel|dur|yaz)", w)
    if m and m.start(1) > 0 and _fiil_govdesi(w[:m.start(1)], addan=False):
        kendi(m, 1)
    m = re.search(r"(y?[ıiuü])ver(?:d[ıi]\w*|ir\w*|ecek\w*|eceğ\w*|miş\w*|sin|in|iyor\w*|me\w*|ince|erek|e|en)?$", w)
    if m and _fiil_govdesi(w[:m.start(1)]):
        kendi(m, 1)                                                                  # tuTUver, geLİverdi
    kendi(re.search(r"(m[ae]k)s[ıi]z[ıi]n$", w), 1)                                  # bakMAKsızın

    # ── olumsuzluk -mA- (I&O 141; Ink ex.61–62, 70) ────────────────────────────────────────────
    m = re.search(r"(m[ae])(d[ıi](m|n|k|n[ıi]z|l[ae]r)?(s[ae]|ysa|ydı|ymış)?|m[ıi]ş\w*|d[ae]n|y[ae]c[ae][kğ]\w*|"
                  r"y[ae]l[ıi]m|y[ıi]p|y[ıi]nc[ae]|y[ae]r[ae]k|s[ıi]n(l[ae]r)?|m[ae]l[ıi]\w*|s[ae]\w*|"
                  r"y[ıi]n([ıi]z)?)$", w)                                            # olumsuz emir: GEÇmeyin
    if m and _fiil_govdesi(w[:m.start(1)]):
        once(m, 1)                                                                   # GİTmedik, oKUmayacak
    m = re.search(r"(m[ae])$", w)                                                   # olumsuz emir, yan cümle sonunda
    if son and m and n >= 2 and w not in _MA_AD and _fiil_govdesi(w[:m.start(1)], addan=False):
        once(m, 1)                                                                   # acele ETme. KORKma!
    m = re.search(r"(m[ıiuü])yor", w)
    if m and _fiil_govdesi(w[:m.start(1)]):
        once(m, 1)                                                                   # GELmiyor, anlaTAmıyor
    # olumsuz geniş zaman -mAz/-mAm/-mAyIz vurgulanabilir: vurgu -mA- hecesinde (G&K: bakMAZdık, yazMAyız)
    m = re.search(r"(m[ae])(z\w*|m|y[ıi]z|y[ıi]m)$", w)
    if m and _fiil_govdesi(w[:m.start(1)]):
        kendi(m, 1)

    # ── ek-eylem ve kişi ekleri zaman ekinden sonra vurgu almaz (G&K 32–34; I&O fn.4) ──────────
    m = re.search(r"([ae]r|[ıiuü]r|m[ae]z)(d[ıiuü]\w*|s[ae]\w*|[ıiuü]m|[ıiuü]z|s[ıiuü]n(?:[ıiuü]z)?|ken)$", w)
    # kişi ekinde "karar+ım" (iyelik) ile karışmasın; -DI / -sA / -ken'de ad okuması da aynı vurguyu verir
    if m and _fiil_govdesi(w[:m.start(1)]) and (w[:m.end(1)] not in sz["kokler"] or m.group(2)[0] in "dsk"):
        kendi(m, 1)                                                                  # giDERdik, uYUrum, giDERse
    if _VAR_YOK.match(w):
        aday.append(0)                                                               # VARmış, YOKtu, VARdır
    # ad + ek-eylem -mIş (G&K 32): güZELmiş, çoCUKmuş; eylem gövdesinden sonra -mIş zaman ekidir (gelMİŞ)
    m = re.search(r"(m[ıiuü]ş)(l[ae]r)?$", w)
    if m and n >= 2 and (w[:m.start(1)] in sz["kokler"] or w[:m.start(1)] in sz["ozel"])             and not _fiil_govdesi(w[:m.start(1)]):
        once(m, 1)
    once(re.search(r"m[ıiuü]ş((?:t[ıiuü]|y?d[ıiuü])\w*|s[ae]\w*|[ıiuü]m|[ıiuü]z|s[ıiuü]n(?:[ıiuü]z)?|t[ıiuü]r\w*)$", w), 1)
    once(re.search(r"[ae]c[ae]k((?:t[ıi]|s[ae]|s[ıi]n|t[ıi]r)\w*)$", w), 1)          # okuyaCAKtır, gideCEKsin
    once(re.search(r"[ae]c[ae]ğ([ıi]m|[ıi]z)$", w), 1)                               # geleCEğim
    if n >= 3:
        once(re.search(r"(?:d[ıiuü](?:m|n|k|n[ıiuü]z|l[ae]r)?|l[ae]r)(s[ae])$", w), 1)  # geldiLERse
        # ünlüden sonra kaynaştırmalı ek-eylem -(y)DI, -(y)mIş, -(y)sA, -(y)Im, -(y)Iz, -(y)ken: iyelik
        # ünlüden sonra -m/-z olduğundan -yIm/-yIz yalnız ek-eylemdir (okulDAymışlar, öğrenCİyim)
        once(re.search(rf"[{_V}](y)(d[ıiuü]\w*|m[ıiuü]ş\w*|s[ae]\w*|[ıiuü]m|[ıiuü]z|ken)$", w), 1)
    # -DIr ek-eylem; ettirgen -DIr vurgulanabilir (kazanDIR) — eylem gövdesinden sonra aranmaz
    m = re.search(r"([dt][ıiuü]r)(l[ae]r)?$", w)
    if m and n >= 2 and not _fiil_govdesi(w[:m.start(1)]):
        once(m, 1)                                                                   # kiraLIKtır, güZELdir
    if n >= 3 and w.endswith("ken") and w not in sz["kokler"]:
        once(re.search(r"(ken)$", w), 1)                                             # otuRURken, evDEYken
    # -(y)lA araç/birliktelik (I&O 141; Ink ex.61); eylem yapan -lA vurgulanabilir (tekmeLE)
    m = re.search(rf"(?:(?<=[{_V}])(yl[ae])|(l[ae]))$", w)
    if m and w not in sz["kokler"] and not _fiil_govdesi(w, addan=False):
        g = 1 if m.group(1) else 2
        if g == 1 or w[:m.start(2)] in sz["kokler"] or w[:m.start(2)] in sz["ozel"]:
            once(m, g)                                                               # araBAyla, bisikLETle
    # emir 2. çoğul -(y)In(Iz) ünlüden sonra (tekmeLEyin); ünsüzden sonra iyelik/tamlayanla karışır
    m = re.search(rf"(?<=[{_V}])(y[ıiuü]n(?:[ıiuü]z)?)$", w)
    if m and _fiil_govdesi(w[:m.start(1)]):
        once(m, 1)
    # -CA zarf / dil adı / "-ca" (Ink ex.61; I&O 141, 146): güZELce, TÜRKçe, yılLARca
    m = re.search(r"([cç][ae])$", w)
    if m and n >= 2:
        govde = w[:-2]
        if (govde in sz["kokler"] or govde in sz["ozel"] or re.sub(r"l[ae]r$", "", govde) in sz["kokler"]) \
                and govde not in sz["fiiller"]:                                      # eğlen+ce, düşün+ce değil
            once(m, 1)
    # ad + ek-eylem -(y)sA (G&K: bisikLETse, BENse); eylem gövdesinden sonra koşul -sA vurgulanabilir (gelSE)
    m = re.search(r"(s[ae])$", w)
    if m and n >= 2 and w not in sz["kokler"] and not _fiil_govdesi(w[:-2]) and \
            (w[:-2] in sz["kokler"] or w[:-2] in sz["ozel"]) and w[:-1] not in sz["kokler"]:   # elmas+a, ders+e değil
        once(m, 1)
    m = re.search(r"(leyin)$", w)                                                    # akŞAMleyin (Ink ex.61):
    if m and w[:-5] in _ZAMAN:                                                       # yalnız zaman adlarına gelir
        once(m, 1)
    once(re.search(r"([cç][ae]s[ıi]n[ae])$", w), 1)                                  # hayVANcasına (I&O 141)
    return aday


def vurgulu_hece(w: str, ozel_kok: str = "", son: bool = False) -> int | None:
    """Sözcüğün vurgulu hecesinin sırası; vurgusuz sözcükte None.
    w küçük harf, yalnız harf; ozel_kok: metinde özel ad olarak tanınan kök (Serdivan'daki → serdivan);
    son: sözcük cümle ya da yan cümle sonunda."""
    if w in VURGUSUZ or _SORU.match(w):
        return None
    bas = heceler(w)
    kok, ilk = _kok_vurgusu(w, ozel_kok)
    aday = ([kok] if kok is not None else []) + _ek_adaylari(w, bas, ilk, son)
    aday = [a for a in aday if 0 <= a < len(bas)]
    return min(aday) if aday else len(bas) - 1


def isaretle(w: str, ozel_kok: str = "") -> str:
    """Okunuş denetimi için: 'loˈkantada'."""
    k = vurgulu_hece(w, ozel_kok)
    if k is None:
        return w
    b = heceler(w)[k]
    return w[:b] + "ˈ" + w[b:]
