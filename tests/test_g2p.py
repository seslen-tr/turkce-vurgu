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

    def test_tire_ve_bicim_isaretleri(self):
        self.assertEqual(normallestir("Ar-Ge birimi", tam=False), "ar ge birimi")            # sözcük içi tire
        self.assertEqual(normallestir("Ankara — başkent — büyük.", tam=False), "ankara, başkent, büyük.")
        self.assertEqual(normallestir("<!-- not --> # Başlık **kalın**", tam=False), "başlık kalın")
        self.assertEqual(normallestir("göster · katman", tam=False), "göster, katman")
        self.assertEqual(normallestir("LibriVox ve Wikipedia", tam=False), "librivoks ve vikipedia")

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


class EkZinciri(unittest.TestCase):
    """18.11.2026: kökten sonrası baştan sona ek olmalı; "hata"+"yda", "kilis"+"ede", "gala"+"tasaray" ek sayılıyordu."""

    def test_sahte_kok_eslesmez(self):
        self.assertEqual(g2p("Hatay'da", vurgu=True), "ˈhatajda")          # önceden "hataːjda"
        self.assertEqual(g2p("kilisede", vurgu=True), "ciˈlisede")         # önceden "ˈcilisede"
        self.assertNotIn("ˈɡa", g2p("Galatasaray", vurgu=True))            # önceden "ˈɡalatasaɾaj"
        self.assertNotIn("ː", g2p("Adapazarı gazino animasyon", vurgu=False))

    def test_gercek_ekler_kalir(self):
        from turkce_vurgu.vurgu import _ek_zinciri
        for ek in ("", "da", "yla", "lerimizde", "nın", "daki", "lılaşarak", "sız", "cık"):
            self.assertTrue(_ek_zinciri(ek), ek)
        for ek in ("yda", "tasaray", "no", "masyon"):       # sıra denetlenmez: "azarı" (a+z+ar+ı) geçer
            self.assertFalse(_ek_zinciri(ek), ek)


class OzelAd(unittest.TestCase):
    """18.11.2026: büyük harfli sıradan sözcük özel ad vurgusu alıyordu ("Bugün Pazar" → "ˈpazar")."""

    def test_buyuk_harfli_siradan_sozcuk(self):
        from turkce_vurgu.g2p import ozel_kokler
        self.assertEqual(ozel_kokler("Bugün Pazar. Büyük Millet Meclisi toplandı."), set())
        self.assertEqual(ozel_kokler("Dünya Sağlık Örgütü'nde çalışıyor."), set())
        self.assertEqual(ozel_kokler("Mısır'a gittik, Kanada'ya döndük."), {"mısır", "kanada"})
        self.assertEqual(ozel_kokler("Rusya ile anlaştılar."), {"rusya"})          # cümle başı, sözlükte değil
        self.assertIn("van", ozel_kokler("Dün Van Gölü'ne gittik."))

    def test_sıradan_il_adi(self):
        self.assertEqual(g2p("ordusu", vurgu=True), "oɾduˈsu")
        self.assertEqual(g2p("Ordu'da doğdu.", vurgu=True), "ˈoɾduda doːˈdu.")


if __name__ == "__main__":
    unittest.main()
