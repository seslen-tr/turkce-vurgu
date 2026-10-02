# -*- coding: utf-8 -*-
"""Tam sayıların Türkçe okunuşu: 347 → ["üç", "yüz", "kırk", "yedi"]."""
from __future__ import annotations

_BIR = ["", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
_ON = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]


def okunus(n: int) -> list[str]:
    """Tam sayının Türkçe okunuşu (sözcük listesi)."""
    if n == 0:
        return ["sıfır"]
    out: list[str] = []
    for bolen, ad in ((10 ** 9, "milyar"), (10 ** 6, "milyon"), (1000, "bin")):
        if n >= bolen:
            k, n = divmod(n, bolen)
            out += ([] if (k == 1 and ad == "bin") else okunus(k)) + [ad]
    if n >= 100:
        k, n = divmod(n, 100)
        out += ([] if k == 1 else [_BIR[k]]) + ["yüz"]
    if n >= 10:
        out.append(_ON[n // 10])
        n %= 10
    if n:
        out.append(_BIR[n])
    return out
