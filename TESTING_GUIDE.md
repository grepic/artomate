# 🧪 Artomate Testing Guide

Kompletní průvodce testováním všech funkcí systému - od základních po pokročilé.

---

## ⚡ Quick Start (2 minuty, bez API klíčů)

```bash
# 1. Zkontroluj instalaci
artomate --version

# 2. Vytvoř testovací job
artomate create --theme "mountain" --style "minimalist" --niche "wall-art"

# 3. Zobraz statistiky
artomate stats

# 4. Test trend analyzeru
python3 -c "
from artomate.workers.trend_analyzer import TrendAnalyzer
analyzer = TrendAnalyzer()
trends = analyzer.get_trending_themes(limit=3)
for t in trends:
    print(f'{t[\"theme\"]} - {t[\"style\"]} (score: {t.get(\"trend_score\", 0)})')
"

# 5. Test render engine
python3 -c "
from artomate.workers.render_engine import RenderEngine
from PIL import Image
import tempfile

# Create test image
img = Image.new('RGB', (1024, 1024), 'blue')
path = tempfile.mktemp(suffix='.png')
img.save(path)

# Render
renderer = RenderEngine()
result = renderer.render_image(path, 4500, 5400, mode='cover')
print(f'✓ Rendered: {result.size}')
"
```

**✅ Co funguje bez API klíčů:**
- CLI commands (create, stats)
- Database operations
- Trend analyzer
- Render engine (Pillow)
- Feed export
- State machine

---

## 🎨 Level 1: Image Generation (vyžaduje OpenAI API)

### Setup

```bash
# Přidej do .env
OPENAI_API_KEY=sk-...

# Nebo exportuj
export OPENAI_API_KEY=sk-...
```

### Test

```bash
# Python test
python3 << 'EOF'
from artomate.core.job_manager import JobManager
from artomate.workers.image_generator import ImageGenerator

# Create job
manager = JobManager()
job = manager.create_job(
    theme="minimalist cat",
    style="japandi",
    niche="wall-art"
)

# Generate image
generator = ImageGenerator()
assets = generator.generate_for_job(job, count=1)

print(f"✓ Generated {len(assets)} asset(s)")
print(f"  Path: {assets[0].storage_path}")
print(f"  Size: {assets[0].width}x{assets[0].height}")
EOF
```

**Očekávaný výsledek:**
```
✓ Generated 1 asset(s)
  Path: data/assets/images/job_5_20251218_120000_0_0.png
  Size: 1024x1024
```

**Cena:** ~$0.08 za 1024x1024 HD obrázek

---

## 🏭 Level 2: Printify Integration (vyžaduje Printify API)

### Setup

```bash
# Přidej do .env
PRINTIFY_API_TOKEN=your-token
PRINTIFY_SHOP_ID=12345
```

### Test Connection

```python
from artomate.integrations.printify_client import PrintifyClient

client = PrintifyClient()

# Test connection
shops = client.get_shops()
print(f"✓ Connected to {len(shops)} shop(s)")

# Get catalog
catalog = client.get_catalog()
print(f"✓ Found {len(catalog)} blueprints")
```

### Test Product Creation

```python
from artomate.workers.printify_worker import PrintifyWorker

# Assuming you have job and asset from Level 1
printify = PrintifyWorker()

products = printify.create_product_for_job(
    job=job,
    asset=asset,
    product_types=["tshirt"]  # Start with just 1
)

print(f"✓ Created {len(products)} product(s)")
print(f"  Printify ID: {products[0].printify_product_id}")
print(f"  Price: ${products[0].selling_price}")
```

**Poznámka:** Tohle vytvoří SKUTEČNÝ produkt v Printify (draft mode).

---

## 🛍️ Level 3: Etsy Integration (vyžaduje Etsy API)

### Setup

```bash
# Přidej do .env
ETSY_API_KEY=your-key
ETSY_SHOP_ID=12345678
# ETSY_ACCESS_TOKEN=...  # Pro OAuth (advanced)
```

### Test (READ-ONLY)

```python
from artomate.integrations.etsy_client import EtsyClient

client = EtsyClient()

# Get shop info (READ-ONLY, no auth needed)
try:
    shop = client.get_shop()
    print(f"✓ Connected to shop: {shop.get('shop_name')}")
except Exception as e:
    print(f"Note: Full Etsy access requires OAuth")
```

### Test Listing Creation (vyžaduje OAuth)

