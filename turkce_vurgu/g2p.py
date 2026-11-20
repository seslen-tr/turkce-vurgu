# -*- coding: utf-8 -*-
"""
TÜRKÇE G2P — metin → IPA ses dizisi (StyleTTS2 öğrencisinin girdisi).

Neden kendimiz: StyleTTS2 / Kokoro espeak kullanır (GPL; ürüne giremez) ve espeak'in
Türkçesi vurgu ve incelme (k/g/l) konusunda zayıf.
Türkçe yazıldığı gibi okunur; birkaç kural yeter:
  - k, g, l ön ünlüyle (e i ö ü, î â'nın incelttiği) incelir: k→c, g→ɟ, l→l;
    kalın ünlüyle kalın: k, ɡ, ɫ. Ünsüzün ünlüsü: hemen ardındaki ünlü,
    yoksa (hece sonu) öndeki ünlü.
  - â î û: uzun ünlü; â/û önceki k, g, l'yi inceltir (kâr → caːɾ).
  - ğ: ünsüzden / sözcük sonundan önce önceki ünlüyü uzatır (dağ → daː);
    iki ünlü arasında düşer (ağaç → aatʃ).
  - Sayılar, yüzde, birkaç kısaltma sözcüğe açılır (sayi.py).
  - Yazımda görünmeyen uzun ünlü ve ince l/k/g okunuş sözlüğünden (veri/okunus.tsv,
    Vikisözlük; TDK telaffuzuyla düzeltilmiş): memur → meːmuɾ, metal → metal, kilometre → cilometɾe.
    Ünlüyle başlayan ekte uzayan kökler veri/ek_uzun.tsv'de (TDK): icat → iːdʒat, icadı → iːdʒaːdɯ.
Noktalama korunur (, . ! ? ; : …): öğrenci duraklamayı ve tonlamayı ondan öğrenir.
vurgu=True: vurgulu hecenin önüne ˈ (vurgu.py; özel adlar büyük harf ve kesme
işaretinden, normalleştirmeden ÖNCE bulunur).
Semboller StyleTTS2'nin özgün sembol listesinde var: önceden eğitilmiş
metin gömmeleri yeniden kullanılabilir.

    python -m turkce_vurgu "Dikkat! Kâr %12,5 arttı."
"""
from __future__ import annotations

import re
import sys
import unicodedata
from functools import lru_cache
from pathlib import Path

from .sapka import ek_okunuslar
from .sayi import okunus as _okunus
from .vurgu import YER_ADLARI, _daha_uzun_kok, _ek_mi, _ek_zinciri, _sozluk, heceler, vurgulu_hece

KALIN = set("aıou")
INCE = set("eiöü")
UNLU = KALIN | INCE | set("âîû")
NOKTALAMA = ",.!?;:…"
_BASIT = {"a": "a", "b": "b", "c": "dʒ", "ç": "tʃ", "d": "d", "e": "e", "f": "f", "h": "h", "ı": "ɯ",
          "i": "i", "j": "ʒ", "m": "m", "n": "n", "o": "o", "ö": "ø", "p": "p", "r": "ɾ", "s": "s",
          "ş": "ʃ", "t": "t", "u": "u", "ü": "y", "v": "v", "y": "j", "z": "z",
          "â": "aː", "î": "iː", "û": "uː", "w": "v", "x": "ks", "q": "k"}
KISALTMA = {"km": "kilometre", "m²": "metrekare", "m2": "metrekare", "cm": "santimetre", "kg": "kilogram",
            "tl": "türk lirası", "vb": "ve benzeri", "vs": "vesaire", "dr": "doktor", "sn": "sayın",
            "no": "numara", "mah": "mahallesi", "cad": "caddesi", "sok": "sokağı"}
SEMBOLLER = sorted(set("".join(_BASIT.values())) | set("cɟɡkɫlːˈ ") | set(NOKTALAMA))
_HARF = "A-Za-zÇĞİÖŞÜÂÎÛçğıöşüâîû"


def _kucuk(s: str) -> str:
    return unicodedata.normalize("NFC", s.replace("I", "ı").replace("İ", "i")).lower()


def _sayi(m: re.Match) -> str:
    tam, kesir = m.group(1).replace(".", ""), m.group(2)
    s = " ".join(_okunus(int(tam)))
    if kesir:
        s += " virgül " + " ".join(_okunus(int(kesir))) if not kesir.startswith("0") else \
            " virgül " + " ".join("sıfır" if c == "0" else " ".join(_okunus(int(c))) for c in kesir)
    return f" {s} "


