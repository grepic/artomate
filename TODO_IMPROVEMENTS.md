# TODO - Co chybí a co dodělat 🚧

## 🔴 Kritické (bez toho to není production ready)

### 1. **Centrální Logging System**
**Status:** ⚠️ Částečně - má loguru, ale není komplexní
**Co chybí:**
- Strukturovaný logger s různými výstupy (console, soubor, remote)
- Log rotation (automatické archivování starých logů)
- Correlation IDs pro sledování jednoho jobu napříč všemi workery
- Různé log levels pro různé prostředí (dev=DEBUG, prod=INFO)

**Příklad co by mělo být:**
```python
# artomate/utils/logger.py
from loguru import logger
import sys

def setup_logging(config):
    """Setup centralized logging with rotation and formatting."""
    logger.remove()  # Remove default handler

    # Console output
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=config.log_level,
        colorize=True,
    )

    # File output with rotation
    logger.add(
        config.log_file,
        rotation="100 MB",  # Rotate when file reaches 100MB
        retention="30 days",  # Keep logs for 30 days
        compression="zip",  # Compress rotated files
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
    )

    # Error file (separate file for errors)
    logger.add(
        config.log_file.parent / "errors.log",
        rotation="50 MB",
        retention="90 days",
        level="ERROR",
    )
```

**Kde použít:**
- V `artomate/__init__.py` při startu aplikace
- V každém workeru přidat context: `logger.bind(job_id=job.id)`

---

### 2. **Error Handling & Retry Mechanismus**
**Status:** ❌ Chybí kompletně
**Co chybí:**
- Try/catch bloky ve všech workers
- Automatický retry pro API volání (OpenAI, Printify, Etsy)
- Exponential backoff (2s → 4s → 8s → 16s)
- Dead letter queue pro permanently failed joby

**Příklad retry decorator:**
```python
# artomate/utils/retry.py
import time
from functools import wraps
from loguru import logger

def retry_with_backoff(max_retries=3, base_delay=2, backoff=2.0, exceptions=(Exception,)):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {e}")
                        raise

                    delay = base_delay * (backoff ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator
```

**Použití:**
```python
# V image_generator.py
@retry_with_backoff(max_retries=3, exceptions=(openai.APIError,))
def _call_openai_api(self, prompt):
    response = self.client.images.generate(...)
    return response
```

---

### 3. **Config Validation**
**Status:** ⚠️ Částečně - má config.py, ale nevaliduje při startu
**Co chybí:**
- Kontrola že OPENAI_API_KEY existuje před generováním
- Kontrola že PRINTIFY_API_TOKEN existuje před vytvářením produktů
- Funkce `validate_for_workflow()` která zkontroluje co je potřeba

**Příklad:**
```python
# V artomate/core/config.py
class Config(BaseSettings):
    # ... existing code ...

    def validate_for_image_generation(self):
        """Validate config for image generation."""
        if not self.openai_api_key and self.default_image_provider == "openai":
            raise ValueError("OPENAI_API_KEY is required for image generation")
        if not self.stability_api_key and self.default_image_provider == "stability":
            raise ValueError("STABILITY_API_KEY is required for image generation")

    def validate_for_printify(self):
        """Validate config for Printify integration."""
        if not self.printify_api_token:
            raise ValueError("PRINTIFY_API_TOKEN is required")
        if not self.printify_shop_id:
            raise ValueError("PRINTIFY_SHOP_ID is required")

    def validate_complete_workflow(self):
        """Validate all required settings for complete workflow."""
        self.validate_for_image_generation()
        self.validate_for_printify()
        # ... další validace
```

---

### 4. **Database Migrations (Alembic)**
**Status:** ❌ Chybí kompletně
**Co chybí:**
- Alembic setup pro správu DB schématu
- Migration historie
- Možnost rollback změn

**Co udělat:**
```bash
# Install
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "initial schema"

# Run migrations
alembic upgrade head
```

**Proč je to důležité:**
- Když změníš `models.py`, potřebuješ migrovat existující DB
- Bez toho ztratíš data při změnách schématu

---

### 5. **Unit Tests**
**Status:** ❌ Žádné testy (jen prázdný `tests/__init__.py`)
**Co chybí:**
- Testy pro každý worker
- Testy pro state machine transitions
- Integration testy pro API endpoints
- Mock testy (bez volání real API)

