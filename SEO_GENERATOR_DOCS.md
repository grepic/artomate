# SEO Text Generator - Dokumentace

## Přehled

ChatGPT API (OpenAI) bylo úspěšně integrováno do Artomate systému pro automatické generování SEO-optimalizovaných textů:

- **Titulky produktů** (optimalizované pro každou platformu)
- **Popisy produktů** (přesvědčivé, SEO-friendly)
- **Tagy/klíčová slova** (relevantní pro vyhledávání)

## Funkce

### ✅ Implementované funkce

1. **AI-Powered SEO Text Generator** (`artomate/workers/seo_text_generator.py`)
   - Generování titulků pro Printify, Etsy, Amazon
   - Generování popisů produktů s optimalizovanou strukturou
   - Generování relevantních tagů/klíčových slov
   - Fallback na pravidlové generování, pokud AI selže

2. **Integrace s PrintifyWorker**
   - Automatické použití AI pro SEO texty při vytváření produktů
   - Volitelné vypnutí: `PrintifyWorker(use_ai_seo=False)`

3. **Integrace s EtsyWorker**
   - Optimalizace pro Etsy specifická SEO pravidla
   - Automatické AI generování při vytváření listingů
   - Volitelné vypnutí: `EtsyWorker(use_ai_seo=False)`

## Konfigurace

### 1. OpenAI API klíč

API klíč je uložen v `.env`:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Model

Systém používá **GPT-4o-mini** pro optimální poměr cena/výkon:
- Rychlý
- Levný
- Dostatečně kvalitní pro SEO texty

## Použití

### Základní použití

```python
from artomate.workers.seo_text_generator import SEOTextGenerator
from artomate.db.models import Job

# Vytvořit job
job = Job(
    theme="Cat Lover",
    style="Minimalist",
    niche="home-decor",
    keywords=["cat art", "modern decor"],
    input_source="manual",
)

# Inicializovat generátor
generator = SEOTextGenerator()

# Generovat titulek
title = generator.generate_product_title(
    job=job,
    product_name="Poster",
    platform="printify",
)

# Generovat popis
description = generator.generate_product_description(
    job=job,
    product_name="Poster",
    platform="printify",
)

# Generovat tagy
tags = generator.generate_product_tags(
    job=job,
    product_name="Poster",
    platform="etsy",
    max_tags=13,
)

# Nebo vše najednou
seo_package = generator.generate_complete_seo_package(
    job=job,
    product_name="Poster",
    platform="etsy",
)
```

### Automatické použití v Workers

SEO generátor se automaticky používá při vytváření produktů:

```python
# PrintifyWorker
from artomate.workers.printify_worker import PrintifyWorker

worker = PrintifyWorker()  # AI SEO enabled by default
product = worker.create_product(job, asset, "poster")

# Vypnout AI SEO
worker = PrintifyWorker(use_ai_seo=False)  # Fallback to template-based
```

```python
# EtsyWorker
from artomate.workers.etsy_worker import EtsyWorker

worker = EtsyWorker()  # AI SEO enabled by default
listing = worker.create_listing_for_product(product, job)

# Vypnout AI SEO
worker = EtsyWorker(use_ai_seo=False)  # Fallback to rule-based
```

## Optimalizace pro platformy

### Printify / Shopify
- **Titulek**: max 80 znaků
- **Popis**: 200-1000 znaků
- **Tagy**: max 15
- **Styl**: Vyvážený SEO a brand appeal

### Etsy
- **Titulek**: max 140 znaků
- **Popis**: Strukturovaný s emoji
- **Tagy**: max 13, každý max 20 znaků
- **Styl**: Zaměřeno na vyhledávání zákazníků

### Amazon
- **Titulek**: max 200 znaků
- **Popis**: Velmi detailní
- **Tagy**: max 50
- **Styl**: Maximální použití znaků, velmi popisný

## Testování

Spusťte testovací skript:

```bash
python test_seo_generator.py
```

