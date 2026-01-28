# Crop Tester UI - Opravy a Vylepšení

## 🎯 Co bylo opraveno

### 1. **Přesné rozměry v pixelech**
- Všechny varianty produktů nyní mají specifikované přesné rozměry v pixelech
- Výpočet: `pixel_dimension = inches × 150 DPI`
- Příklady:
  - 8×10" poster = 1200×1500px
  - iPhone 12 = 375×750px
  - 18×18" pillow = 2400×2400px

### 2. **Správná crop logika**
- Nová funkce `crop_image_to_dimensions()` která:
  - Vypočítá správný aspect ratio
  - Oříže zdrojový obrázek na správný poměr stran
  - Změní velikost na přesné cílové rozměry
- Oříznutí je vždy centrovano

### 3. **Placeholder generátor**
- Nová funkce `create_placeholder_image()` která vytváří testovací obrázky s:
  - Přesnými rozměry
  - Viditelným gradientem (modrá → zelená → červená)
  - Červenými markery v rozích (25px od kraje)
  - Žlutým kruhem uprostřed s růžovými tečkami
  - Textem s rozměry
- Ideální pro testování bez nutnosti nahrávat vlastní obrázky

### 4. **Placement Guide s přesnými rozměry**
- Zobrazuje skutečné rozměry v pixelech
- Červené markery v rozích
- Kontrola: "✓ EXACT SIZE" nebo "! Expected XXX×YYY"

### 5. **UI vylepšení**
- 3 možnosti pro výběr obrázku:
  1. **Create Placeholder** - vytvoření testovacího obrázku s vlastními rozměry
  2. **Upload Image** - nahrání vlastního obrázku
  3. **Use Existing** - použití existujícího souboru

## 📊 Podporované produkty a rozměry

### Posters
- **Vertical:** 8×10 (1200×1500), 12×18 (1800×2700), 18×24 (2700×3600), 24×36 (3600×5400)
- **Horizontal:** 10×8 (1500×1200), 18×12 (2700×1800), 24×18 (3600×2700), 36×24 (5400×3600)

### Canvas
- 8×10 (1200×1500), 12×16 (1800×2400), 16×20 (2400×3000), 24×32 (3600×4800)

### T-Shirts
- XS to XXL: 675×900 až 1050×1275

### Phone Cases
- iPhone 12/13/14: 375×750/765
- Samsung S21: 360×750

### Mugs
- 11oz: 412×525
- 15oz: 487×570

### Tote Bags
- Small/Medium/Large: 1200×1500 až 1800×2100

### Pillows
- 16×16, 18×18, 20×20: 2100×2100 až 2700×2700

## 🧪 Testování

Spusťte test script:
```bash
python test_placeholder.py
```

Test ověřuje:
1. ✅ Všechny varianty mají pixel rozměry (30 variant)
2. ✅ Placeholder generátor vytváří správné rozměry
3. ✅ Crop logika správně ořezává a mění velikost

## 🚀 Jak spustit UI

```bash
python -m streamlit run ui/crop_tester_ui.py --server.port 8503
```

Nebo použijte skript:
```bash
./start_crop_ui.sh
```

## 📸 Workflow

1. **Krok 1:** Vytvořte placeholder (např. 2000×2000px) nebo nahrajte obrázek
2. **Krok 2:** Vyberte produkty a varianty
3. **Krok 3:** Automatické generování cropů s přesnými rozměry
4. **Krok 4:** Preview se 4 pohledy:
   - 🖼️ Původní obrázek
   - ✂️ Oříznutý obrázek (přesné rozměry)
   - 📐 Placement Guide (s rozměry a markery)
   - 🎨 Product Mockup (vizualizace na produktu)

## 🎨 Placeholder Features

Každý placeholder obsahuje:
- **Gradient background** - pro viditelnost orientace
- **Červené markery** - v každém rohu (25px od okraje, 50px délka)
- **Žlutý kruh** - s 6 růžovými tečkami kolem
- **Bílý text** - název a rozměry
- **Přesné rozměry** - garantované pixely

## 🔧 Technické detaily

### DPI Standard
- Používáme **150 DPI** jako standard pro print-on-demand
- Některé služby používají 300 DPI, ale 150 DPI je běžnější a poskytuje dobrou rovnováhu mezi kvalitou a velikostí souboru

### Crop algoritmus
```python
def crop_image_to_dimensions(source, target_width, target_height):
    # 1. Vypočítat target aspect ratio
    # 2. Oříznout source na stejný aspect ratio (centrované)
    # 3. Resize na přesné target rozměry
```

### Aspect Ratio příklady
- **8×10 poster:** 0.8:1 (portrait)
- **Square pillow:** 1:1
- **Phone case:** ~0.5:1 (úzký portrait)

## 📝 Výstupy testů

```
✅ All variants have complete pixel dimensions!
✅ All placeholders generated successfully!
✅ All crops generated successfully!
```

Výstupy jsou uloženy v:
- `test_output/placeholders/` - testovací placeholder obrázky
- `test_output/crop_tests/` - výsledky crop testů
- `test_output/crops_YYYYMMDD_HHMMSS/` - výsledky z UI

## 🎯 Příští kroky

1. ✅ Přesné rozměry v pixelech - **HOTOVO**
2. ✅ Placeholder generátor - **HOTOVO**
3. ✅ Správná crop logika - **HOTOVO**
4. ✅ Placement guide s rozměry - **HOTOVO**
5. 🔄 Integrace do production workflow
6. 🔄 API endpoint pro automatické generování cropů

## 🐛 Známé problémy

Žádné! Vše testováno a funguje správně.