**Co vytvořit:**
```
tests/
├── unit/
│   ├── test_state_machine.py
│   ├── test_job_manager.py
│   ├── test_image_generator.py
│   ├── test_render_engine.py
│   └── test_config.py
├── integration/
│   ├── test_printify_worker.py
│   ├── test_etsy_worker.py
│   └── test_workflow_orchestrator.py
├── api/
│   ├── test_jobs_routes.py
│   ├── test_products_routes.py
│   └── test_telegram_routes.py
└── conftest.py  # Pytest fixtures
```

**Příklad testu:**
```python
# tests/unit/test_state_machine.py
import pytest
from artomate.core.state_machine import StateMachine, JobState

def test_valid_transition():
    sm = StateMachine()
    assert sm.can_transition(JobState.CREATED, JobState.GENERATING)

def test_invalid_transition():
    sm = StateMachine()
    assert not sm.can_transition(JobState.DONE, JobState.CREATED)

def test_transition_history():
    sm = StateMachine()
    history = []
    sm.transition(
        JobState.CREATED,
        JobState.GENERATING,
        on_success=lambda old, new: history.append((old, new))
    )
    assert len(history) == 1
```

---

## 🟡 Vysoká priorita (vylepší stabilitu)

### 6. **Job Queue System (Celery nebo RQ)**
**Status:** ❌ Chybí
**Co chybí:**
- Background job processing
- Možnost zpracovat 100 jobů paralelně
- Job scheduling (spustit job každý den v 3:00)

**Doporučení: Redis Queue (RQ)** - jednodušší než Celery
```python
# artomate/workers/queue.py
from redis import Redis
from rq import Queue

redis_conn = Redis(host='localhost', port=6379)
job_queue = Queue('artomate', connection=redis_conn)

# Použití
from artomate.core.workflow_orchestrator import WorkflowOrchestrator

def run_workflow_background(job_id):
    orchestrator = WorkflowOrchestrator()
    return orchestrator.run_complete_workflow(job_id)

# Enqueue job
job_queue.enqueue(run_workflow_background, job_id=1)
```

**Worker proces:**
```bash
rq worker artomate
```

---

### 7. **Webhook Notifications (Discord/Slack)**
**Status:** ❌ Chybí
**Co přidat:**
- Notifikace když job skončí (SUCCESS/FAILED)
- Notifikace když vznikne chyba
- Dashboard URL v notifikaci

**Příklad:**
```python
# artomate/integrations/webhook_notifier.py
import requests
from loguru import logger

class WebhookNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def notify_job_complete(self, job, results):
        """Send notification when job completes."""
        message = {
            "content": f"✅ Job #{job.id} complete!",
            "embeds": [{
                "title": f"{job.theme} - {job.style}",
                "color": 0x00ff00,  # Green
                "fields": [
                    {"name": "Assets", "value": str(len(results['assets'])), "inline": True},
                    {"name": "Products", "value": str(len(results['products'])), "inline": True},
                    {"name": "Duration", "value": "5m 32s", "inline": True},
                ],
                "url": f"http://localhost:8501?job_id={job.id}"
            }]
        }
        requests.post(self.webhook_url, json=message)

    def notify_job_failed(self, job, error):
        """Send notification when job fails."""
        message = {
            "content": f"❌ Job #{job.id} failed!",
            "embeds": [{
                "title": f"{job.theme} - {job.style}",
                "color": 0xff0000,  # Red
                "description": f"Error: {error}",
            }]
        }
        requests.post(self.webhook_url, json=message)
```

---

### 8. **Health Check Endpoint**
**Status:** ⚠️ Existuje `routes/health.py`, ale není komplexní
**Co přidat:**
- Kontrola DB konektivity
- Kontrola dostupnosti API klíčů
- Kontrola disk space
- Kontrola Redis (pokud bude queue)

