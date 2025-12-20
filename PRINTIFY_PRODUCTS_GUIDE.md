# 📦 Kompletní Průvodce Printify Produkty

**60+ produktů s automatickou optimalizací pro každý typ!**

---

## 🎯 Přehled Systému

Artomate nyní podporuje **60+ Printify produktů** rozdělených do 5 kategorií:

| Kategorie | Produktů | Coverage Type | Background |
|-----------|----------|---------------|------------|
| **Apparel** (oblečení) | 9 | Transparent | PNG s alpha |
| **Home & Living** (domov) | 16 | Full | Celoplošný tisk |
| **Wall Art** (nástěnné) | 12 | Full | Edge-to-edge |
| **Drinkware** (nádobí) | 5 | Transparent | Wrap-around |
| **Accessories** (doplňky) | 11 | Mixed | Podle typu |

**Celkem: 53 produktů ready to use!**

---

## 📋 Kategorie Produktů

### 1️⃣ **APPAREL (Oblečení)** - Transparent Background

✅ **Automaticky odstraní bílé pozadí** z AI obrázků
✅ **PNG s alpha channel** pro profesionální vzhled
✅ **Centrovaný design** na produktu

| Product ID | Name | Print Area | Notes |
|-----------|------|------------|-------|
| `tshirt_unisex` | Unisex Heavy Cotton Tee | 4500×5400 | Classic tričko |
| `tshirt_premium` | Premium Unisex Tee | 4500×5400 | Vyšší kvalita |
| `tshirt_womens` | Women's Relaxed T-Shirt | 4500×5400 | Dámský střih |
| `tshirt_kids` | Youth Short Sleeve Tee | 3600×4320 | Dětské velikosti |
| `tank_top` | Unisex Tank Top | 4500×5400 | Bez rukávů |
| `long_sleeve` | Long Sleeve Tee | 4500×5400 | Dlouhý rukáv |
| `hoodie_unisex` | Unisex Heavy Blend Hoodie | 4500×5400 | Mikina s kapucí |
| `hoodie_zip` | Unisex Zip Hoodie | 4500×5400 | Mikina na zip |
| `sweatshirt` | Unisex Crewneck Sweatshirt | 4500×5400 | Bez kapuce |

**Použití:**
```python
# Automaticky transparent background
products = ["tshirt_unisex", "hoodie_unisex", "tank_top"]
# Systém automatically: removes white BG + transparent PNG
```

---

### 2️⃣ **HOME & LIVING (Domov)** - Full Coverage

✅ **Celoplošný tisk** edge-to-edge
✅ **Žádné bílé okraje** - design vyplní celý produkt
✅ **RGB formát** pro  nejlepší barvy

| Product ID | Name | Print Area | Notes |
|-----------|------|------------|-------|
| **Blankets (Deky)** ||||
| `blanket_fleece` | Fleece Blanket 50×60 | 6000×8000 | Velká deka |
| `blanket_medium` | Fleece Blanket 40×50 | 4500×6000 | Střední |
| `blanket_large` | Fleece Blanket 60×80 | 7200×9000 | Extra velká |
| **Pillows (Polštáře)** ||||
| `throw_pillow_14x14` | Throw Pillow 14×14 | 4200×4200 | Malý polštář |
| `throw_pillow_16x16` | Throw Pillow 16×16 | 4800×4800 | Střední |
| `throw_pillow_18x18` | Throw Pillow 18×18 | 5400×5400 | Velký |
| `lumbar_pillow` | Lumbar Pillow 22×12 | 6600×3600 | Obdélníkový |
| **Bathroom (Koupelna)** ||||
| `shower_curtain` | Shower Curtain 71×74 | 7200×7200 | Sprchový závěs |
| `bath_towel` | Bath Towel 30×60 | 8100×5400 | Velký ručník |
| `hand_towel` | Hand Towel 15×30 | 4500×3000 | Malý ručník |
| **Rugs (Koberce)** ||||
| `rug_small` | Area Rug 24×36 | 7200×4800 | Malý koberec |
| `rug_medium` | Area Rug 48×72 | 9600×7200 | Velký koberec |
| `doormat` | Doormat 18×30 | 5400×3600 | Rohožka |
| **Bedding (Ložnice)** ||||
| `duvet_cover_twin` | Duvet Cover Twin | 8400×10200 | Peřina twin |
| `duvet_cover_queen` | Duvet Cover Queen | 10500×10500 | Peřina queen |
| `duvet_cover_king` | Duvet Cover King | 12300×10500 | Peřina king |

