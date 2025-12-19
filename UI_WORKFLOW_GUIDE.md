# 🎨 Artomate UI & Complete Workflow Guide

Kompletní průvodce pro UI a automatizovaný workflow od Telegramu až po všechny platformy.

---

## 🚀 Spuštění UI

### Varianta 1: Pouze UI

```bash
./start_ui.sh
```

Otevři browser: **http://localhost:8501**

### Varianta 2: Kompletní Stack (API + UI)

```bash
./start_full_stack.sh
```

Otevři:
- **UI**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🎯 Complete Workflow

### Workflow Overview

```
Telegram Input
    ↓
Create Job
    ↓
Generate 12 Monthly Variants (AI)
    ↓
Render for ALL Products (Pillow)
    ↓
Create Printify Products
    ↓
Create Etsy Listings (optional)
    ↓
Instagram Carousel (12 images)
    ↓
Create Reels/Shorts for each variant
    ↓
Submit ALL to Shutterstock
    ↓
Submit ALL to Adobe Stock
    ↓
DONE!
```

---

## 📱 Telegram Workflow

### 1. Setup Telegram Bot

```bash
# Create bot via @BotFather
# Get token: 123456:ABC-DEF...

# Add to .env
TELEGRAM_BOT_TOKEN=your-token
```

### 2. Set Webhook

```bash
# Point bot to your API
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-domain.com/telegram/webhook"}'
```

### 3. Send Message to Bot

```
/create theme: minimalist cat, style: japandi, niche: wall-art, keywords: zen minimal cute
```

### 4. Bot Auto-Creates & Processes

Bot automaticky:
1. ✅ Vytvoří job
2. ✅ Vygeneruje 12 měsíčních variant
3. ✅ Ořeže pro všechny produkty
4. ✅ Vytvoří Printify produkty
5. ✅ Vytvoří Instagram carousel
6. ✅ Vytvoří Reels pro první 3 varianty
7. ✅ Submitne všechny na Shutterstock
8. ✅ Submitne všechny na Adobe Stock

### 5. Check Status

```
/status <job_id>
```

---

## 🎨 UI Workflow

### Tab 1: Create Job

1. **Theme**: Zadej téma (e.g., "minimalist cat")
2. **Style**: Vyber styl (japandi, boho, minimalist...)
3. **Niche**: Vyber kategorii (wall-art, apparel...)
4. **Keywords**: Zadej keywords (každý na řádek)
5. **Variants**: Počet variant (1-12)

**Klikni "Create Job"** → Job ID se zobrazí

### Tab 2: Generate Variants

1. Počet variant: 1-12 (default 12)
2. **Klikni "Generate"**

**Co se stane:**
- Vygeneruje 12 měsíčních variant
- Každá má jiný mood/barvy:
  - Leden: Zimní, chladné tóny
  - Únor: Romantické, červená/růžová
  - Březen: Jarní, pastelové
  - Duben: Živé, květinové
  - Květen: Veselé, žluté/zelené
  - Červen: Slunečné, teplé
  - Červenec: Tropické, tyrkysové
  - Srpen: Plážové, modré
  - Září: Podzimní, oranžové
  - Říjen: Sklizeň, zlaté
  - Listopad: Pochmurné, hluboké barvy
  - Prosinec: Sváteční, červená/zelená/zlatá

**Real-time log** ukazuje progress!

### Tab 3: View Assets

Náhledy všech 12 vygenerovaných variant v galerii 4x3.

### Tab 4: Create Products

1. **Vyber typy produktů**:
   - T-shirt
   - Poster 12x18
   - Poster 18x24
   - Mug
   - Hoodie
   - Canvas 16x20

2. **Klikni "Create All Products"**

**Co se stane:**
- Pro každou ze 12 variant vytvoří vybrané produkty
- Ořeže každý obrázek na správné rozměry pro každý produkt
- Vytvoří Printify produkty s cenami
- Celkem: 12 variant × počet produktů

**Příklad:**
- 12 variant × 2 produkty (tshirt, poster) = **24 produktů**

### Tab 5: Social Media

1. **Vyber platformy**:
   - Instagram Carousel
   - Instagram Reels
   - TikTok
   - YouTube Shorts

2. **Klikni "Publish to Social"**

**Co se stane:**

**Instagram Carousel:**
- 1 post s 10 obrázky (IG limit)
- SEO caption
- 30 hashtags

**Reels/Shorts:**
- Pro první 3 varianty vytvoří videa
- Ken Burns efekt (zoom + pan)
- 5 sekund, 1080x1920
- Caption + hashtags pro každou platformu

**Celkem:** 1 carousel + 3 × 3 videa = **10 social posts**

### Tab 6: Stock Platforms

1. **Vyber platformy**:
   - Shutterstock
   - Adobe Stock

2. **Klikni "Submit to Stock"**

**Co se stane:**
- Každá ze 12 variant → Shutterstock submission
- Každá ze 12 variant → Adobe Stock submission
- Vygeneruje:
  - SEO title
  - Description
  - 50 keywords
  - AI disclosure
  - Category suggestions
- Vytvoří JSON soubory v `exports/stock_outbox/`

**Celkem:** 12 × 2 platformy = **24 submissions**

---

## 📊 Console Log

V UI vidíš real-time log:

