# -*- coding: utf-8 -*-
"""Şapkasız yazılan alıntı sözcüklerin okunuşu (g2p okunuş sözlüğüne eklenir).

Bugünkü metinlerin çoğu düzeltme işaretini yazmaz: "hikaye", "dükkan", "rüzgar", "mekan". Kural yalnız şapkalı
yazımda k, g, l'yi inceltir ("hikâye" → hicaːje); şapkasız yazımda "hikaje" okunuyordu. Sözlükte k/g/l'den sonra
â ya da û olan kökler (Vikisözlük) şapkasız yazımlarıyla da okunur. Eşsesliler bağlamsız ayırt edilemez, yazıldığı
gibi kalır: kar / kâr, hala / hâlâ, kanun / kânun, ala / âlâ, hal / hâl, adet / âdet, alem / âlem.

Ek ünlüsü ince olan alıntılarda son l incedir (gol → golü, kalp → kalbi, petrol → petrolü); kural öndeki kalın ünlüye
bakıp ɫ okuyordu. Okunuş sözlüğünde olmayanlar burada.
"""
from __future__ import annotations

import re

#: Şapkalı yazımı sözlükte olup şapkasız yazımı başka bir sözcük olanlar: dokunulmaz.
ESSESLI = set("""kâr kârlı kârsız kârlılık hâlâ âlâ kânun kânunuevel kânunuevvel kânunusani""".split())
#: Batı dillerinden alıntı: şapka yalnız l'yi inceltir, ünlü kısadır (plan → plan, "plaːn" değil); INCE_L'de.
BATI = set("""plân plâj plâk parlâmento""".split())

#: k/g/l'den sonra gelmeyen ama şapkasız yazımı da yaygın, eşsesli olmayan uzun ünlülü sözcükler.
UZUN_UNLULU = """dâhil dâhiliye dâhilen hâlen hâlbuki herhâlde hâlihazırda hâdise âdeta derhâl hattâ inşâ nâhoş
nâmert nâtamam nâmevcut fâni âciz âcizane âbide""".split()

#: l'si ince alıntılar (okunuş sözlüğünde olmayanlar): ek ünlüsü ince olanlar ve Batı alıntıları.
INCE_L = """gol petrol kalp futbol basketbol voleybol hentbol metropol idol protokol misal ihmal iştigal helal meal
mahal usul nüzul mol hol istikbal ishal plan plaj plak parlamento""".split()

_SAPKASIZ = str.maketrans("âîû", "aiu")
_HARIC = ESSESLI | BATI


def ek_okunuslar(kokler, sozcuk, oz=None) -> dict[str, str]:
    """Okunuş sözlüğüne eklenecek {yazım: IPA}. kokler: sözlük kökleri; sozcuk: g2p'nin kural okuyucusu (_sozcuk);
    oz: okunuş sözlüğü (şapkalı yazımın Vikisözlük kaydı varsa o alınır: dükkân → dyccan)."""
    oz = oz or {}
    ek: dict[str, str] = {}
    sapkali = [k for k in kokler if re.search("[kgl][âû]", k) and k not in _HARIC] + UZUN_UNLULU
    for k in sapkali:
        # "hâl"in l'si incedir: herhâlde, derhâl, hâlbuki (kural â'dan sonra ɫ okur)
        ek.setdefault(k.translate(_SAPKASIZ), (oz.get(k) or sozcuk(k)).replace("haːɫ", "haːl"))
    for k in INCE_L:
        ek[k] = sozcuk(k).replace("ɫ", "l")
    return ek