**Vylepšený health check:**
```python
# artomate/api/routes/health.py
from fastapi import APIRouter
from sqlalchemy import text
from artomate.db.database import get_db
from artomate.core.config import get_config

router = APIRouter()

@router.get("/health")
async def health_check():
    """Comprehensive health check."""
    config = get_config()
    checks = {
        "status": "healthy",
        "database": "unknown",
        "storage": "unknown",
        "openai_api": "unknown",
        "printify_api": "unknown",
    }

    # DB check
    try:
        with get_db().session_scope() as session:
            session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"
        checks["status"] = "unhealthy"

    # Storage check
    try:
        if config.assets_dir.exists() and config.assets_dir.is_dir():
            checks["storage"] = "ok"
        else:
            checks["storage"] = "missing"
    except Exception as e:
        checks["storage"] = f"error: {e}"

    # API keys check
    checks["openai_api"] = "configured" if config.openai_api_key else "missing"
    checks["printify_api"] = "configured" if config.printify_api_token else "missing"

    return checks
```

---

### 9. **Monitoring & Metrics**
**Status:** ❌ Chybí
**Co přidat:**
- Prometheus metrics endpoint
- Sledování: job success rate, avg duration, error count
- Grafana dashboard

**Příklad metrics:**
```python
# artomate/utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
jobs_created = Counter('artomate_jobs_created_total', 'Total jobs created')
jobs_completed = Counter('artomate_jobs_completed_total', 'Total jobs completed', ['status'])
job_duration = Histogram('artomate_job_duration_seconds', 'Job duration')
active_jobs = Gauge('artomate_active_jobs', 'Currently active jobs')

# Use in workflow_orchestrator.py
jobs_created.inc()
with job_duration.time():
    results = self.run_complete_workflow(job_id)
jobs_completed.labels(status='success').inc()
```

---

## 🟢 Nice to have (užitečné features)

### 10. **Docker Setup**
**Status:** ❌ Chybí
**Co vytvořit:**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Install package
RUN pip install -e .