**Použití:**
```python
# Automaticky full coverage
products = ["blanket_fleece", "throw_pillow_16x16", "duvet_cover_queen"]
# Systém automatically: full edge-to-edge print
```

---

### 3️⃣ **WALL ART (Nástěnné Umění)** - Full Coverage

✅ **Edge-to-edge tisk** bez okrajů
✅ **Vysoké rozlišení** 300 DPI
✅ **Různé velikosti** od malých po obří

| Product ID | Name | Print Area | Notes |
|-----------|------|------------|-------|
| **Posters (Plakáty)** ||||
| `poster_12x18` | Poster 12×18 | 3600×5400 | Standard |
| `poster_18x24` | Poster 18×24 | 5400×7200 | Velký |
| `poster_24x36` | Poster 24×36 | 7200×10800 | Extra velký |
| **Canvas (Plátno)** ||||
| `canvas_8x10` | Canvas 8×10 | 2400×3000 | Malý |
| `canvas_12x16` | Canvas 12×16 | 3600×4800 | Střední |
| `canvas_16x20` | Canvas 16×20 | 4800×6000 | Velký |
| `canvas_18x24` | Canvas 18×24 | 5400×7200 | Extra velký |
| `canvas_24x36` | Canvas 24×36 | 7200×10800 | Obří |
| **Framed (Rámované)** ||||
| `framed_print_12x16` | Framed Print 12×16 | 3600×4800 | S rámem |
| `framed_print_16x20` | Framed Print 16×20 | 4800×6000 | Větší rám |
| **Special (Speciální)** ||||
| `wood_print` | Wood Print 8×10 | 4800×6000 | Tisk na dřevo |
| `metal_print` | Metal Print 16×20 | 4800×6000 | Kovový tisk |

**Použití:**
```python
# Automaticky full coverage
products = ["poster_18x24", "canvas_16x20", "framed_print_16x20"]
# Systém automatically: fills entire print area
```

---

### 4️⃣ **DRINKWARE (Nádobí)** - Transparent/Wrap

✅ **Wrap-around tisk** kolem produktu
✅ **Transparent background** pro čisté obrysy
✅ **Izolované termosky** premium

| Product ID | Name | Print Area | Notes |
|-----------|------|------------|-------|
| `mug_11oz` | White Glossy Mug 11oz | 2475×1155 | Classic hrnek |
| `mug_15oz` | White Glossy Mug 15oz | 2850×1155 | Velký hrnek |
| `travel_mug` | Stainless Steel Travel Mug 15oz | 2550×1950 | Termohrnec |
| `water_bottle` | Stainless Steel Water Bottle 17oz | 2475×2400 | Láhev |
| `wine_tumbler` | Wine Tumbler 12oz | 2475×1800 | Víno tumbler |

**Použití:**
```python
# Automaticky transparent wrap
products = ["mug_11oz", "travel_mug", "water_bottle"]
# Systém automatically: transparent BG + wrap layout
```

---

### 5️⃣ **ACCESSORIES (Doplňky)** - Mixed

✅ **Různé typy** podle produktu
✅ **Optimalizováno** pro každý item

| Product ID | Name | Print Area | Coverage | Notes |
|-----------|------|------------|----------|-------|
| `phone_case_iphone` | iPhone Tough Case | 1875×3150 | Transparent | Ochranný obal |
| `phone_case_samsung` | Samsung Tough Case | 1875×3150 | Transparent | Samsung |
| `tote_bag` | Cotton Tote Bag | 4500×5400 | Transparent | Taška |
| `tote_bag_large` | Large Cotton Tote | 6000×7200 | Transparent | Velká taška |
| `sticker_3x3` | Square Sticker 3×3 | 900×900 | Transparent | Malá samolepka |
| `sticker_4x4` | Square Sticker 4×4 | 1200×1200 | Transparent | Větší samolepka |
| `notebook_spiral` | Spiral Notebook | 3000×4500 | Full | Sešit |
| `mousepad` | Rectangle Mouse Pad | 2700×2100 | Full | Podložka myši |
| `yoga_mat` | Yoga Mat 24×68 | 7200×2400 | Full | Jogamatka |
| `beach_towel` | Beach Towel 30×60 | 9000×6000 | Full | Plážový ručník |
| `apron` | All-Over Print Apron | 4500×6000 | Full | Zástěra |