```python
from artomate.workers.etsy_worker import EtsyWorker

# Requires OAuth access token
etsy = EtsyWorker()

listing = etsy.create_listing_for_product(
    product=product,
    job=job,
    images=[asset]
)

print(f"✓ Created listing: {listing.listing_url}")
```

**Poznámka:** Etsy vyžaduje OAuth2 pro write operace. Pro testování doporučuji začít bez Etsy.

---

## 📹 Level 4: Video Generation (vyžaduje FFmpeg)

### Setup

```bash
# Install FFmpeg
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg

# Verify
ffmpeg -version
```

### Test

```python
from artomate.workers.video_generator import VideoGenerator

# Assuming you have job and asset
video_gen = VideoGenerator()

video = video_gen.create_reel(
    job=job,
    assets=[asset],
    duration=5,
    style="ken_burns",  # or: slideshow, zoom, pan
    add_text=False
)

print(f"✓ Created video: {video.storage_path}")
print(f"  Duration: 5s")
print(f"  Format: 1080x1920 (9:16)")
print(f"  Size: {video.file_size_bytes / 1024 / 1024:.1f} MB")
```

**Očekávaný výsledek:**
```
✓ Created video: data/assets/videos/reel_5_20251218_120000.mp4
  Duration: 5s
  Format: 1080x1920 (9:16)
  Size: 2.3 MB
```

---

## 📱 Level 5: Social Media (placeholder)

```python
from artomate.workers.social_media_publisher import SocialMediaPublisher
from artomate.db.models import SocialPlatform

social = SocialMediaPublisher()

post = social.create_post(
    job=job,
    platform=SocialPlatform.INSTAGRAM,
    video_asset=video
)

print(f"✓ Created Instagram post draft")
print(f"  Caption: {post.caption[:50]}...")
print(f"  Hashtags: {len(post.hashtags)}")
print(f"  Status: {post.status}")  # "draft" - manual posting
```

**Poznámka:** Automatické postování vyžaduje business účty + OAuth. Pro MVP je post uložený jako draft.

---

## 📊 Level 6: Export Feeds

```python
from artomate.workers.feed_exporter import export_products, export_listings

# Export products as XML
xml_path = export_products(format="xml")
print(f"✓ Exported XML: {xml_path}")

# Export as CSV
csv_path = export_products(format="csv", niche="wall-art")
print(f"✓ Exported CSV: {csv_path}")

# Export as JSON
json_path = export_products(format="json")
print(f"✓ Exported JSON: {json_path}")
```

**Očekávaný výsledek:**
```
✓ Exported XML: exports/products_20251218_120000.xml
✓ Exported CSV: exports/products_20251218_120001.csv
✓ Exported JSON: exports/products_20251218_120002.json
```

---

## 🌐 Level 7: REST API

### Setup

```bash
# Install FastAPI + uvicorn
pip install fastapi uvicorn[standard]
```

### Start Server

```bash
# Development
uvicorn artomate.api.main:app --reload

# Production
uvicorn artomate.api.main:app --host 0.0.0.0 --port 8000
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Create job
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "ocean waves",
    "style": "minimalist",
    "niche": "wall-art"
  }'

# Get stats
curl http://localhost:8000/api/analytics/stats
```

### OpenAPI Docs

Otevři browser: **http://localhost:8000/docs**

Interaktivní API dokumentace s možností testovat všechny endpointy!

---

## 🚀 Complete End-to-End Test

Kompletní workflow od A do Z (vyžaduje: OpenAI API key):

```python
from artomate.core.job_manager import JobManager
from artomate.workers.image_generator import ImageGenerator
from artomate.workers.render_engine import RenderEngine
from artomate.workers.feed_exporter import export_products
from artomate.workers.trend_analyzer import TrendAnalyzer

print("🚀 Complete E2E Test\n")

# 1. Trend Analysis
print("1. Analyzing trends...")
analyzer = TrendAnalyzer()
trending = analyzer.get_trending_themes(limit=1)[0]
print(f"   ✓ Top trend: {trending['theme']}")

# 2. Create Job
print("\n2. Creating job...")
manager = JobManager()
job = manager.create_job(
    theme=trending['theme'],
    style=trending['style'],
    niche=trending['niches'][0],
    keywords=trending['keywords']
)
print(f"   ✓ Job {job.id} created")

# 3. Generate Image
print("\n3. Generating image with DALL-E...")
generator = ImageGenerator()
assets = generator.generate_for_job(job, count=1)
print(f"   ✓ Generated asset {assets[0].id}")

# 4. Render Print Files
print("\n4. Rendering print files...")
renderer = RenderEngine()
print_file = renderer.create_print_file(
    asset=assets[0],
    target_width=4500,
    target_height=5400,
    crop_mode="cover"
)
print(f"   ✓ Created print file {print_file.id}")

# 5. Export Feed
print("\n5. Exporting feed...")
feed_path = export_products(format="json")
print(f"   ✓ Exported to {feed_path}")

print("\n✅ E2E Test Complete!")
print(f"\nResults:")
print(f"  - Job: {job.id}")
print(f"  - Asset: {assets[0].storage_path}")
print(f"  - Print file: {print_file.storage_path}")
print(f"  - Feed: {feed_path}")
```