Test ověří:
- ✅ OpenAI API klíč
- ✅ Generování titulků (Printify, Etsy)
- ✅ Generování popisů
- ✅ Generování tagů
- ✅ Kompletní SEO balíček

## Příklady výstupů

### Titulek (Printify)
```
Minimalist Cat Art Poster | Modern Animal Print | Perfect Gift for Cat Lovers
```

### Titulek (Etsy)
```
Minimalist Cat Art | Modern Animal Print | Wall Art Print for Cat Lovers | Unique Home Decor Gift
```

### Tagy (Etsy)
```
cat lover canvas, minimalist cat art, animal print decor, modern cat decor, 
home decor gift, cat wall art print, minimalist animal art, pet lover gift, 
canvas print decor, feline wall decor, cat poster art, modern home art, 
unique cat gifts
```

### Popis (ukázka)
```
Transform your space into a sanctuary for cat lovers with our stunning 
Minimalist Cat Lover Poster. This piece of cat art beautifully encapsulates 
the charm and elegance of feline friends, making it a perfect addition to 
any modern decor...

Perfect for:
- Cat lovers wanting to add a touch of personality to their home
- Gift-givers looking for a unique present
- Minimalist decor enthusiasts seeking a statement piece

Features:
- Eye-catching minimalist design
- High-quality printing on premium paper
- Available in multiple sizes
...
```

## Fallback mechanismus

Pokud AI generování selže nebo není k dispozici API klíč:

1. **Titulky**: Template-based (`{theme} | {style} | {niche}`)
2. **Popisy**: Předpřipravený text s placeholdery
3. **Tagy**: Pravidlově generované z job atributů

## Výhody AI SEO

### Před (Template-based)
```
Cat Lover | Minimalist | Art - Poster
```

### Po (AI-powered)
```
Minimalist Cat Art Poster | Modern Animal Print | Perfect Gift for Cat Lovers
```

**Rozdíl**:
- ✅ Přirozenější jazyk
- ✅ Více klíčových slov
- ✅ Lepší CTR (click-through rate)
- ✅ Optimalizované pro platformu
- ✅ Přesvědčivější pro zákazníky

## Náklady

- Model: **GPT-4o-mini**
- Cena za 1M input tokens: ~$0.15
- Cena za 1M output tokens: ~$0.60

**Odhad nákladů na produkt**:
- Titulek: ~100 tokens = $0.00006
- Popis: ~800 tokens = $0.00048
- Tagy: ~300 tokens = $0.00018
- **Celkem: ~$0.00072 per produkt (~0.02 Kč)**

**Pro 1000 produktů**: ~$0.72 (~20 Kč)

## Monitoring

Všechny volání jsou logované:

```python
2025-12-24 19:41:35.220 | INFO | artomate.workers.seo_text_generator:generate_product_title:96 - 
✓ Generated title: Minimalist Cat Art Poster | Modern Animal Print | Perfect Gift for Cat Lovers
```

Fallback warningy:
```python
2025-12-24 19:41:35.220 | WARNING | artomate.workers.printify_worker:generate_title:625 - 
AI title generation failed: <error>, using fallback
```

## Soubory

Nové soubory:
- `artomate/workers/seo_text_generator.py` - Hlavní modul
- `test_seo_generator.py` - Testovací skript

Upravené soubory:
- `artomate/workers/printify_worker.py` - Integrace AI SEO
- `artomate/workers/etsy_worker.py` - Integrace AI SEO
- `.env` - Nový OpenAI API klíč

## Další kroky

### Možná vylepšení:
1. **Caching** - Cachovat podobné requesty
2. **A/B testování** - Porovnat AI vs. template výsledky
3. **Fine-tuning** - Trénovat vlastní model na našich datech
4. **Multi-language** - Generování v různých jazycích
5. **Batch processing** - Generovat více produktů najednou

## Kontakt

Pro dotazy k SEO generátoru:
- Autor: Artomate AI Team
- Datum: 24.12.2025
- Verze: 1.0.0
