# Artomate Quickstart Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.10+
- pip or uv
- API keys (OpenAI, Printify)

## Installation

### 1. Clone & Setup

```bash
cd /home/user/artomate

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your API keys
nano .env  # or vim, code, etc.
```

**Required API keys:**
- `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys
- `PRINTIFY_API_TOKEN` - Get from Printify dashboard
- `PRINTIFY_SHOP_ID` - Your Printify shop ID

### 3. Initialize Database

```bash
artomate init-db
```

## Your First Job

### Create a job

```bash
artomate create \
  --theme "minimalist cat" \
  --style "japandi" \
  --niche "wall-art"
```

This will output: `✓ Created job 1`

### Run the job

```bash
artomate run 1
```

This will:
1. Generate image using DALL-E 3
2. Download and save locally
3. Render print files for common sizes
4. Mark job as DONE

### Check status

```bash
# Single job
artomate status 1

# All jobs
artomate status

# Filter by state
artomate status --state done
artomate status --state failed
```

## What Just Happened?

The system:

1. ✓ Created a job in SQLite database
2. ✓ Generated prompt: "minimalist cat, japandi style, suitable for wall art print, high quality, detailed, professional, original design, no text, no logos"
3. ✓ Called OpenAI DALL-E 3 API
4. ✓ Downloaded image to `data/assets/images/`
5. ✓ Created asset record in database
6. ✓ Rendered print files to `data/assets/printfiles/`
7. ✓ Created print file records in database
8. ✓ Updated job state: CREATED → GENERATING → RENDERING → DONE

## File Structure

After running your first job:

```
artomate/
├── data/
│   ├── artomate.db          # SQLite database
│   └── assets/
│       ├── images/          # Generated images
│       │   └── job_1_20250101_120000_0_0.png
│       └── printfiles/      # Print-ready files
│           ├── printfile_1_..._4500x5400.png  # T-shirt
│           └── printfile_1_..._3000x4000.png  # Poster
└── logs/
    └── artomate.log         # Application logs
```

## Next Steps

### Create More Jobs

```bash
# Simple
artomate create --theme "turtle" --style "boho"

# Advanced
artomate create \
  --theme "japanese garden" \
  --style "watercolor" \
  --niche "home-decor" \
  --keywords "zen,peaceful,meditation" \
  --priority 8
```

### Batch Create (CSV)

Create `jobs.csv`:

```csv
theme,style,niche,keywords
minimalist cat,japandi,wall-art,"cat,cute,minimalism"
vintage bicycle,retro,apparel,"bike,vintage,urban"
tropical leaves,boho,home-decor,"tropical,plants,nature"
```

Then import (coming soon):

```bash
artomate import jobs.csv
```

### View Statistics

```bash
artomate stats
```

Output:
```
Job Statistics

  Total jobs: 5
  created: 1
  generating: 0
  rendering: 0
  done: 4
  failed: 0
```

## Troubleshooting

### Job fails with "OpenAI API error"

- Check your `OPENAI_API_KEY` in `.env`
- Verify API key is active at https://platform.openai.com/api-keys
- Check you have credits available

### "Image generation failed: timeout"

- OpenAI DALL-E 3 can take 30-60 seconds
- Increase timeout in `.env`: `IMAGE_GENERATION_TIMEOUT=180`

### Database errors

Reset database:

```bash
artomate reset-db
# WARNING: This will delete all jobs and assets!
```

### Check logs

```bash
tail -f logs/artomate.log
```

## What's Next?

### Phase 1 (MVP) - ✅ Complete
- [x] SQLite database
- [x] Image generation (OpenAI DALL-E)
- [x] Pillow crop/resize
- [x] CLI interface
- [x] Basic state machine

### Phase 2 - Coming Soon
- [ ] Printify product creation
- [ ] Etsy listing automation
- [ ] n8n orchestration
- [ ] Telegram bot integration
- [ ] Feed exports (XML/CSV/JSON)

### Phase 3 - Planned
- [ ] Social media automation
- [ ] Stock platform submission
- [ ] Analytics dashboard
- [ ] A/B testing

## Support

- Documentation: See `README.md`
- Issues: Report bugs or request features
- Logs: Check `logs/artomate.log` for detailed output

## Tips

1. **Start small**: Generate 1-2 jobs to test before scaling
2. **Monitor costs**: Each DALL-E 3 HD image costs $0.08
3. **Check compliance**: Review generated images for trademark issues
4. **Use priorities**: Higher priority (8-10) for trending topics
5. **Backup database**: Regular backups of `data/artomate.db`

Happy automating! 🎨🤖
