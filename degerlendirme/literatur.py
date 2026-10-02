# -*- coding: utf-8 -*-
"""
LİTERATÜR SINAVI — tests/literatur.tsv'deki kaynaklı örneklerde kuralların doğruluğu.

    python degerlendirme/literatur.py          # özet + yanlışlar
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
from turkce_vurgu.g2p import _kucuk  # noqa: E402
from turkce_vurgu.vurgu import heceler, isaretle, vurgulu_hece  # noqa: E402

BUYUK_UNLU = set("AEIİOÖUÜÂÎÛ")


def ornekler() -> list[dict]:
    """Her satır: sözcük (küçük), beklenen hece, tür, kaynak, özel kök."""
    sonuc = []
    for s in (KOK / "tests" / "literatur.tsv").read_text(encoding="utf-8").splitlines():
        if not s or s.startswith("#"):
            continue
        p = s.split("\t")
        ornek, tur, kaynak = p[0], p[1], p[2]
        kok = p[3] if len(p) > 3 else ""
        w = _kucuk(ornek)
        i = next(j for j, c in enumerate(ornek) if c in BUYUK_UNLU)
        beklenen = max(k for k, b in enumerate(heceler(w)) if b <= i)
        sonuc.append({"w": w, "beklenen": beklenen, "tur": tur, "kaynak": kaynak, "kok": kok, "ornek": ornek})
    return sonuc


def main() -> int:
    say, dogru, yanlis = Counter(), Counter(), []
    for o in ornekler():
        t = vurgulu_hece(o["w"], o["kok"])
        say[o["tur"]] += 1
        if t == o["beklenen"]:
            dogru[o["tur"]] += 1
        else:
            yanlis.append(o | {"tahmin": isaretle(o["w"], o["kok"])})
    for tur in ("kural", "sezer", "sozluk", "belirsiz"):
        if say[tur]:
            print(f"{tur:9s} {dogru[tur]:3d} / {say[tur]:3d}  %{100 * dogru[tur] / say[tur]:.0f}")
    olcu = [t for t in ("kural", "sezer") if say[t]]
    print(f"KURAL + SEZER: {sum(dogru[t] for t in olcu)} / {sum(say[t] for t in olcu)}  "
          f"%{100 * sum(dogru[t] for t in olcu) / sum(say[t] for t in olcu):.1f}")
    for o in yanlis:
        if o["tur"] != "belirsiz":
            print(f"  ✗ {o['tur']:7s} {o['ornek']:22s} tahmin {o['tahmin']:22s} ({o['kaynak']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
