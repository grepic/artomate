# 🎬 Viral Content Creation Guide

Kompletní průvodce automatickým vytvářením virálních videí pro TikTok, Instagram Reels a YouTube Shorts.

---

## 📋 Přehled Systému

Artomate nyní umí automaticky vytvářet **virální video content** s:
- ✅ **AI-generovanými fakty** o zvířatech
- ✅ **Profesionálními video efekty** (zoom, pan, Ken Burns)
- ✅ **Text overlays** s fakty
- ✅ **Viral hooks** (attention-grabbing intros)
- ✅ **Call-to-action** (CTA) outro
- ✅ **Background music** (volitelně)
- ✅ **Multi-platform formáty** (TikTok 9:16, Instagram 1:1, YouTube 16:9)
- ✅ **Optimalizované captions a hashtags**
- ✅ **Ready-to-post export**

---

## 🎯 Co Systém Vytvoří

### Z Jednoho Obrázku Vytvoří:

```
Input: cat_image.png (tvůj design)

Output:
├── TikTok Video (1080x1920, 15s)
│   ├── Viral hook: "Did you know cats have a SECRET superpower? 🤯"
│   ├── 3 AI facts s overlays
│   ├── Ken Burns effect
│   ├── Background music
│   └── CTA: "FOLLOW FOR MORE!"
│
├── Instagram Reel (1080x1920, 15s)
│   ├── Stejný content jako TikTok
│   └── Instagram-optimized captions & hashtags
│
└── YouTube Short (1080x1920, 60s)
    ├── Delší verze s více fakty (5 faktů)
    └── YouTube-optimized metadata

+ Captions pro každou platformu
+ Hashtags optimalizované na engagement
+ README s posting instructions
```

---

## 🚀 Jak Na To

### **Option 1: Kompletní Automatika (Doporučeno)**

```bash
# Vytvoř kompletní viral package pro všechny platformy
curl -X POST http://localhost:8000/api/viral/package \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 123,
    "asset_id": 456,
    "platforms": ["tiktok", "instagram", "youtube"],
    "export": true
  }'
```

**Co se stane:**
1. ✅ Vygeneruje 5 AI faktů o tématu (např. o kočkách)
2. ✅ Vytvoří 3 videa (TikTok, Instagram, YouTube)
3. ✅ Přidá text overlays s fakty
4. ✅ Přidá viral hook intro
5. ✅ Přidá hudbu na pozadí
6. ✅ Vygeneruje captions a hashtags
7. ✅ Exportuje ready-to-post složku

**Výstup:**
```
data/exports/job_123_20250120/
├── tiktok/
│   ├── video.mp4          ← Nahraj na TikTok
│   ├── caption.txt        ← Copy/paste caption
│   └── hashtags.txt       ← Copy/paste hashtags
├── instagram/
│   ├── video.mp4
│   ├── caption.txt
│   └── hashtags.txt
├── youtube/
│   ├── video.mp4
│   ├── caption.txt
│   └── hashtags.txt
└── README.md              ← Posting instructions
```

### **Option 2: Jen AI Fakty**

```bash
# Vygeneruj pouze fakty (bez videa)
curl -X POST http://localhost:8000/api/viral/facts \
  -H "Content-Type: application/json" \
  -d '{
    "animal": "elephant",
    "count": 5,
    "style": "viral"
  }'
```

**Response:**
```json
{
  "animal": "elephant",
  "facts": [
    "Elephants can't jump - they're the only mammals that can't! 🐘",
    "An elephant's trunk has over 40,000 muscles! 💪",
    "Elephants mourn their dead like humans do 😢",
    "Elephants can hear each other from 5 miles away! 👂",
    "Elephants are pregnant for 22 months - longest of any mammal! 🤰"
  ],
  "count": 5
}
```

**Styles:**
- `viral` - Shareable, viral-worthy facts
- `fun` - Zábavné a entertaining
- `educational` - Vzdělávací a vědecké
- `shocking` - Překvapivé a mind-blowing
- `cute` - Roztomilé a heartwarming

### **Option 3: Jen Viral Hook**

```bash
# Vygeneruj attention-grabbing intro
curl -X POST http://localhost:8000/api/viral/hook \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "cats",
    "duration": "short"
  }'
```