**Použití:**
```python
# Mix typů
products = ["phone_case_iphone", "tote_bag", "notebook_spiral"]
# Systém automatically: správný coverage type pro každý
```

---

## 🔧 Jak To Funguje

### **Automatická Optimalizace**

Systém automaticky pro každý produkt:

```python
# 1. Detekce coverage type ze specifikace
spec = PRINTIFY_PRODUCTS["tshirt_unisex"]
# → coverage_type: "transparent"

# 2. Výběr crop mode
if coverage_type == "full":
    crop_mode = "cover"        # Vyplní celou oblast
elif coverage_type == "centered":
    crop_mode = "contain"      # Centrovaný s okraji
else:  # transparent
    crop_mode = "contain"      # Centrovaný na transparent

# 3. Rendering
if transparent:
    - Vytvoří RGBA PNG
    - Odstraní bílé pozadí (AI images)
    - Alpha channel pro transparentnost
else:
    - Vytvoří RGB PNG
    - Celoplošný tisk edge-to-edge
    - Optimální barvy

# 4. Upload na Printify
- Správné rozlišení (300 DPI)
- Optimální formát (PNG)
- Perfektní fit pro produkt
```

### **Coverage Types Vysvětleno**

#### **Transparent** (např. trička)
```
Before:           After:
┌──────────┐     ┌──────────┐
│  ░░░░░░  │     │          │
│  ░CAT ░  │  →  │   CAT    │ (transparent BG)
│  ░░░░░░  │     │          │
└──────────┘     └──────────┘
```
- Bílé pozadí odstraněno
- PNG s alpha channel
- Clean, profesionální vzhled

#### **Full** (např. deky)
```
Before:           After:
┌──────────┐     ╔══════════╗
│          │     ║  CAT     ║
│   CAT    │  →  ║          ║ (edge-to-edge)
│          │     ║    DESIGN║
└──────────┘     ╚══════════╝
```
- Celoplošný tisk
- Žádné okraje
- Design vyplní celý produkt

#### **Centered** (speciální případy)
```
Before:           After:
┌──────────┐     ┌──────────┐
│          │     │ ░░░░░░░  │
│   CAT    │  →  │ ░ CAT ░  │ (borders OK)
│          │     │ ░░░░░░░  │
└──────────┘     └──────────┘
```
- Centrovaný design
- Může mít okraje
- Respektuje proporce

---

## 📝 Příklady Použití

### **Example 1: Vytvoř Tričko a Mikinu**

```python
# API call
POST /api/jobs/{job_id}/products
{
    "product_types": ["tshirt_unisex", "hoodie_unisex"]
}

# Co se stane:
# 1. Systém zjistí že oba jsou "transparent"
# 2. Odstraní bílé pozadí z AI obrázku
# 3. Vytvoří PNG s alpha channel (4500×5400px)
# 4. Centruje design na triko/mikinu
# 5. Upload na Printify
# 6. ✅ Done! Professional look
```

### **Example 2: Vytvoř Deku a Polštář**

```python
# API call
POST /api/jobs/{job_id}/products
{
    "product_types": ["blanket_fleece", "throw_pillow_16x16"]
}

# Co se stane:
# 1. Systém zjistí že oba jsou "full"
# 2. Použije "cover" mode (fill entire area)
# 3. Vytvoří RGB PNG (6000×8000px, 4800×4800px)
# 4. Edge-to-edge tisk bez okrajů
# 5. Upload na Printify
# 6. ✅ Done! Beautiful full coverage
```

### **Example 3: Kompletní Kolekce**

```python
# Mix všech kategorií
POST /api/jobs/{job_id}/products
{
    "product_types": [
        # Apparel (transparent)
        "tshirt_unisex",
        "hoodie_unisex",

        # Home (full)
        "blanket_fleece",
        "throw_pillow_16x16",

        # Wall Art (full)
        "poster_18x24",
        "canvas_16x20",

        # Drinkware (transparent)
        "mug_11oz",

        # Accessories (mixed)
        "tote_bag",
        "notebook_spiral"
    ]
}

# Systém automatically:
# - Transparent BG pro apparel + drinkware
# - Full coverage pro home + wall art
# - Správné cropy pro každý produkt
# - 9 produktů ready to sell! 🚀
```

