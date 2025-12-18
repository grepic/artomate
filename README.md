# Artomate - Content-to-Commerce Automation System

Automatizovaný systém pro generování designů, tvorbu produktů a publikaci na marketplace platformy.

## Architektura

- **Python Backend** (CLI/FastAPI) - Hlavní logika
- **n8n** - Orchestrace, webhooks, scheduling
- **SQLite/PostgreSQL** - Stavová databáze
- **React Dashboard** - Volitelné UI

## Struktur

```
artomate/
├── artomate/              # Python package
│   ├── cli/              # CLI interface (Click)
│   ├── core/             # Core business logic
│   ├── workers/          # Worker modules
│   ├── integrations/     # External APIs
│   ├── db/               # Database models
│   └── utils/            # Helpers
├── n8n/                  # n8n workflows
├── dashboard/            # React app (optional)
├── data/                 # SQLite DB, assets
└── exports/              # XML/CSV/JSON feeds
```

## Rychlý start

### 1. Setup

```bash
# Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database
python -m artomate.cli init-db

# Configure API keys
cp .env.example .env
# Edit .env with your keys
```

### 2. Základní použití (CLI)

```bash
# Vytvořit nový job
artomate create --theme "minimalist cat" --style "japandi" --niche "wall-art"

# Spustit job
artomate run <job-id>

# Zobrazit status
artomate status <job-id>

# Export feedů
artomate export --format xml --output exports/products.xml
artomate export --format csv --output exports/products.csv

# Denní automatický běh
artomate daily-cycle --count 10
```

### 3. FastAPI server (volitelné)

```bash
uvicorn artomate.api.main:app --reload

# API endpoints:
# POST /api/jobs - Create job
# GET /api/jobs/{id} - Get job status
# POST /api/jobs/{id}/run - Run job
# GET /api/export/{format} - Export feeds
```

### 4. n8n orchestrace

```bash
# Import workflows
n8n import:workflow --input=n8n/workflows/telegram-webhook.json
n8n import:workflow --input=n8n/workflows/daily-cron.json
n8n import:workflow --input=n8n/workflows/notifications.json

# Configure webhooks v n8n UI:
# Telegram → http://localhost:8000/webhooks/telegram
# Cron → http://localhost:8000/jobs/daily-cycle
```

## Workflow

### Automatický běh (n8n cron)

```
Každý den 3:00 AM:
n8n → POST /api/jobs/daily-cycle → Python vytvoří 10 jobů
→ Generuje assety → Vytvoří produkty → Publikuje na Etsy
→ n8n pošle notifikaci "10 produktů vytvořeno"
```

### Manuální běh (Telegram)

```
Telegram: "/create cat japandi minimalist"
→ n8n webhook → POST /api/jobs
→ Python vytvoří job
→ n8n pošle "Job created, ID: 123"
→ Python zpracuje
→ n8n pošle "Job 123 done: 3 produkty vytvořeny"
```

## State Machine

```
CREATED → GENERATING → RENDERING → PRINTIFY_UPLOAD
→ PRINTIFY_PRODUCT → ETSY_LISTING → DONE
                                   ↓
                                 FAILED (→ retry)
```

## Funkce

### Fáze 1 (MVP) ✅
- [x] SQLite database
- [x] Image generation (OpenAI DALL-E)
- [x] Pillow crop/resize
- [x] Printify API integration
- [x] CLI interface
- [x] Basic state machine

### Fáze 2 (Orchestrace)
- [ ] n8n webhooks
- [ ] Telegram bot integration
- [ ] Daily cron automation
- [ ] Notifications

### Fáze 3 (Marketplace)
- [ ] Etsy API integration
- [ ] SEO optimization
- [ ] Mockup generation
- [ ] Feed exports (XML/CSV/JSON)

### Fáze 4 (Analytics)
- [ ] Performance tracking
- [ ] React dashboard
- [ ] Manual approval workflow
- [ ] A/B testing

### Fáze 5 (Scale)
- [ ] Multi-provider image gen
- [ ] Social media automation
- [ ] Stock platform submission
- [ ] PostgreSQL migration

## Konfigurace

### .env
```bash
# API Keys
OPENAI_API_KEY=sk-...
STABILITY_API_KEY=sk-...
PRINTIFY_API_KEY=...
ETSY_API_KEY=...
TELEGRAM_BOT_TOKEN=...

# Database
DATABASE_URL=sqlite:///data/artomate.db
# DATABASE_URL=postgresql://user:pass@localhost/artomate

# Storage
ASSETS_DIR=./data/assets
EXPORTS_DIR=./exports

# n8n
N8N_WEBHOOK_URL=http://localhost:5678/webhook/artomate
```

## Příklady

### CLI
```bash
# Jednoduchý run
artomate create --theme "turtle" --style "boho"

# Pokročilé
artomate create \
  --theme "japanese garden" \
  --style "watercolor" \
  --niche "home-decor" \
  --colors "pastel,beige,green" \
  --products "tshirt,poster,mug"

# Export
artomate export --format xml --marketplace etsy
artomate export --format csv --columns "id,title,price,status"

# Statistiky
artomate stats --period 30d
artomate stats --group-by niche
```

### Python API
```python
from artomate.core.job_manager import JobManager
from artomate.core.config import Config

config = Config.from_env()
manager = JobManager(config)

# Create job
job = manager.create_job(
    theme="minimalist cat",
    style="japandi",
    niche="wall-art"
)

# Run
manager.run_job(job.id)

# Check status
status = manager.get_job_status(job.id)
print(status)
```

## Licence

MIT