---

## 🐛 Troubleshooting

### "OpenAI API error"
- Zkontroluj API key v `.env`
- Ověř, že máš kredity na účtu
- Zkontroluj rate limiting

### "Printify API error 401"
- Zkontroluj `PRINTIFY_API_TOKEN`
- Ověř `PRINTIFY_SHOP_ID`
- Token musí mít správná oprávnění

### "FFmpeg not found"
```bash
# Install FFmpeg
sudo apt-get install ffmpeg  # Linux
brew install ffmpeg          # macOS
```

### Database errors
```bash
# Reset database
artomate reset-db
```

### Import errors
```bash
# Reinstall package
pip install -e .
```

---

## 📋 Test Checklist

Použij tento checklist k ověření všech funkcí:

### Core (bez API klíčů)
- [ ] `artomate --version` funguje
- [ ] `artomate create` vytvoří job
- [ ] `artomate stats` zobrazí statistiky
- [ ] Trend analyzer vrací trendy
- [ ] Render engine renderuje obrázky
- [ ] Feed export vytvoří XML/CSV/JSON

### Image Generation (OpenAI API)
- [ ] Image generator vytvoří obrázek
- [ ] Asset se uloží do databáze
- [ ] Soubor existuje v `data/assets/images/`

### Printify (Printify API)
- [ ] Printify client se připojí
- [ ] Product worker vytvoří produkt
- [ ] Pricing je správně vypočítaný
- [ ] Print file je vyrendero vaný

### Etsy (Etsy API + OAuth)
- [ ] Etsy client se připojí (read-only)
- [ ] Listing worker vytvoří listing (s OAuth)
- [ ] SEO tags jsou optimalizované

### Video (FFmpeg)
- [ ] Video generator vytvoří MP4
- [ ] Video má správný formát (9:16)
- [ ] Všechny 4 styly fungují

### Social Media
- [ ] Post draft se vytvoří
- [ ] Caption je generovaný
- [ ] Hashtags jsou optimalizované

### REST API (FastAPI)
- [ ] Server se spustí
- [ ] `/health` vrací status
- [ ] `/docs` zobrazí OpenAPI
- [ ] `/api/jobs` vytvoří job

---

## 🎯 Doporučené Testování

### Začátečník (bez kredencialů)
1. Install: `pip install -e .`
2. Test CLI: `artomate stats`
3. Test trends: Spusť trend analyzer
4. Test render: Vyrendruj test image

### Středně pokročilý (s OpenAI API)
1. Vše výše +
2. Nastav `OPENAI_API_KEY`
3. Vygeneruj 1-2 obrázky
4. Vyrendruj print files
5. Exportuj feed

### Pokročilý (s Printify)
1. Vše výše +
2. Nastav Printify credentials
3. Vytvoř 1 testovací produkt
4. Zkontroluj v Printify dashboardu
5. Smaž testovací produkt

### Expert (kompletní stack)
1. Vše výše +
2. Install FFmpeg
3. Vygeneruj video
4. Nastav Etsy OAuth (optional)
5. Spusť E2E test
6. Deploy REST API

---

## 💡 Tips

1. **Začni malé**: První test bez API klíčů
2. **Testuj postupně**: Přidávej API klíče po jednom
3. **Používej logs**: `tail -f logs/artomate.log`
4. **Kontroluj DB**: `sqlite3 data/artomate.db`
5. **Backup**: Před velkými testy zálohuj DB

---

## 📞 Potřebuješ pomoc?

Pokud něco nefunguje:
1. Zkontroluj logs: `logs/artomate.log`
2. Ověř `.env` konfiguraci
3. Zkus reset: `artomate reset-db`
4. Reinstall: `pip install -e . --force-reinstall`

Happy testing! 🚀
