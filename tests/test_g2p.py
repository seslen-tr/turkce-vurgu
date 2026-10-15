# -*- coding: utf-8 -*-
"""python -m unittest discover tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from turkce_vurgu.g2p import SEMBOLLER, g2p, normallestir  # noqa: E402


class G2P(unittest.TestCase):
    def test_temel(self):
        self.assertEqual(g2p("çiçek"), "tʃitʃec")
        self.assertEqual(g2p("şeker"), "ʃeceɾ")
        self.assertEqual(g2p("ılık"), "ɯɫɯk")

    def test_incelme(self):
        self.assertEqual(g2p("kol"), "koɫ")
        self.assertEqual(g2p("göl"), "ɟøl")
        self.assertEqual(g2p("kâr"), "caːɾ")
        self.assertEqual(g2p("ilk"), "ilc")

    def test_yumusak_g(self):
        self.assertEqual(g2p("dağ"), "daː")
        self.assertEqual(g2p("ağaç"), "aatʃ")
        self.assertEqual(g2p("değil"), "deil")

    def test_sayi_ve_kisaltma(self):
        self.assertEqual(normallestir("347 kayıt"), "üç yüz kırk yedi kayıt")
        self.assertEqual(normallestir("%12,5"), "yüzde on iki virgül beş")
        self.assertEqual(normallestir("1.250 km"), "bin iki yüz elli kilometre")
        self.assertEqual(normallestir("İSTANBUL"), "istanbul")

    def test_noktalama(self):
        self.assertEqual(g2p("Dikkat! Emin misin?"), "dickat! emin misin?")
        self.assertEqual(g2p("Evet - hayır"), "evet, hajɯɾ")

    def test_okunus_sozlugu(self):                        # Vikisözlük: uzun ünlü, kural dışı ince l
        self.assertEqual(g2p("nadir"), "naːdiɾ")
        self.assertEqual(g2p("metal"), "metal")
        self.assertEqual(g2p("kilometrelerce"), "cilometɾeleɾdʒe")
        self.assertEqual(g2p("gitmedik"), "ɟitmedic")         # sözlük kuralların inceliğini bozmaz
        self.assertEqual(g2p("evladım"), "evladɯm")           # yumuşayan kök de sözlükten: ince l kalır
        self.assertEqual(g2p("evlat"), "evlat")

    def test_semboller_kapali(self):
        metin = "Sapanca bölgesinde üç yüz kırk yedi abone kaydı buldum; Serdivan'daki arıza giderildi!"
        self.assertTrue(set(g2p(metin)) <= set(SEMBOLLER), set(g2p(metin)) - set(SEMBOLLER))


if __name__ == "__main__":
    unittest.main()
