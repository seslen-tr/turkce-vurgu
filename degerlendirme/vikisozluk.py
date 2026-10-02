# -*- coding: utf-8 -*-
"""
VİKİSÖZLÜK ÖLÇÜSÜ — Türkçe sözcüklerin Vikisözlük (İngilizce Wiktionary) IPA'sındaki vurguyla
kuralları karşılaştırır.

Veri: kaikki.org (wiktextract) Türkçe dökümü, CC BY-SA 4.0 — veri/vikisozluk/tr.jsonl
  (https://kaikki.org/dictionary/Turkish/kaikki.org-dictionary-Turkish.jsonl)

Güvenilirlik: Vikisözlük'ün Türkçe okunuş şablonu vurgu belirtilmezse SON heceyi işaretler.
  - son hece DIŞI işaret: editör yazmıştır → güvenilir altın veri
  - son hece işareti: editör de yazmış olabilir, şablonun varsayılanı da → yumuşak veri
Son hece dışı sözcükler sözlüğümüzde (istisna.tsv) olduğundan ölçü 5 katlı çapraz doğrulamadır:
her katta o katın sözcükleri sözlükten çıkarılır, kurallar onları görmeden tahmin eder.
Raporlanan:
  A. son hece dışı (güvenilir): kurallar sözlüksüz kaçını buluyor (genelleme)
  B. son hece işaretli (yumuşak): kurallar kaçında son hece DIŞI diyor (yanlış alarm üst sınırı)

    python degerlendirme/vikisozluk.py
"""
from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
from turkce_vurgu.g2p import _kucuk  # noqa: E402
from turkce_vurgu.vurgu import _sozluk, heceler, vurgulu_hece  # noqa: E402

HARF = re.compile(r"^[a-zçğıöşüâîû]+$")


def ipa_vurgu(ipa: str) -> tuple[int, int] | None:
    """'/ˈan.ka.ɾa/' → (vurgulu hece sırası 0, hece sayısı 3)."""
    s = ipa.strip("/[] ")
    if "ˈ" not in s or " " in s:
        return None
    parca = [p for p in re.split(r"[.ˈ]", s.replace("ˌ", ".")) if p]
    once = s.split("ˈ")[0]
    sira = len([p for p in re.split(r"[.]", once.replace("ˌ", ".")) if p])
    return sira, len(parca)


def altin() -> dict[str, tuple[str, int, int]]:
    """sözcük → (tür, vurgulu hece, hece sayısı); 2+ heceli, tek sözcüklü, hece sayısı tutan maddeler."""
    sonuc = {}
    for satir in open(KOK / "veri" / "vikisozluk" / "tr.jsonl", encoding="utf-8"):
        d = json.loads(satir)
        w = d.get("word", "")
        if " " in w or "-" in w or w in sonuc:
            continue
        for snd in d.get("sounds", []):
            r = ipa_vurgu(snd["ipa"]) if snd.get("ipa") else None
            if r:
                k = _kucuk(w)
                if HARF.match(k) and len(heceler(k)) == r[1] and r[1] > 1:
                    sonuc[w] = ("özel ad" if w[0].isupper() else d.get("pos", "?"), r[0], r[1])
                break
    return sonuc


def main() -> int:
    veri = altin()
    ist = _sozluk()["istisna"]
    sozcukler = sorted(veri)
    random.Random(4).shuffle(sozcukler)
    kat = {w: i % 5 for i, w in enumerate(sozcukler)}
    a_say, a_dogru, b_say, b_alarm = Counter(), Counter(), Counter(), Counter()
    alarm_ornek: list[tuple[str, int]] = []
    for k in range(5):
        cikar = {}
        for w in (w for w in sozcukler if kat[w] == k):
            for anahtar in (_kucuk(w), re.sub(r"m[ae]k$", "", _kucuk(w))):
                if anahtar in ist:
                    cikar[anahtar] = ist.pop(anahtar)
        for w in (w for w in sozcukler if kat[w] == k):
            tur, v, n = veri[w]
            kucuk = _kucuk(w)
            t = vurgulu_hece(kucuk, kucuk if w[0].isupper() else "")
            if v < n - 1:
                a_say[tur] += 1
                a_dogru[tur] += t == v
            else:
                b_say[tur] += 1
                if t is not None and t < n - 1:
                    b_alarm[tur] += 1
                    alarm_ornek.append((w, t))
        ist.update(cikar)
    A, B = sum(a_say.values()), sum(b_say.values())
    print(f"A. son hece DIŞI vurgu (güvenilir, {A} sözcük), sözlükten çıkarılarak: "
          f"kurallar %{100 * sum(a_dogru.values()) / A:.1f}  (hep son hece: %0)")
    for t, n in a_say.most_common(6):
        print(f"     {t:9s} {n:5d}  %{100 * a_dogru[t] / n:.1f}")
    print(f"B. son hece işaretli (yumuşak, {B} sözcük): kurallar %{100 * sum(b_alarm.values()) / B:.1f}'inde "
          f"son hece DIŞI diyor (yanlış alarm üst sınırı)")
    for t, n in b_say.most_common(6):
        print(f"     {t:9s} {n:5d}  %{100 * b_alarm[t] / n:.1f}")
    print("   alarm örnekleri:", alarm_ornek[:20])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