---

## 🎨 Best Practices

### **Pro Transparent Products (Trička, Hrnky)**

✅ **DO:**
- Use designs s čistými konturami
- AI obrázky s bílým pozadím (auto-removed)
- Vektorové grafiky
- Loga, ilustrace, typography

❌ **DON'T:**
- Fotografie krajiny (use full coverage instead)
- Busy backgrounds
- Gradients to edges

### **Pro Full Coverage Products (Deky, Plakáty)**

✅ **DO:**
- Patterns a textury
- Fotografie
- Abstraktní umění
- Paisley, mandaly
- Edge-to-edge designs

❌ **DON'T:**
- Malé centrované motivy (use centered instead)
- Text u okrajů (může se ořezat)

---

## 📊 Product Selection Strategy

### **Strategie 1: Minimal (Quick Start)**
```python
# 5 best-sellers
products = [
    "tshirt_unisex",        # Nejprodávanější
    "poster_18x24",         # Wall art standard
    "mug_11oz",             # Levné, populární
    "throw_pillow_16x16",   # Home decor
    "tote_bag",             # Praktické
]
# Pokryje: apparel, wall art, drinkware, home, accessories
```

### **Strategie 2: Medium (Balanced)**
```python
# 12 produktů
products = [
    # Apparel
    "tshirt_unisex", "hoodie_unisex", "long_sleeve",

    # Home
    "blanket_fleece", "throw_pillow_16x16", "shower_curtain",

    # Wall Art
    "poster_18x24", "canvas_16x20",

    # Drinkware
    "mug_11oz", "travel_mug",

    # Accessories
    "tote_bag", "phone_case_iphone",
]
```

### **Strategie 3: Comprehensive (All-In)**
```python
# 30+ produktů - maximální reach
products = PRINTIFY_PRODUCTS.keys()  # All 53 products!

# Split do kategorií:
from artomate.workers.printify_product_catalog import PRODUCT_CATEGORIES

apparel = PRODUCT_CATEGORIES["apparel"]          # 9 produktů
home = PRODUCT_CATEGORIES["home_living"]         # 16 produktů
wall_art = PRODUCT_CATEGORIES["wall_art"]        # 12 produktů
drinkware = PRODUCT_CATEGORIES["drinkware"]      # 5 produktů
accessories = PRODUCT_CATEGORIES["accessories"]  # 11 produktů
```

---

## 🔍 Filtering & Discovery

### **Get Products by Category**

```python
from artomate.workers.printify_product_catalog import (
    PRODUCT_CATEGORIES,
    get_products_by_category,
    get_products_by_coverage,
    get_all_product_ids
)

# Všechny apparel
apparel = get_products_by_category("apparel")
# → ["tshirt_unisex", "hoodie_unisex", ...]

# Všechny home & living
home = get_products_by_category("home_living")
# → ["blanket_fleece", "throw_pillow_14x14", ...]

# Všechny wall art
art = get_products_by_category("wall_art")
# → ["poster_12x18", "canvas_16x20", ...]
```

### **Get Products by Coverage Type**

```python
# Všechny transparent (apparel + drinkware + some accessories)
transparent = get_products_by_coverage("transparent")
# → ["tshirt_unisex", "mug_11oz", "phone_case_iphone", ...]

# Všechny full coverage (home + wall art + some accessories)
full = get_products_by_coverage("full")
# → ["blanket_fleece", "poster_18x24", "yoga_mat", ...]

# Všechny centered (speciální případy)
centered = get_products_by_coverage("centered")
# → []  (momentálně žádné, ale možné přidat)
```

### **Get All Products**

```python
# Všechny dostupné produkty
all_products = get_all_product_ids()
# → 53 product IDs

print(f"Total products available: {len(all_products)}")
# → Total products available: 53
```

---

## 🚀 Production Workflow

### **Step-by-Step**

