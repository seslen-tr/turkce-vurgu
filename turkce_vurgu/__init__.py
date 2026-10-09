# -*- coding: utf-8 -*-
"""Türkçe vurgu: metin → vurgu işaretli IPA okunuş (ses sentezi için), espeak'siz.

    from turkce_vurgu import g2p
    g2p("Ankara'ya gitmedik.", vurgu=True)   # 'ˈankaɾaja ˈɟitmedic.'
"""
from .g2p import SEMBOLLER, g2p, normallestir, ozel_kokler, sozcuk_okunusu
from .vurgu import heceler, isaretle, sezer, vurgulu_hece

__all__ = ["g2p", "normallestir", "ozel_kokler", "sozcuk_okunusu", "SEMBOLLER",
           "heceler", "isaretle", "sezer", "vurgulu_hece"]
__version__ = "0.1.1"