**Response:**
```json
{
  "theme": "cats",
  "hook": "This cat fact will BLOW YOUR MIND! 🤯 Wait for it...",
  "duration": "short"
}
```

**Durations:**
- `short` - 3-5 sekund (první 3 sekundy videa)
- `long` - 7-10 sekund (delší buildup)

### **Option 4: Posting Schedule**

```bash
# Zjisti kdy postovat pro maximum reach
curl "http://localhost:8000/api/viral/schedule?platforms=tiktok&platforms=instagram"
```

**Response:**
```json
{
  "platforms": {
    "tiktok": {
      "best_times": ["7-9 PM", "12-1 PM"],
      "best_days": ["Tuesday", "Thursday", "Friday"],
      "frequency": "1-3 posts/day",
      "optimal_length": "15-30 seconds",
      "tips": [
        "Use trending sounds",
        "Hook in first 3 seconds",
        "Engage with comments immediately",
        "Post consistently same time daily"
      ]
    },
    "instagram": {
      "best_times": ["6-9 AM", "12-2 PM", "5-7 PM"],
      "best_days": ["Monday", "Wednesday", "Thursday"],
      "frequency": "1-2 reels/day",
      "optimal_length": "7-15 seconds",
      "tips": [
        "Use 5-7 relevant hashtags",
        "Share to stories after posting",
        "Cross-post to feed",
        "Collaborate with similar accounts"
      ]
    }
  }
}
```

---

## 🎨 Video Formáty

| Platform | Rozměry | Aspect Ratio | Max Délka | FPS | Formát |
|----------|---------|--------------|-----------|-----|--------|
| TikTok | 1080x1920 | 9:16 | 15-60s | 30 | MP4 |
| Instagram Reel | 1080x1920 | 9:16 | 15-90s | 30 | MP4 |
| Instagram Square | 1080x1080 | 1:1 | 15-60s | 30 | MP4 |
| YouTube Short | 1080x1920 | 9:16 | 15-60s | 30 | MP4 |
| YouTube | 1920x1080 | 16:9 | Neomezeno | 30 | MP4 |

---

## 🎬 Video Efekty

### **Ken Burns Effect** (Doporučeno)
- Kombinace zoom + pan
- Profesionální, cinematic look
- Udržuje pozornost diváka
- Nejlepší pro statické obrázky

### **Zoom Effect**
- Plynulé přibližování
- Jednoduché, ale efektivní
- Dobrý pro detail shots

### **Pan Effect**
- Horizontální posun
- Dobrý pro široké obrázky
- Vytváří pocit pohybu

### **Slideshow**
- Více obrázků za sebou
- Každý obrázek X sekund
- Dobrý pro before/after, kolekce

---

## 📝 Caption & Hashtag Generování

### Caption Structure

```
🌟 Amazing Cat Facts! 🤯

Did you know...

1. Cats spend 70% of their lives sleeping! 😴
2. A cat's purr can help heal bones! 🦴
3. Cats can rotate their ears 180 degrees! 👂

Which fact surprised you most? Comment below! 👇

Follow for more amazing facts! ❤️

—
#catfacts #cats #catsofinstagram #catfacts ...
```

### Hashtag Strategy

**Platform Limits:**
- Instagram: Max 30 hashtags (use 5-10 for best engagement)
- TikTok: Max 10 hashtags
- YouTube: Max 15 hashtags

**Mix:**
- **Niche tags** (high relevance): `#catfacts`, `#catlovers`
- **Medium tags** (moderate competition): `#catsofinstagram`, `#petstagram`
- **Broad tags** (high reach): `#viral`, `#fyp`, `#trending`

---

## 🎵 Background Music

### Setup (Volitelné)