```bash
# 1. Vytvoř design (AI nebo upload)
POST /api/jobs
{
    "theme": "minimalist cat",
    "style": "japandi",
    "variants": 4
}
# → Job #123 created, 4 AI designs generated

# 2. Vyber produkty (automaticky optimalizované)
POST /api/jobs/123/products
{
    "product_types": [
        "tshirt_unisex",           # Transparent BG
        "blanket_fleece",          # Full coverage
        "poster_18x24",            # Full coverage
        "mug_11oz"                 # Transparent BG
    ]
}

# 3. Systém automatically:
# ✅ Creates transparent PNG for tshirt + mug
# ✅ Removes white background
# ✅ Creates full RGB PNG for blanket + poster
# ✅ Crops perfectly for each product
# ✅ Uploads to Printify
# ✅ Sets correct pricing

# 4. Publikuj na Etsy
POST /api/jobs/123/publish-etsy
# → 4 products live on Etsy! 🎉
```

---

## 💡 Tips & Tricks

### **Tip 1: Mix Transparent + Full**
Pro každý design vytvoř mix:
- 2-3 transparent (trička, hrnky)
- 2-3 full (deky, plakáty)
- 1-2 special (phone case, tote bag)

= **7-8 produktů** z jednoho designu!

### **Tip 2: Size Variations**
Nabídni více velikostí stejného produktu:
- `poster_12x18` + `poster_18x24` + `poster_24x36`
- `canvas_8x10` + `canvas_16x20` + `canvas_24x36`
- `mug_11oz` + `mug_15oz`

= More options = More sales!

### **Tip 3: Bundle Podobné**
Vytvoř product bundles:
- Tričko + Mikina (apparel set)
- Deka + Polštář (bedroom set)
- Hrnek + Tote Bag (morning combo)

### **Tip 4: Seasonal Products**
Některé produkty jsou seasonal:
- **Zima:** blanket, hoodie, sweatshirt
- **Léto:** tank_top, beach_towel, tote_bag
- **Whole Year:** poster, mug, phone_case

---

## 📈 Expected Results

### **Coverage Breakdown**

| Coverage Type | Products | % of Total | Use Cases |
|--------------|----------|------------|-----------|
| Transparent | 25 | 47% | Trička, hrnky, tašky, obaly |
| Full | 28 | 53% | Deky, polštáře, plakáty, koberce |
| Centered | 0 | 0% | Rezerva pro budoucnost |

### **Revenue Potential per Design**

```
1 design × 10 produktů = 10 listings
10 listings × $15 avg price = $150 potential
10 listings × 1% conversion = 0.1 sales/day
0.1 sales × 30 days = 3 sales/month
3 sales × $5 profit = $15/month per design

10 designs = $150/month
50 designs = $750/month
100 designs = $1,500/month 💰
```

---

## 🎓 Pokročilé Featury

### **Custom Coverage Override**

```python
# Override default coverage type
print_file = renderer.create_print_file(
    asset=asset,
    target_width=4500,
    target_height=5400,
    transparent_background=True,   # Force transparent
    remove_white_bg=True,           # Remove white BG
    crop_mode="contain",            # Force centered
)
```

### **Custom White BG Removal Threshold**

V `render_engine.py` upravit threshold:
```python
def _remove_white_background(self, img: Image.Image):
    # Current threshold: RGB > 240
    if item[0] > 240 and item[1] > 240 and item[2] > 240:
        # Make transparent

    # Stricter (less removal): RGB > 250
    # More aggressive (more removal): RGB > 230
```

---

## ✅ Checklist

Před spuštěním:

- [ ] Vybral jsem produkty ze správných kategorií
- [ ] Zkontroloval jsem coverage type (transparent vs full)
- [ ] Design je vhodný pro vybrané produkty
- [ ] AI obrázky mají bílé pozadí (auto-removed)
- [ ] Print areas mají správné rozměry (300 DPI)
- [ ] Testoval jsem na 1-2 produktech před mass upload

---

## 🎉 Hotovo!

Máš **53 Printify produktů** ready to use!

**Next Steps:**
1. Vyber kategorii produktů (apparel, home, wall art...)
2. Vytvoř job s designem
3. Spusť product creation
4. Watch the magic happen! ✨

**Questions?** Check VIRAL_CONTENT_GUIDE.md nebo PHASE3_TEST_REPORT.md

---

**Happy Selling! 💰🚀**