try:                                   # isteğe bağlı: tarih, saat, para, kısaltma, Roma rakamı, kesir…
    from turkce_normalize import normalize as _tam_normalize
except ImportError:                    # pragma: no cover — yalın kurulumda basit sayı/kısaltma okuyucu
    _tam_normalize = None


def normallestir(metin: str, tam: bool = True) -> str:
    """Metni okunuşa hazırlar. turkce-normalize kuruluysa (tam=True) önce o çalışır;
    yoksa yalnız sayılar, yüzde ve birkaç kısaltma açılır."""
    metin = re.sub(r"<!--.*?(?:-->|$)|<[^>\n]{1,200}>", " ", metin, flags=re.S)      # HTML yorumu ve etiketi
    if tam and _tam_normalize is not None:
        metin = _tam_normalize(metin)
    s = _kucuk(metin)
    s = re.sub(r"%\s*(\d)", r"yüzde \1", s)
    s = re.sub(r"(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?", _sayi, s)
    s = re.sub(r"\b(" + "|".join(map(re.escape, KISALTMA)) + r")\b\.?",
               lambda m: KISALTMA[m.group(1)], s)
    s = re.sub(r"[\"“”‘’'()\[\]«»]", "", s)
    s = re.sub(r"\.\.\.", "…", s)
    # Boşluklu tire ve uzun çizgi ara söz duraklamasıdır ("Ankara — başkent —"); sözcük içi tire değildir:
    # "ar-ge", "e-devlet", "sentinel-2" 0.1.1'e kadar "ar, ge" diye virgülle (duraklamayla) okunuyordu.
    s = re.sub(r"\s+[-–—]+\s+|\s*—\s*", ", ", s)
    s = re.sub(r"[-–‐‑]", " ", s)
    # Biçim işaretleri (Markdown, kod) okunmaz; modele giderse anlamsız ses olur ("<!--" → gürültü, 03.11.2026).
    s = re.sub(r"\s*[·•◦▪‣]\s*", ", ", s)                             # madde ayırıcı nokta: duraklama
    s = re.sub(r"[#*_<>|~^`\\{}=@$/©®™]+", " ", s)
    # Türkçede olmayan harfler (sözlükte olmayan yabancı sözcük): en yakın Türkçe ses ("librivox" → "librivoks")
    s = s.replace("x", "ks").replace("w", "v").replace("q", "k")
    s = re.sub(r"\s*[,;:](?:\s*[,;:])+\s*", ", ", s)                 # işaret silinince kalan art arda virgüller
    s = re.sub(r"^[\s,;:.]+", "", s)
    return re.sub(r"\s+", " ", s).strip()


# Gün ve ay adları büyük harfle ve kesmeyle yazılsa da özel ad vurgusu almaz ("Pazar'a", "Mayıs'ta")
GUN_AY = set("""pazartesi salı çarşamba perşembe cuma cumartesi pazar ocak şubat mart nisan mayıs haziran temmuz
ağustos eylül ekim kasım aralık""".split())


def _sozluk_koku(w: str, kume) -> str:
    """w'nin kümedeki en uzun kökü (ardı ek zinciri), yoksa ""."""
    return next((w[:n] for n in range(len(w), 1, -1) if w[:n] in kume and _ek_zinciri(w[n:])), "")


