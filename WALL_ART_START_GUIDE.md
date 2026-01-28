"""
QUICK START GUIDE - Wall Art Posters
=====================================

Začneme s NEJJEDNODUŠŠÍ kategorií - plakáty.

## PROČ POSTERS?
- ✅ Full coverage (žádné transparentní pozadí)
- ✅ Jednoduché cropping (jen resize)
- ✅ Perfektní pro kalendář
- ✅ Vysoká marže

## KROK 1: Připrav si 12 obrázků kalendáře

Ulož je do složky, např.: `calendar_images/`
- january.png
- february.png
- march.png
... atd.

## KROK 2: Test crop pro JEDEN produkt

```bash
# Nejdřív otestuj na 1 obrázku
artomate test-crop calendar_images/january.png --product poster_matte_vertical --preview
```

To ukáže:
- Jaké velikosti se vygenerují
- Náhled každého cropu
- Čeká na tvoje OK

## KROK 3: Když vypadá dobře, vygeneruj všechny

```bash
artomate crop-product-batch \
  --images calendar_images/*.png \
  --product poster_matte_vertical \
  --output crops/posters
```

## KROK 4: Nahraj na Printify

```bash
artomate upload-to-printify \
  --crops crops/posters \
  --blueprint-id 282 \
  --provider-id 99
```

## PRODUKTY PRO START:

1. **Matte Vertical Posters** (blueprint 282)
   - Velikosti: 8x10, 10x10, 11x14, 12x16, 12x18, 16x20, 18x24, 24x36
   - Provider: Printify Choice (99)
   
2. **Canvas Print** (blueprint 184) 
   - Velikosti: 8x8, 10x10, 12x12, 8x10, 12x16, 16x16, 16x20, 18x24, 24x36
   - Provider: Printify Choice (99)

3. **Framed Poster** (blueprint 492/540)
   - Velikosti: 10x10, 12x16, 16x20, 18x24
   - Provider: Printify Choice (99)

## TIPS:

- Začni s JEDNÍM produktem (poster)
- Test na 1-2 obrázcích nejdřív
- Zkontroluj preview před hromadným generováním
- Pak postupně přidávej další produkty (canvas, framed)
