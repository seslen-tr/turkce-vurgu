# -*- coding: utf-8 -*-
"""
ZEMBEREK MOTORU (isteğe bağlı) — vurgu kurallarını kalıplar yerine gerçek biçimbirimlere uygular.

    pip install zemberek-python "setuptools<81"
    g2p(metin, vurgu=True, motor="zemberek")

Zemberek (Ahmet A. Akın; Python sürümü zemberek-python, Apache-2.0) sözcüğü kök ve eklerine
ayırır, cümle bağlamıyla tek çözümleme seçer. Kurallar vurgu.py'dekiyle aynı kaynaklardan
(I&O, Ink, G&K, O&I) ve aynı algoritma: adaylar toplanır, EN SOLDAKİ kazanır, yoksa son hece.

Biçimbirim → vurgu sınıfı:
  ÖNCESİ (vurgu almayan; ekten önceki hece): Neg (olumsuz geniş zaman hariç), WithoutHavingDoneSo
    (-mAdAn), Cop (-DIr), While (-ken), Ins (-lA), Equ / Ly (-CA), AsIf (-CAsInA), emir A2pl
    (-(y)In), ad + ek-eylem (Zero'dan sonraki Past / Narr / Cond / kişi ekleri), zaman ekinden
    (Aor, Fut, Narr, Prog) sonraki ek-eylem ve kişi ekleri.
  İLK HECE (vurgu çeken): Prog1 (-Iyor), ByDoingSo (-ArAk), When (-IncE), Hastily (-Iver), Stay
    (-Akal), EverSince (-Agel), Repeat (-Adur), Almost (-Ayaz); olumsuz geniş zamanda -mA- (gelMEZ).
  KÖK: sözlüksel vurgu (istisna.tsv + literatür), özel ad (Zemberek Prop) → Sezer (kişi adları hariç).
Zemberek sözlüğünde tek parça duran türemiş sözcüklerde (çocukça, akşamleyin) gövdeye kalıp
kuralları (vurgu.py) da uygulanır.
Hız: sözcük başına ~25 ms (bağlamlı), ilk yükleme ~3,5 sn.
"""
from __future__ import annotations

import logging
import warnings
from functools import lru_cache

from turkce_vurgu import vurgu as V

_ONCESI = {"Neg", "WithoutHavingDoneSo", "Cop", "While", "Ins", "Equ", "Ly", "AsIf"}
_ILK = {"Prog1", "ByDoingSo", "When", "Hastily", "Stay", "EverSince", "Repeat", "Almost"}
_ZAMAN = {"Aor", "Fut", "Narr", "Prog1", "Prog2"}
_EKEYLEM = {"Past", "Narr", "Cond", "Cop", "A1sg", "A2sg", "A1pl", "A2pl"}


def _kucuk(s: str) -> str:
    return s.replace("I", "ı").replace("İ", "i").lower()


@lru_cache(maxsize=1)
def _morfoloji():
    logging.getLogger("zemberek").setLevel(logging.WARNING)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from zemberek import TurkishMorphology
        return TurkishMorphology.create_with_defaults()


def _kok_adayi(analiz) -> int | None:
    """Kökün sözlüksel vurgusu ya da özel ad için Sezer; düzenli kökte None."""
    sz = V._sozluk()
    lemma = _kucuk(analiz.item.lemma)
    fiil = str(analiz.item.primary_pos).endswith("Verb") and lemma.endswith(("mak", "mek"))
    anahtar = lemma[:-3] if fiil else lemma
    if anahtar in sz["istisna"]:
        return sz["istisna"][anahtar]
    if "Prop" in str(analiz.item.secondary_pos):
        if anahtar in sz["adlar"] or anahtar in V.LITERATUR_SON or V.SEZERSIZ_SON.search(anahtar) \
                or len(V.heceler(anahtar)) < 2:
            return None                                   # kişi adı, -istan/-hane, tek hece: düzenli
        if anahtar.endswith("iye") and len(V.heceler(anahtar)) >= 3:
            return V._son_unlu_hecesi(anahtar, len(anahtar) - 3)
        return V.sezer(anahtar)
    return None


def analiz_vurgusu(analiz, w: str) -> int | None:
    """Tek çözümleme + yüzey biçimi (küçük harf, kesmesiz) → vurgulu hece; örtüşmezse None."""
    parca, konum = [], 0
    for d in analiz.morpheme_data_list:
        parca.append((konum, d.surface, d.morpheme.id_))
        konum += len(d.surface)
    if konum != len(w) or not parca:
        return None
    bas = V.heceler(w)
    aday: list[int] = []
    k = _kok_adayi(analiz)
    if k is not None:
        aday.append(k)
    gov = parca[0][1]
    if len(gov) >= 2:                                     # sözlükte tek parça duran türemiş gövde
        g = V.vurgulu_hece(gov)
        if g is not None and g < len(V.heceler(gov)) - 1:
            aday.append(g)
    imp = any(i == "Imp" for _, _, i in parca)
    zero = zaman = False
    for p, s, i in parca[1:]:
        if s:
            aor_ardi = any(x[2] == "Aor" and x[0] == p + len(s) for x in parca)
            if i == "Neg" and aor_ardi:
                aday.append(V._hece(bas, p))                              # gelMEZ, yazMAyız (G&K)
            elif i in _ILK:
                aday.append(V._hece(bas, p))                              # geLİyor, yaPArak
            elif i in _ONCESI or (i == "A2pl" and imp):
                aday.append(V._son_unlu_hecesi(w, p))                     # GİTmedik, araBAyla
            elif i in _EKEYLEM and (zero or zaman):
                aday.append(V._son_unlu_hecesi(w, p))                     # yorGUNum, giDERdi, uYUrum
        if i == "Zero":
            zero = True
        if i in _ZAMAN:
            zaman = True
    aday = [a for a in aday if 0 <= a < len(bas)]
    return min(aday) if aday else len(bas) - 1


def cumle_vurgulari(metin: str) -> dict[str, int | None]:
    """Cümle bağlamıyla çözümlenmiş her sözcüğün (küçük harf) vurgulu hecesi; bilinmeyenler yok."""
    sonuc: dict[str, int | None] = {}
    try:
        cozum = _morfoloji().analyze_and_disambiguate(metin).best_analysis()
    except Exception:                                     # noqa: BLE001 — çözümleyici hata verirse kalıplar
        return sonuc
    for a in cozum:
        if a.is_unknown() or "Punc" in str(a.item.primary_pos):
            continue
        w = _kucuk("".join(d.surface for d in a.morpheme_data_list))
        if not w or w in sonuc:
            continue
        if w in V.VURGUSUZ or V._SORU.match(w):
            sonuc[w] = None
            continue
        v = analiz_vurgusu(a, w)
        if v is not None:
            sonuc[w] = v
    return sonuc