def ozel_kokler(metin: str) -> set[str]:
    """Özel ad kökleri (küçük harf): kesme işaretinden önceki kısım (Serdivan'daki → serdivan), cümle başı olmayan,
    büyük harfle başlayan sözcük (… Zeynep ile → zeynep) ya da cümle başında sözlükte sıradan sözcük olmayan özel ad
    (Rusya ile → rusya). 18.11.2026: büyük harfli sıradan sözcük özel ad sayılmaz ("Bugün Pazar" → "ˈpazar",
    "Dünya Sağlık Örgütü'nde" üç sözcük de ilk hecede vurgulanıyordu): kökü yalnız sözlükte (kokler) olan ya da hem
    sözlükte hem özel ad listesinde olup il ya da kişi adı olmayan sözcük, kesmesizse sıradandır; gün ve ay adı hep
    sıradandır."""
    sz = _sozluk()
    yer = YER_ADLARI
    kok = set()
    for m in re.finditer(rf"[{_HARF}]+(?:['’][{_HARF}]+)?", metin):
        t = m.group(0)
        once = metin[:m.start()].rstrip()
        bas = not once or once[-1] in ".!?…:"
        if "'" in t or "’" in t:
            k = _kucuk(re.split("['’]", t)[0])
            siradan = k in GUN_AY or (k not in sz["ozel"] and k not in yer and _sozluk_koku(k, sz["kokler"])
                                       and not _sozluk_koku(k, sz["ozel"]))
            if not siradan:
                kok.add(k)
        elif len(t) > 2 and t[0].isupper() and not t.isupper():
            w = _kucuk(t)
            oz = _sozluk_koku(w, sz["ozel"] | yer)
            if bas:                      # cümle başı: yalnız sözlükte sıradan karşılığı olmayan özel ad
                if oz and oz not in sz["kokler"] and oz not in GUN_AY:
                    kok.add(w)
            elif oz:
                if oz in yer or oz in sz["adlar"] or (oz not in sz["kokler"] and oz not in GUN_AY):
                    kok.add(w)
            elif not _sozluk_koku(w, sz["kokler"]):
                kok.add(w)               # sözlükte hiç yok: büyük olasılıkla ad
    return kok


def _sozcuk(w: str, vurgu_harf: int | None = None) -> str:
    out: list[str] = []
    n = len(w)
    for i, ch in enumerate(w):
        if i == vurgu_harf:
            out.append("ˈ")
        if ch in "kgl":
            sonra = w[i + 1] if i + 1 < n else ""
            if sonra in UNLU:
                ince = sonra in INCE or sonra in "âîû"
            else:
                once = next((w[j] for j in range(i - 1, -1, -1) if w[j] in UNLU), "")
                ince = once in INCE or once == "î"
            out.append({"k": "ck", "g": "ɟɡ", "l": "lɫ"}[ch][0 if ince else 1])
        elif ch == "ğ":
            sonra = w[i + 1] if i + 1 < n else ""
            if sonra not in UNLU and out and out[-1][-1] in "aeɯioøuy":
                out.append("ː")
        elif ch in _BASIT:
            out.append(_BASIT[ch])
    return "".join(out)


def g2p(metin: str, vurgu: bool = False) -> str:
    kokler = ozel_kokler(metin) if vurgu else set()
    s = normallestir(metin)
    parca = re.findall(rf"[a-zçğıöşüâîûwxq]+|[{re.escape(NOKTALAMA)}]", s)
    out = ""
    for i, p in enumerate(parca):
        if p in NOKTALAMA:
            out = out.rstrip() + p + " "
            continue
        son = i + 1 == len(parca) or parca[i + 1] in NOKTALAMA        # cümle / yan cümle sonu (olumsuz emir)
        out += sozcuk_okunusu(p, kokler, vurgu, son) + " "
    return out.strip()


def sozcuk_vurgusu(p: str, kokler: set[str] = frozenset(), son: bool = False) -> int | None:
    """Normalleştirilmiş tek sözcüğün vurgulu hecesinin sırası (vurgusuz sözcükte None).
    son: sözcük cümle ya da yan cümle sonunda."""
    ozel = max((k for k in kokler if p.startswith(k) and (p == k or _ek_mi(p[len(k):]) or len(k) >= 4)),
               key=len, default="")
    return vurgulu_hece(p, ozel, son)


@lru_cache(maxsize=1)
def _okunus_sozlugu() -> dict[str, str]:
    """veri/okunus.tsv: yazımda görünmeyen uzun ünlü ve ince l/k/g (Vikisözlük, CC BY-SA 4.0); üstüne şapkasız
    yazılan alıntılar ve ince l'li alıntılar (sapka.py; Vikisözlük kaydı varsa o geçer)."""
    yol = Path(__file__).resolve().parent / "veri" / "okunus.tsv"
    oz = {} if not yol.exists() else dict(
        s.split("\t") for s in yol.read_text(encoding="utf-8").splitlines() if s and not s.startswith("#"))
    for w, ipa in ek_okunuslar(_sozluk()["kokler"], _sozcuk, oz).items():
        oz.setdefault(w, ipa)
    for w in _ek_uzun_sozlugu():       # ekte uzayan kök (merak → merakı) yalın okunuşu kurala eşit olsa da kök
        oz.setdefault(w, _sozcuk(w))
    return oz