```
[12:34:56] [INFO] Creating job: minimalist cat
[12:34:57] [SUCCESS] ✓ Job 5 created successfully
[12:35:00] [INFO] Generating variant 1/12
[12:35:45] [SUCCESS] ✓ Variant 1 generated
[12:35:46] [INFO] Generating variant 2/12
...
[12:42:30] [INFO] Creating tshirt for asset 67
[12:42:35] [SUCCESS] ✓ Created tshirt #89
...
[12:50:00] [SUCCESS] ✓ Created 24 products
[12:50:05] [INFO] Creating Instagram carousel post
[12:50:10] [SUCCESS] ✓ Instagram carousel created
...
[12:55:00] [SUCCESS] ✓ Created 24 stock submissions
[12:55:05] [INFO] Workflow complete
```

Vidíš **každý krok** včetně chyb!

---

## 🔄 Complete Automation

### Telegram → Everything

```bash
# 1. Send to Telegram
/create theme: cat, style: japandi, keywords: zen cute

# 2. Bot replies:
✓ Job 123 created and processing started!

Theme: cat
Style: japandi
Variants: 12
Products: tshirt, poster_18x24

Workflow includes:
• 12 image variants
• 24 products
• Instagram carousel + Reels
• TikTok + YouTube Shorts
• Shutterstock + Adobe Stock

Check status with: /status 123

# 3. Everything runs automatically!
```

**Po 10-15 minutách máš:**
- ✅ 12 obrázků
- ✅ 24+ produktů v Printify
- ✅ 1 Instagram carousel
- ✅ 9+ Reels/Shorts (3 varianty × 3 platformy)
- ✅ 24 stock submissions ready

---

## 📁 Výsledky

### Soubory

```
data/assets/
├── images/
│   ├── job_5_month01_...png
│   ├── job_5_month02_...png
│   └── ... (12 obrázků)
├── videos/
│   ├── reel_5_...mp4
│   └── ... (3 videa)
└── printfiles/
    ├── printfile_5_..._4500x5400.png  # T-shirt
    ├── printfile_5_..._4500x6000.png  # Poster
    └── ... (12 × počet produktů)

exports/stock_outbox/
├── shutterstock_asset_67.json
├── shutterstock_asset_68.json
├── ... (24 submissions)
├── adobe_stock_asset_67.json
└── ...
```

### Database

```sql
SELECT * FROM jobs WHERE id = 5;
-- state: DONE

SELECT COUNT(*) FROM assets WHERE job_id = 5;
-- 12 (images) + 3 (videos) = 15

SELECT COUNT(*) FROM products WHERE job_id = 5;
-- 24 (12 variants × 2 product types)

SELECT COUNT(*) FROM social_posts WHERE job_id = 5;
-- 10 (1 carousel + 9 videos)
```

---

## ⚡ Quick Commands

### Start UI Only
```bash
./start_ui.sh
# → http://localhost:8501
```

### Start Full Stack
```bash
./start_full_stack.sh
# → API: 8000, UI: 8501
```

### Manual Workflow
```python
from artomate.core.workflow_orchestrator import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator()

results = orchestrator.run_complete_workflow(
    job_id=5,
    options={
        "variant_count": 12,
        "product_types": ["tshirt", "poster_18x24"],
        "create_printify": True,
        "create_social": True,
        "submit_stock": True,
    }
)

print(f"✓ Created {len(results['assets'])} assets")
print(f"✓ Created {len(results['products'])} products")
print(f"✓ Created {len(results['social_posts'])} social posts")
```

---

## 🎬 Demo Workflow

### 1. Open UI
```bash
./start_ui.sh
```

### 2. Create Job
- Theme: "mountain landscape"
- Style: "minimalist"
- Niche: "wall-art"
- Variants: 3 (pro rychlý test)

### 3. Generate
- Klikni "Generate"
- Sleduj console log
- Za ~3 minuty máš 3 obrázky

### 4. View Assets
- Tab 3: Vidíš náhledy

### 5. Create Products
- Vyber: tshirt, poster
- Klikni "Create All Products"
- Výsledek: 6 produktů (3 × 2)

### 6. Social
- Vyber: Instagram Carousel
- 1 carousel post s 3 obrázky

---

## 🚨 Troubleshooting

### UI se nespustí
```bash
pip install streamlit
./start_ui.sh
```

### Console log nejde vidět
- Refresh stránku (auto-refresh je každých 0.1s)

### Generování selže
- Zkontroluj `.env`: `OPENAI_API_KEY`
- Zkontroluj konzoli v UI

### Produkty se nevytvoří
- Zkontroluj `PRINTIFY_API_TOKEN`
- Zkontroluj `PRINTIFY_SHOP_ID`

---

## 💡 Pro Tips

1. **Začni s 3 variantami** místo 12 (rychlejší test)
2. **Sleduj console log** - vidíš přesně co se děje
3. **Reset session** v sidebaru vyčistí vše
4. **View Stats** ukáže celkové statistiky
5. **Background processing** - můžeš zavřít tab, běží dál

---

## 📞 Help

- **UI Guide**: Tento soubor
- **API Docs**: http://localhost:8000/docs
- **Testing**: `TESTING_GUIDE.md`
- **Complete docs**: `README.md`

Happy automating! 🚀