CMD ["uvicorn", "artomate.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./exports:/app/exports
    depends_on:
      - db
      - redis

  ui:
    build: .
    command: streamlit run ui/streamlit_app.py --server.port=8501
    ports:
      - "8501:8501"
    env_file:
      - .env
    volumes:
      - ./data:/app/data

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: artomate
      POSTGRES_USER: artomate
      POSTGRES_PASSWORD: artomate
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

### 11. **Template System**
**Status:** ❌ Chybí
**Co by to bylo:**
- Předpřipravené styly/témata
- User může vybrat "Minimalist Cat Template" místo psaní promptu
- Šablony s optimalizovanými klíčovými slovy

**Struktura:**
```python
# artomate/templates/templates.py
TEMPLATES = {
    "minimalist_cat": {
        "theme": "cat",
        "style": "minimalist",
        "keywords": ["zen", "calm", "simple", "line art"],
        "prompt_template": "minimalist line art of a {animal}, zen aesthetic, simple shapes, black and white",
        "niche": "home decor",
        "target_audience": "millennials, home decorators",
        "price_range": {"min": 15.99, "max": 29.99},
    },
    "boho_florals": {
        "theme": "flowers",
        "style": "boho",
        "keywords": ["boho", "bohemian", "earthy", "natural"],
        "prompt_template": "bohemian floral arrangement, earthy tones, watercolor style",
        "niche": "fashion, lifestyle",
    },
}
```

**Použití v CLI:**
```bash
python -m artomate.cli.main create-from-template minimalist_cat
```

---

### 12. **Batch Processing (CSV import)**
**Status:** ❌ Chybí
**Co by to bylo:**
- Upload CSV se 100 řádky (každý řádek = 1 job)
- Automaticky vytvoří 100 jobů a zpracuje
- Progress tracking pro celý batch

**CSV format:**
```csv
theme,style,keywords,niche
cat,minimalist,zen calm simple,home-decor
dog,boho,earthy natural,lifestyle
flower,japandi,wabi-sabi minimalist,wellness
```

**Implementace:**
```python
# artomate/workers/batch_processor.py
import csv
from pathlib import Path

class BatchProcessor:
    def process_csv(self, csv_path: Path):
        """Process batch of jobs from CSV."""
        jobs = []

        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                job = self.job_manager.create_job(
                    theme=row['theme'],
                    style=row['style'],
                    keywords=row['keywords'].split(),
                    niche=row.get('niche'),
                )
                jobs.append(job)

        # Enqueue all jobs
        for job in jobs:
            job_queue.enqueue(run_workflow_background, job.id)

        return jobs
```

---

### 13. **Analytics Dashboard**
**Status:** ❌ Chybí (existuje `/api/analytics` endpoint, ale není UI)
**Co přidat:**
- Graf: Jobs per day
- Graf: Success rate %
- Graf: Avg duration per state
- Top performing themes/styles
- Revenue estimation

**Přidat do Streamlit UI novou záložku:**
```python
# V ui/streamlit_app.py
tab7 = st.tabs(["...", "...", "Analytics"])

with tab7:
    st.header("📊 Analytics")

    # Get analytics data
    response = requests.get("http://localhost:8000/api/analytics")
    analytics = response.json()

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Jobs", analytics['total_jobs'])
    col2.metric("Success Rate", f"{analytics['success_rate']}%")
    col3.metric("Avg Duration", analytics['avg_duration'])
    col4.metric("Total Revenue", f"${analytics['estimated_revenue']}")

    # Charts
    st.line_chart(analytics['jobs_per_day'])
    st.bar_chart(analytics['top_themes'])
```

---

### 14. **N8N Workflows**
**Status:** ⚠️ Dokumentace existuje, ale nejsou hotové workflows
**Co dodělat:**
- Vytvořit export `.json` workflows pro n8n
- Workflow: "Daily Trend Automation"
- Workflow: "Telegram Bot Integration"
- Workflow: "Error Notifications"

**Vytvořit složku:**
```
n8n_workflows/
├── daily_automation.json
├── telegram_integration.json
├── error_alerts.json
└── README.md
```

---

### 15. **Image Upscaling**
**Status:** ❌ Chybí
**Co by to bylo:**
- AI upscale obrázků na vyšší rozlišení
- Použít Real-ESRGAN nebo similar
- Pro lepší kvalitu na velkých produktech (canvas, postery)

**Knihovna:**
```bash
pip install realesrgan
```

**Použití:**
```python
# artomate/workers/upscaler.py
from realesrgan import RealESRGAN

class ImageUpscaler:
    def upscale(self, image_path, scale=2):
        """Upscale image 2x or 4x."""
        model = RealESRGAN(scale=scale)
        upscaled = model.predict(image_path)
        return upscaled
```

---

### 16. **Multi-language Support**
**Status:** ❌ Chybí
**Co by to bylo:**
- České popisy produktů pro český Etsy
- Automatický překlad pomocí OpenAI
- Konfigurace: `LANGUAGE=cs` nebo `LANGUAGE=en`

---

### 17. **A/B Testing**
**Status:** ❌ Chybí (je v config jako `enable_ab_testing=False`)
**Co by to bylo:**
- Vytvoří 2 varianty Etsy listingu (různé titulky, ceny, tagy)
- Sleduje která má lepší conversion rate
- Automaticky vybere vítěze

---

### 18. **Automatic Pricing Optimization**
**Status:** ❌ Chybí
**Co by to bylo:**
- Scrape konkurenční ceny na Etsy
- Automaticky nastav optimální cenu
- Dynamická úprava podle poptávky

---

## 📝 Doporučení prioritizace

### Fáze 1: **Production Ready** (1-2 týdny)
1. ✅ Centrální logging system
2. ✅ Error handling + retry mechanismus
3. ✅ Config validation
4. ✅ Database migrations (Alembic)
5. ✅ Basic unit tests

### Fáze 2: **Stability & Scale** (1 týden)
6. ✅ Job queue (RQ nebo Celery)
7. ✅ Webhook notifications
8. ✅ Comprehensive health check
9. ✅ Docker setup

### Fáze 3: **Advanced Features** (2-3 týdny)
10. ✅ Monitoring & metrics
11. ✅ Template system
12. ✅ Batch processing
13. ✅ Analytics dashboard
14. ✅ N8N workflows hotové

### Fáze 4: **Nice to Have** (ongoing)
15. Image upscaling
16. Multi-language
17. A/B testing
18. Pricing optimization

---

## 🎯 Co dodělat jako první?

**Moje doporučení - začni s:**

1. **Logging** - budeš ho potřebovat hned pro debugging
2. **Error handling** - bez toho se to bude crashovat
3. **Config validation** - ušetří to hodiny debugování "proč to nefunguje"
4. **Testy** - aspoň basic testy pro state machine a job manager

**Chceš, abych něco z toho začal implementovat?** Řekni mi číslo nebo název funkce a půjdeme na to! 🚀