@lru_cache(maxsize=1)
def _ek_uzun_sozlugu() -> dict[str, str]:
    """veri/ek_uzun.tsv: ünlüyle başlayan ekte son ünlüsü uzayan kökler (TDK telaffuzu: icat → i:cat ama
    icadı → i:ca:dı; ilan → i:la:nı). 0.1.6'ya kadar ekli biçimde de kısa okunuyordu."""
    yol = Path(__file__).resolve().parent / "veri" / "ek_uzun.tsv"
    return {} if not yol.exists() else dict(
        s.split("\t")[:2] for s in yol.read_text(encoding="utf-8").splitlines() if s and not s.startswith("#"))


_FONEM = re.compile(r"dʒ|tʃ|[aeiɯoøuy]ː?|.")


def _vurgu_koy(fonem: str, k: int) -> str:
    """IPA dizisinde k. hecenin önüne ˈ koyar (heceleme vurgu.heceler ile aynı kural)."""
    t = _FONEM.findall(fonem)
    unlu = [i for i, x in enumerate(t) if x[0] in "aeiɯoøuy"]
    if k >= len(unlu):
        return fonem
    if k == 0:
        bas = 0
    else:
        once, simdi = unlu[k - 1], unlu[k]
        bas = simdi if simdi - once == 1 else simdi - 1
    return "".join(t[:bas]) + "ˈ" + "".join(t[bas:])


_YUMUSAMA = {"t": ("d", "t", "d"), "p": ("b", "p", "b"), "ç": ("c", "tʃ", "dʒ")}


def _yumusak_kok(p: str, oz: dict[str, str]) -> str | None:
    """Ünlüyle başlayan ekte yumuşayan sözlük kökü: evlat → evladım, kitap → kitabı (okunuş sözlükten, ek kuralla)."""
    aday = [(r[:-1] + _YUMUSAMA[r[-1]][0], r) for r in oz if len(r) >= 3 and r[-1] in _YUMUSAMA]
    y, r = max(((y, r) for y, r in aday if p.startswith(y) and len(p) > len(y) and p[len(y)] in UNLU
                and _ek_mi(p[len(y):])), key=lambda a: len(a[0]), default=("", ""))
    if not y or _daha_uzun_kok(p, y, _sozluk()["kokler"], _sozluk()["ozel"]):
        return None                    # "kalbur" ⊄ "kalp": sözlükte daha uzun kök varsa yumuşama değil
    _, sert, yumusak = _YUMUSAMA[r[-1]]
    taban = _ek_uzun_sozlugu().get(r, oz[r])           # yumuşama hep ünlüyle başlayan ekte: icat → icadı
    if not taban.endswith(sert):
        return None
    return taban[: -len(sert)] + yumusak + _sozcuk(p)[len(_sozcuk(y)):]


def sozcuk_okunusu(p: str, kokler: set[str] = frozenset(), vurgu: bool = False, son: bool = False) -> str:
    """Normalleştirilmiş tek sözcük → IPA. kokler: metnin özel ad kökleri (ozel_kokler).
    Sözcük ya da kökü okunuş sözlüğündeyse (memur, metal…) kök oradan, ekler kurallarla okunur."""
    k = sozcuk_vurgusu(p, kokler, son) if vurgu else None
    oz = _okunus_sozlugu()
    if p in oz:
        fonem = oz[p]
    else:
        kok = max((r for r in oz if p.startswith(r) and len(r) >= 3 and not r.endswith("ğ") and _ek_zinciri(p[len(r):])),
                  key=len, default="")
        if kok and _daha_uzun_kok(p, kok, _sozluk()["kokler"], _sozluk()["ozel"]):
            kok = ""                   # "sela" ⊂ "selanik": sözlükte olmayan daha uzun kök varsa kural okur
        taban = _ek_uzun_sozlugu().get(kok) if kok and p[len(kok):][:1] in UNLU else None
        fonem = (taban or oz[kok]) + _sozcuk(p)[len(_sozcuk(kok)):] if kok else _yumusak_kok(p, oz)
    if fonem is None:
        return _sozcuk(p, None if k is None else heceler(p)[k])
    return fonem if k is None else _vurgu_koy(fonem, k)