1. Stáhni royalty-free music:
   - [Pixabay Music](https://pixabay.com/music/)
   - [Uppbeat](https://uppbeat.io/)
   - [YouTube Audio Library](https://studio.youtube.com/channel/UC.../music)

2. Ulož do:
   ```
   data/assets/music/
   ├── upbeat_1.mp3
   ├── chill_vibes.mp3
   └── trending_sound.mp3
   ```

3. Systém automaticky přidá hudbu na pozadí (30% volume)

**Bez hudby:** Stále funguje! Jen přeskoč music overlay.

---

## 💡 Best Practices pro Virální Content

### ✅ DO:

1. **Hook v prvních 3 sekundách**
   - "Did you know..."
   - "This will blow your mind..."
   - "Nobody talks about this..."

2. **Jednoduché, čitelné texty**
   - Velké fonty
   - High contrast (white on black)
   - Emojis pro visual appeal

3. **Překvapivé fakty**
   - Věci co lidé neznají
   - Mind-blowing statistics
   - "Wait, what?!" momenty

4. **CTA na konci**
   - "Follow for more!"
   - "Double tap if you agree!"
   - "Which fact surprised you?"

5. **Cross-post všude najednou**
   - TikTok + Instagram + YouTube = 3× reach
   - Postuj do 1 hodiny od sebe

### ❌ DON'T:

1. ❌ Dlouhé texty (nikdo nečte)
2. ❌ Mluvení bez hook (ztratíš lidi)
3. ❌ Nudné fakty (everyone knows)
4. ❌ Špatná kvalita videa (1080p minimum)
5. ❌ Zapomenout na CTA (ztratíš follows)

---

## 📊 Tracking & Analytics

### Metrics to Track:

| Metric | TikTok | Instagram | YouTube |
|--------|--------|-----------|---------|
| Views | ✅ | ✅ | ✅ |
| Watch Time % | ✅ | ✅ | ✅ |
| Likes | ✅ | ✅ | ✅ |
| Comments | ✅ | ✅ | ✅ |
| Shares | ✅ | ✅ | ❌ |
| Saves | ❌ | ✅ | ❌ |

### Success Benchmarks:

**TikTok:**
- Good: 1,000+ views
- Great: 10,000+ views
- Viral: 100,000+ views

**Instagram:**
- Good: 500+ views
- Great: 5,000+ views
- Viral: 50,000+ views

**YouTube Shorts:**
- Good: 1,000+ views
- Great: 10,000+ views
- Viral: 100,000+ views

---

## 🔧 Troubleshooting

### Video není vytvořené

**Check:**
```bash
# Je FFmpeg nainstalovaný?
ffmpeg -version

# Pokud ne:
apt-get install ffmpeg  # Linux
brew install ffmpeg     # Mac
```

### Žádné AI fakty

**Check:**
```bash
# Je OPENAI_API_KEY v .env?
grep OPENAI_API_KEY .env

# Máš kredity na OpenAI?
# Check: https://platform.openai.com/usage
```

### Hudba se nepřidává

**Check:**
```bash
# Existuje music složka?
ls data/assets/music/

# Pokud ne:
mkdir -p data/assets/music
# Stáhni MP3 soubory do této složky
```

### Text není čitelný

**Fix:**
- Zvětši fontsize v `enhanced_video_renderer.py`
- Zmen barvu textu (yellow/white)
- Přidej větší background box

---

## 🎓 Kompletní Workflow Příklad

### Scénář: Chceš vytvořit viral cat content

```bash
# 1. Vytvoř design (nebo už máš z jobu)
# Job ID: 123, Asset ID: 456 (cat_minimalist.png)

# 2. Vytvoř viral package
curl -X POST http://localhost:8000/api/viral/package \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 123,
    "asset_id": 456,
    "platforms": ["tiktok", "instagram", "youtube"],
    "export": true
  }'

# Response:
# {
#   "export_path": "data/exports/job_123_20250120_143022",
#   "video_count": 3,
#   "fact_count": 5,
#   ...
# }

# 3. Otevři export folder
cd data/exports/job_123_20250120_143022

# 4. Post na TikTok
# - Otevři TikTok app
# - Upload tiktok/video.mp4
# - Copy caption z tiktok/caption.txt
# - Copy hashtags z tiktok/hashtags.txt
# - Post v 7-9 PM (peak time)

# 5. Post na Instagram (do 30 minut)
# - Otevři Instagram app
# - Create Reel
# - Upload instagram/video.mp4
# - Copy caption z instagram/caption.txt
# - Copy hashtags z instagram/hashtags.txt
# - Share to Feed + Stories

# 6. Post na YouTube (do 1 hodiny)
# - Otevři YouTube Studio app
# - Create Short
# - Upload youtube/video.mp4
# - Copy caption z youtube/caption.txt
# - Post

# 7. Engage!
# - Respond to comments (první 30 min critical)
# - Like comments
# - Pin top comment s question
# - Share na další platformy

# 8. Track Analytics (after 24h)
# - Check views, likes, comments
# - Identify what worked
# - Replicate successful patterns
```

---

## 📈 Scaling Strategy

### **Week 1: Testing**
- Post 1-2 videa/den
- Test různá témata (cats, dogs, elephants)
- Test různé časy (morning vs evening)
- Track co funguje

### **Week 2: Optimize**
- Double down na best performers
- Post 3-5 videa/den
- Konzistentní posting times
- Build audience

### **Week 3+: Scale**
- Batch creation (10+ videos najednou)
- Schedule posts
- Repurpose top content
- Collaborate with others

### **Automation**

```bash
# Cron job - denní automatika
# crontab -e
0 18 * * * /path/to/create_and_post_daily.sh

# create_and_post_daily.sh:
#!/bin/bash

# Get trending topic (manual or API)
TOPIC="dolphins"

# Create content
curl -X POST http://localhost:8000/api/viral/package \
  -d '{"job_id": 123, "asset_id": 456, "platforms": ["tiktok","instagram"]}'

# Export created
# Manual post (or use social media APIs if approved)
```

---

## 🎯 Expected Results

### **If you post 3 videa/day:**

**Month 1:**
- 90 videos total
- ~50,000 total views
- ~500 followers gained

**Month 3:**
- 270 videos total
- ~500,000 total views
- ~5,000 followers gained
- Some videos hitting 100k+ views

**Month 6:**
- Established presence
- Consistent viral hits
- Growing audience
- Potential for monetization

### **Revenue Potential:**

**Indirect (Product Sales):**
- Link in bio → Etsy shop
- 1% conversion rate
- $15 average order
- 5,000 followers × 1% × $15 = **$750/month**

**Direct (Creator Fund):**
- TikTok: $0.02-0.04 per 1,000 views
- 500,000 views/month × $0.03 = **$15/month**
- (Scales with views)

**Sponsorships:**
- 10k+ followers: $100-500/post
- 50k+ followers: $500-2,000/post
- 100k+ followers: $2,000-10,000/post

---

## 🎬 Ukázkové Video Timeline

```
0:00 - 0:03  🎯 VIRAL HOOK
             "Did you know cats have a SECRET superpower?"
             [Yellow text, bold, center]
             [Zoom začíná]

0:03 - 0:08  📝 FACT 1
             "FACT 1"
             "Cats spend 70% of their lives sleeping!"
             [White text with black box]
             [Ken Burns effect continues]

0:08 - 0:13  📝 FACT 2
             "FACT 2"
             "A cat's purr can help heal bones!"
             [Smooth transition]

0:13 - 0:15  🎯 CTA
             "FOLLOW FOR MORE!"
             [Yellow text, bold, bottom third]
             [Music fades out]
```

---

## 📚 Další Resources

### Royalty-Free Assets:
- **Music:** Pixabay, Uppbeat, YouTube Audio Library
- **Sound Effects:** Freesound.org, Zapsplat
- **Fonts:** Google Fonts (pro text overlays)

### Analytics Tools:
- **TikTok:** TikTok Analytics (in-app)
- **Instagram:** Instagram Insights (in-app)
- **YouTube:** YouTube Studio

### Learning:
- [TikTok Creator Portal](https://www.tiktok.com/creators/)
- [Instagram Creator Hub](https://creators.instagram.com/)
- [YouTube Creator Academy](https://creatoracademy.youtube.com/)

---

## ✨ Hotovo!

Teď máš **kompletní automatický systém** na vytváření viral content! 🚀

**Next Steps:**
1. Doplň OpenAI API key do `.env`
2. Stáhni pár royalty-free music do `data/assets/music/`
3. Vytvoř první viral package
4. Post a sleduj views! 📈

**Questions?** Check `/health` endpoint nebo logy v `logs/artomate.log`

---

**Happy Creating! 🎬✨**
