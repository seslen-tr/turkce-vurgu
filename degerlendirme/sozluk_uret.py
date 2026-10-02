# -*- coding: utf-8 -*-
"""
SÖZLÜK ÜRETİMİ — Vikisözlük'ten (kaikki.org / wiktextract dökümü, CC BY-SA 4.0) veri dosyaları:

  turkce_vurgu/veri/istisna.tsv   sözlüksel vurgulu kökler: sözcük, vurgulu hece, tür
      YALNIZ son hece DIŞI işaretler alınır. Vikisözlük'ün Türkçe okunuş şablonu vurgu
      belirtilmezse son heceyi kendiliğinden işaretler; son hece dışı bir işaret ise
      editörün elle yazdığı bilgidir (ör. ˈan.ka.ɾa). Eylemlerde anahtar gövdedir
      (gelivermek → geliver), çekimli biçimler de vurguyu gövdeden alır.
  turkce_vurgu/veri/adlar.txt     Türkçe kişi adları (son hece vurgusu; Sezer uygulanmaz)
  turkce_vurgu/veri/kokler.txt    özel ad olmayan madde başları ve eylem gövdeleri — bir ekin
      gerçekten ek olup olmadığını sınamak için (güzel+ce: "güzel" kök → -CA eki)
  turkce_vurgu/veri/fiiller.txt   eylem gövdeleri (gel, oku, geliver) — olumsuzluk -mA- ve geniş
      zaman denetimi için
  turkce_vurgu/veri/ozel.txt      özel ad madde başları (Sezer kuralı yalnız özel adlara)

Bu dosyalar CC BY-SA 4.0'tır (Vikisözlük'ten türetilmiş); paketin kodu MIT.

    python degerlendirme/sozluk_uret.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
sys.path.insert(0, str(KOK / "degerlendirme"))
from turkce_vurgu.g2p import _kucuk  # noqa: E402
from turkce_vurgu.vurgu import heceler  # noqa: E402
from vikisozluk import HARF, ipa_vurgu  # noqa: E402

HEDEF = KOK / "turkce_vurgu" / "veri"
_AD = re.compile(r"Turkish (male|female|unisex) given names")


def main() -> int:
    istisna, adlar, kokler, fiiller, ozel = {}, set(), set(), set(), set()
    for satir in open(KOK / "veri" / "vikisozluk" / "tr.jsonl", encoding="utf-8"):
        d = json.loads(satir)
        w = d.get("word", "")
        if " " in w or "-" in w:
            continue
        kucuk = _kucuk(w)
        if not HARF.match(kucuk):
            continue
        anlam = d.get("senses", [])
        if anlam and all(s.get("form_of") or "form-of" in s.get("tags", []) for s in anlam):
            continue                                            # çekimli biçim maddesi
        tur = d.get("pos", "?")
        kat = " ".join((c.get("name", "") if isinstance(c, dict) else str(c)) for s in anlam for c in s.get("categories", []))
        if _AD.search(kat):
            adlar.add(kucuk)
        anahtar = kucuk
        if tur == "verb" and re.search(r"m[ae]k$", kucuk) and len(kucuk) > 4:
            anahtar = kucuk[:-3]
        if w[0].isupper():
            ozel.add(kucuk)
        else:
            kokler.add(anahtar)
        if anahtar != kucuk:
            fiiller.add(anahtar)
        for snd in d.get("sounds", []):
            r = ipa_vurgu(snd["ipa"]) if snd.get("ipa") else None
            if not r:
                continue
            n = len(heceler(kucuk))
            if r[1] == n and r[0] < n - 1:
                # eylemde vurgu gövdede olmalı (mastar eki -mAk son hece). Düzenli türemiş eylemlerde
                # (kır+ıl, it+ele, normal+leş) Vikisözlük'ün işareti emir biçiminden geliyor ve
                # literatürle çelişiyor (kırılacakLAR, G&K 30); yalnız birleşik eylemler alınır
                # (affet, kaybol, vazgeç, öngör, geliver).
                if anahtar != kucuk and (r[0] >= len(heceler(anahtar)) or
                                         re.search(r"(l[ae]|l[ae]ş|[ıiuü]l|[dt][ıiuü]r|[ae]bil|yin|dim)$", anahtar)):
                    break
                istisna.setdefault(anahtar, (r[0], "ozel" if w[0].isupper() else tur))
            break
    HEDEF.mkdir(parents=True, exist_ok=True)
    (HEDEF / "istisna.tsv").write_text(
        "# Vikisözlük (kaikki.org), CC BY-SA 4.0 — sözcük<TAB>vurgulu hece (0'dan)<TAB>tür\n"
        + "\n".join(f"{k}\t{v}\t{t}" for k, (v, t) in sorted(istisna.items())) + "\n", encoding="utf-8")
    (HEDEF / "adlar.txt").write_text("# Vikisözlük Türkçe kişi adları, CC BY-SA 4.0\n" + "\n".join(sorted(adlar)) + "\n",
                                     encoding="utf-8")
    (HEDEF / "kokler.txt").write_text("# Vikisözlük özel ad olmayan madde başları ve eylem gövdeleri, CC BY-SA 4.0\n"
                                      + "\n".join(sorted(kokler)) + "\n", encoding="utf-8")
    (HEDEF / "fiiller.txt").write_text("# Vikisözlük eylem gövdeleri, CC BY-SA 4.0\n" + "\n".join(sorted(fiiller)) + "\n",
                                       encoding="utf-8")
    (HEDEF / "ozel.txt").write_text("# Vikisözlük özel ad madde başları, CC BY-SA 4.0\n" + "\n".join(sorted(ozel)) + "\n",
                                    encoding="utf-8")
    print(f"istisna {len(istisna)}, kişi adı {len(adlar)}, kök {len(kokler)}, eylem {len(fiiller)}, özel ad {len(ozel)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
