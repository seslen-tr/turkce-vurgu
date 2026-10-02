# -*- coding: utf-8 -*-
"""python -m unittest discover -s tests — Türkçe sözcük vurgusu (vurgu.py).

Beklentiler kaynaklıdır (I&O = Inkelas & Orgun 2003, Ink = Inkelas 1999, G&K = Göksel & Kerslake 2005).
Toplu ölçü: tests/literatur.tsv (degerlendirme/literatur.py).
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "degerlendirme"))
from turkce_vurgu.g2p import SEMBOLLER, g2p, ozel_kokler  # noqa: E402
from turkce_vurgu.vurgu import heceler, isaretle, sezer, vurgulu_hece  # noqa: E402


class Hece(unittest.TestCase):
    def test_hece(self):
        self.assertEqual(heceler("ankara"), [0, 2, 4])          # an-ka-ra
        self.assertEqual(heceler("türkçe"), [0, 4])             # türk-çe
        self.assertEqual(heceler("saat"), [0, 2])               # sa-at


class Vurgu(unittest.TestCase):
    def test_varsayilan_son_hece(self):                        # I&O 140; G&K
        for w, b in [("kitaplar", "kitapˈlar"), ("kitaplardan", "kitaplarˈdan"), ("bırakacak", "bırakaˈcak"),
                     ("gelmek", "gelˈmek"), ("gel", "ˈgel")]:
            self.assertEqual(isaretle(w), b)

    def test_vurgu_almayan_ekler(self):                        # Ink ex.61–62, 70; G&K 32–34
        for w, b in [("gitmedik", "ˈgitmedik"), ("okumayacak", "oˈkumayacak"), ("gelmeyince", "ˈgelmeyince"),
                     ("arabayla", "araˈbayla"), ("güzelce", "güˈzelce"), ("okuyacaktır", "okuyaˈcaktır"),
                     ("oturken", "oˈturken"), ("okuldaymışlar", "okulˈdaymışlar"), ("öğrenciyim", "öğrenˈciyim")]:
            self.assertEqual(isaretle(w), b)

    def test_vurgu_ceken_ekler(self):                          # Ink ex.54, 61; G&K
        for w, b in [("geliyor", "geˈliyor"), ("yaparak", "yaˈparak"), ("gelince", "geˈlince"),
                     ("tutuver", "tuˈtuver"), ("bakmaksızın", "bakˈmaksızın")]:
            self.assertEqual(isaretle(w), b)

    def test_olumsuz_genis_zaman_vurgulanir(self):             # G&K: bakMAZdık, yazMAyız
        self.assertEqual(isaretle("gelmez"), "gelˈmez")
        self.assertEqual(isaretle("bakmazdık"), "bakˈmazdık")
        self.assertEqual(isaretle("yazmayız"), "yazˈmayız")

    def test_en_soldaki_kazanir(self):                         # Ink ex.69–71
        self.assertEqual(isaretle("bırakmıyor"), "bıˈrakmıyor")
        self.assertEqual(isaretle("gelmesin"), "ˈgelmesin")

    def test_sozluksel_kok(self):                              # Ink ex.64; G&K
        for w, b in [("tarhanada", "tarˈhanada"), ("lokantaya", "loˈkantaya"), ("şimdi", "ˈşimdi"),
                     ("orada", "ˈorada")]:
            self.assertEqual(isaretle(w), b)

    def test_karisan_bicimler(self):
        self.assertEqual(isaretle("elmasa"), "elmaˈsa")         # elmas+a (yönelme), elma+sa değil
        self.assertEqual(isaretle("gelmeli"), "gelmeˈli")       # -mAlI gereklilik, olumsuz değil
        self.assertEqual(isaretle("düşünce"), "düşünˈce")       # ad, -IncE değil

    def test_sezer(self):                                      # Sezer 1981; I&O 143
        self.assertEqual(sezer("ankara"), 0)
        self.assertEqual(sezer("istanbul"), 1)
        self.assertEqual(sezer("adana"), 1)
        self.assertEqual(isaretle("hindistan", "hindistan"), "hindisˈtan")      # -istan Sezer'siz (I&O 149)
        self.assertEqual(isaretle("ahmete", "ahmet"), "ahmeˈte")              # kişi adı düzenli (G&K)

    def test_vurgusuz_sozcuk(self):                            # G&K
        for w in ("mi", "misiniz", "de", "ki", "bile"):
            self.assertIsNone(vurgulu_hece(w))

    def test_ozel_ad_metinde(self):
        self.assertEqual(ozel_kokler("Şimdi Serdivan'daki Zeynep geldi."), {"serdivan", "zeynep"})
        self.assertEqual(g2p("Ankara'ya gitmedik.", vurgu=True), "ˈankaɾaja ˈɟitmedic.")

    def test_vurgusuz_varsayilan(self):
        self.assertEqual(g2p("Şimdi geliyorum."), "ʃimdi ɟelijoɾum.")      # vurgu isteğe bağlı

    def test_semboller(self):
        m = "Sapanca'da üç yüz kırk yedi abone kaydı buldum; Serdivan'daki arıza giderilmedi mi?"
        self.assertTrue(set(g2p(m, vurgu=True)) <= set(SEMBOLLER))


class Literatur(unittest.TestCase):
    """tests/literatur.tsv: kaynaklı örneklerin toplu ölçüsü (gerilemeyi yakalar)."""

    def test_literatur(self):
        from literatur import ornekler
        sonuc = {}
        for o in ornekler():
            sonuc.setdefault(o["tur"], []).append(vurgulu_hece(o["w"], o["kok"]) == o["beklenen"])
        self.assertEqual(sum(sonuc["kural"]), len(sonuc["kural"]))
        self.assertEqual(sum(sonuc["sozluk"]), len(sonuc["sozluk"]))
        # 3 yabancı ad (santaMOnika, monTAna, papaDOpulos) Sezer'in kendi tanımına da uymuyor
        self.assertGreaterEqual(sum(sonuc["sezer"]), len(sonuc["sezer"]) - 3)


if __name__ == "__main__":
    unittest.main()
