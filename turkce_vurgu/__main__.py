# -*- coding: utf-8 -*-
"""python -m turkce_vurgu "Ankara'ya gitmedik."  → vurgulu IPA okunuş"""
import sys

from .g2p import g2p

for metin in sys.argv[1:] or ["Merhaba! Şimdi Serdivan'daki haritayı açıyorum."]:
    print(g2p(metin, vurgu=True))
