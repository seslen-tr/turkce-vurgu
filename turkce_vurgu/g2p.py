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
    Vikisözlük): memur → meːmuɾ, metal → metal, kilometre → cilometɾe.
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


try:                                   # isteğe bağlı: tarih, saat, para, kısaltma, Roma rakamı, kesir…
    from turkce_normalize import normalize as _tam_normalize
except ImportError:                    # pragma: no cover — yalın kurulumda basit sayı/kısaltma okuyucu
    _tam_normalize = None


def normallestir(metin: str, tam: bool = True) -> str:
    """Metni okunuşa hazırlar. turkce-normalize kuruluysa (tam=True) önce o çalışır;
    yoksa yalnız sayılar, yüzde ve birkaç kısaltma açılır."""
    if tam and _tam_normalize is not None:
        metin = _tam_normalize(metin)
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
    """veri/okunus.tsv: yazımda görünmeyen uzun ünlü ve ince l/k/g (Vikisözlük, CC BY-SA 4.0)."""
    yol = Path(__file__).resolve().parent / "veri" / "okunus.tsv"
    if not yol.exists():
        return {}
    return dict(s.split("\t") for s in yol.read_text(encoding="utf-8").splitlines() if s and not s.startswith("#"))


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
    if not y:
        return None
    _, sert, yumusak = _YUMUSAMA[r[-1]]
    if not oz[r].endswith(sert):
        return None
    return oz[r][: -len(sert)] + yumusak + _sozcuk(p)[len(_sozcuk(y)):]


def sozcuk_okunusu(p: str, kokler: set[str] = frozenset(), vurgu: bool = False, son: bool = False) -> str:
    """Normalleştirilmiş tek sözcük → IPA. kokler: metnin özel ad kökleri (ozel_kokler).
    Sözcük ya da kökü okunuş sözlüğündeyse (memur, metal…) kök oradan, ekler kurallarla okunur."""
    k = sozcuk_vurgusu(p, kokler, son) if vurgu else None
    oz = _okunus_sozlugu()
    if p in oz:
        fonem = oz[p]
    else:
        kok = max((r for r in oz if p.startswith(r) and len(r) >= 3 and not r.endswith("ğ") and _ek_mi(p[len(r):])),
                  key=len, default="")
        fonem = oz[kok] + _sozcuk(p)[len(_sozcuk(kok)):] if kok else _yumusak_kok(p, oz)
    if fonem is None:
        return _sozcuk(p, None if k is None else heceler(p)[k])
    return fonem if k is None else _vurgu_koy(fonem, k)
