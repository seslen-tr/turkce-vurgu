# Değişiklikler

## 0.1.1

- var/yok + ek-eylem kökten vurgulanır: VARmış, YOKmuş, VARdır, YOKtu, YOKsa.
- Ad + ek-eylem -mIş vurgu almaz: güZELmiş, çoCUKmuş (eylemden sonra zaman eki olarak kalır: gelMİŞ).
- Cümle ya da yan cümle sonundaki yalın eylem+mA olumsuz emir okunur: acele ETme., KORKma! (yerleşik adlar hariç: dondurMA).
- "harika" ilk heceden: HArika.
- Okunuş sözlüğündeki kök ünlüyle başlayan ekte yumuşasa da sözlükten okunur: evlat → evladım (ince l kalır), t/p/ç → d/b/c.
- Ölçüler: literatür sınavı değişmedi (120 / 123, %97,6); Vikisözlük son hece dışı vurgu %22,5 → %22,6.
- README: örnek çıktısı düzeltildi (`ɟideˈdʒeiz`); kurulum, API ve düzen bölümleri eklendi.

## 0.1.0 — ilk açık sürüm

- İlk yayın. Ayrıntılı ölçümler README'de.
- Bağımlılıksız Türkçe G2P (k/g/l incelmesi, uzun ünlüler, yumuşak g, sayı ve kısaltma okuma, 1.488 sözcüklük okunuş sözlüğü).
- Kaynaklı sözcük vurgusu (en soldaki aday kazanır): sözlüksel kökler (1.203 sözcük), vurgu almayan ve vurgu çeken ekler, olumsuz emir -mA- + -(y)In(Iz), Sezer kuralı.
- İsteğe bağlı turkce-normalize (`[tam]` eki); komut satırı `python -m turkce_vurgu`.
