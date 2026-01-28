# Crop Tester UI - Step-by-Step Workflow

## Co je to?

**Crop Tester UI** je interaktivní webová aplikace pro testování ořezávání obrázků pro produkty a jejich varianty. Funguje jako klikačka **krok za krokem** - žádný terminál, žádné příkazové řádky.

```
Step 1: Select Image → Step 2: Select Products → Step 3: Generate → Step 4: Preview
```

## Spuštění

```bash
# Spuštění z root adresáře projektu
./start_crop_ui.sh

# Nebo přímo přes streamlit
streamlit run ui/crop_tester_ui.py
```

Otevře se v prohlížeči: **http://localhost:8501**

## Jak to funguje? 🎯

### 📸 **Krok 1: Select Test Image**

- **Upload nový obrázek** - Drag & drop nebo klikni na upload
- **Nebo vyber ze stávajících** - test_images/ directory

Jakmile zvolíš obrázek, vidíš:
- Preview obrázku
- Informace (velikost, formát)
- Tlačítko "Continue to Product Selection"

### 🏷️ **Krok 2: Select Products & Variants**

Vybírej produkty:

- **Skip** - Přeskočit produkt
- **Test All Variants** - Vyzkoušet všechny varianty
- **Select Specific Variants** - Zvolit konkrétní varianty

Vidíš:
- Počet dostupných variant
- Default size produktu
- Live preview výběru
- Celkový počet variantů k vygenerování

### ⚙️ **Krok 3: Generating Crops**

Automaticky se generují všechny crops:
- Progress bar v reálném čase
- Log všech akcí
- Automaticky se přejde na preview

### 👀 **Krok 4: Preview Crops**

Vidíš všechny vygenerované crops:
- Seskupeny po produktech
- Preview obrázků
- Výsledné velikosti
- Statistika (produkty, varianty, úspěšnost)

## Workflow Diagram

```
START
  ↓
┌─────────────────────┐
│ Upload Test Image   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Select Products &   │
│ Variants            │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Generate Crops      │
│ (Automatic)         │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Preview Results     │
│ & Download          │
└──────────┬──────────┘
           ↓
      Generate New?
         YES ← NO → END
         ↓
    (Back to Step 2)
```

## Features

✅ **Intuitivní UI** - Žádné příkazy, jen klikání
✅ **Step-by-Step** - Jasné vedení procesem
✅ **Real-time Preview** - Vidíš co se generuje
✅ **Batch Processing** - Všechny varianty najednou
✅ **Error Handling** - Jasné error zprávy
✅ **Progress Tracking** - Přehled pokroku
✅ **Export Crops** - Uložené v test_output/ adresáři

## Output

Crops se ukládají do:

```
test_output/crops_YYYYMMDD_HHMMSS/
├── product_family_variant_1.png
├── product_family_variant_2.png
├── product_family_variant_3.png
└── ...
```

## Tips & Tricks

📌 **Pro rychlé testování:**
1. Použij existující test image z test_images/
2. Na Krok 2 vyber "Test All Variants" u jednoho produktu
3. Vylepšit můžeš později

📌 **Pro detailní test:**
1. Upload vlastní obrázek
2. Ručně vyber specifické varianty
3. Zkontroluj results krok za krokem

📌 **Troubleshooting:**
- Aplikace běží na `localhost:8501`
- Logy vidíš v Kroku 3
- Crops se mají uložit v `/test_output/crops_*`

## Navigace

- ✅ **Continue** - Jdi na další krok
- ⬅️ **Back** - Vrať se o krok zpět
- 🔄 **Generate New** - Vyprázdni a začni znovu

## Sidebar

Vlevo vidíš:
- 📍 **Progress** - Kde jsi v procesu
- ℹ️ **Help** - Nápověda k jednotlivým krokům

---

**Hotovo! Teď si to můžeš vyzkoušet.** 🚀
