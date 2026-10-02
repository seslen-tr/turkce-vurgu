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

from .sayi import okunus as _okunus
from .vurgu import _ek_mi, heceler, vurgulu_hece

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


def normallestir(metin: str) -> str:
    s = _kucuk(metin)
    s = re.sub(r"%\s*(\d)", r"yüzde \1", s)
    s = re.sub(r"(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?", _sayi, s)
    s = re.sub(r"\b(" + "|".join(map(re.escape, KISALTMA)) + r")\b\.?",
               lambda m: KISALTMA[m.group(1)], s)
    s = re.sub(r"[\"“”‘’'()\[\]«»]", "", s)
    s = re.sub(r"\.\.\.", "…", s)
    s = re.sub(r"\s*[-–—]\s*", ", ", s)
    return re.sub(r"\s+", " ", s).strip()


def ozel_kokler(metin: str) -> set[str]:
    """Özel ad kökleri (küçük harf): kesme işaretinden önceki kısım (Serdivan'daki → serdivan) ya da
    cümle başı olmayan, büyük harfle başlayan sözcük (… Zeynep ile → zeynep)."""
    kok = set()
    for m in re.finditer(rf"[{_HARF}]+(?:['’][{_HARF}]+)?", metin):
        t = m.group(0)
        if "'" in t or "’" in t:
            kok.add(_kucuk(re.split("['’]", t)[0]))
        elif len(t) > 2 and t[0].isupper() and not t.isupper():
            once = metin[:m.start()].rstrip()
            if once and once[-1] not in ".!?…:":
                kok.add(_kucuk(t))
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
    for p in parca:
        if p in NOKTALAMA:
            out = out.rstrip() + p + " "
            continue
        out += sozcuk_okunusu(p, kokler, vurgu) + " "
    return out.strip()


def sozcuk_vurgusu(p: str, kokler: set[str] = frozenset()) -> int | None:
    """Normalleştirilmiş tek sözcüğün vurgulu hecesinin sırası (vurgusuz sözcükte None)."""
    ozel = max((k for k in kokler if p.startswith(k) and (p == k or _ek_mi(p[len(k):]) or len(k) >= 4)),
               key=len, default="")
    return vurgulu_hece(p, ozel)


def sozcuk_okunusu(p: str, kokler: set[str] = frozenset(), vurgu: bool = False) -> str:
    """Normalleştirilmiş tek sözcük → IPA. kokler: metnin özel ad kökleri (ozel_kokler)."""
    harf = None
    if vurgu:
        k = sozcuk_vurgusu(p, kokler)
        harf = None if k is None else heceler(p)[k]
    return _sozcuk(p, harf)
