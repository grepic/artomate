# Artomate Scripts

Collection of scripts for testing, generating, and managing the Artomate content-to-commerce system.

## Testing Scripts

### test_product_crops.py

Test product crops for all families and variants with visual verification.

**Usage:**
```bash
python scripts/test_product_crops.py <path_to_test_image>
```

**Example:**
```bash
python scripts/test_product_crops.py test_images/test_image.png
```

**Output:**
- Creates `test_output/crop_test_{timestamp}/` directory
- Generates optimized crops for all 19 product families (57+ variants)
- Creates interactive HTML report with visual previews
- Organized by category: apparel, home_living, wall_art, drinkware, accessories

**Features:**
- ✅ Transparent backgrounds for apparel/accessories (RGBA)
- ✅ Full coverage for home décor/wall art (RGB)
- ✅ All crop modes: cover, contain, smart_crop
- ✅ 300 DPI quality
- ✅ Correct dimensions for each variant

### verify_crops.py

Verify that generated crops have correct format and dimensions.

**Usage:**
```bash
python scripts/verify_crops.py <test_output_dir>
```

**Example:**
```bash
python scripts/verify_crops.py test_output/crop_test_20251221_044749
```

**Checks:**
- ✅ Transparent products have RGBA mode
- ✅ Full coverage products have RGB mode
- ✅ Dimensions match specifications
- ✅ All variants present

### create_test_image.py

Generate a colorful test image for crop testing.

**Usage:**
```bash
python scripts/create_test_image.py
```

**Output:**
- Creates `test_images/test_image.png` (3000×3000 pixels)
- Colorful gradient with corner markers for orientation
- High quality for testing all product variants

## Production Scripts

### generate_product_from_ai.py

Generate complete product line from AI-generated image.

**Features:**
1. Generates AI image with DALL-E
2. Creates crops for ALL product families and variants
3. Uploads to Printify
4. Publishes to Etsy (TODO)
5. Creates viral social media content (TikTok, Instagram, YouTube)

**Usage:**
```bash
python scripts/generate_product_from_ai.py \
  --prompt "cute red panda astronaut" \
  --animal "red panda" \
  [--families tshirt poster mug] \
  [--dry-run] \
  [--no-printify] \
  [--no-etsy] \
  [--no-social]
```

**Arguments:**
- `--prompt` (required): DALL-E prompt
- `--animal` (required): Animal name for facts generation
- `--families`: Specific product families to create (default: all 19)
- `--dry-run`: Test mode - don't actually upload/publish
- `--no-printify`: Skip Printify upload
- `--no-etsy`: Skip Etsy publishing
- `--no-social`: Skip social media content creation

**Examples:**

Generate all products (dry run):
```bash
python scripts/generate_product_from_ai.py \
  --prompt "majestic lion king with golden mane" \
  --animal "lion" \
  --dry-run
```

Generate specific products only:
```bash
python scripts/generate_product_from_ai.py \
  --prompt "cute baby elephant" \
  --animal "elephant" \
  --families tshirt hoodie mug sticker
```

Full production run:
```bash
python scripts/generate_product_from_ai.py \
  --prompt "wise owl on magical tree" \
  --animal "owl"
```

### batch_generate_products.py

Batch generate products from CSV file with multiple prompts.

**Usage:**
```bash
python scripts/batch_generate_products.py <csv_file> \
  [--delay 60] \
  [--dry-run] \
  [--no-printify] \
  [--no-etsy] \
  [--no-social]
```

**CSV Format:**
```csv
prompt,animal,families
"cute red panda astronaut","red panda","tshirt,poster,mug"
"majestic lion king","lion",""
```

Columns:
- `prompt`: DALL-E prompt text
- `animal`: Animal name for facts
- `families`: Comma-separated family IDs (empty = all families)

**Arguments:**
- `csv_file` (required): Path to CSV file with prompts
- `--delay`: Delay between generations in seconds (default: 60)
- `--dry-run`: Test mode
- `--no-printify`: Skip Printify upload
- `--no-etsy`: Skip Etsy publishing
- `--no-social`: Skip social media content

**Example:**
```bash
# Dry run with example prompts
python scripts/batch_generate_products.py example_prompts.csv --dry-run

# Production run with 2-minute delay
python scripts/batch_generate_products.py my_prompts.csv --delay 120
```

## Product Families

Available product families (19 total, 57+ variants):

**Apparel** (transparent background):
- `tshirt` - Unisex T-Shirt
- `tshirt_premium` - Premium T-Shirt
- `tshirt_womens` - Women's T-Shirt
- `hoodie` - Unisex Hoodie
- `sweatshirt` - Crewneck Sweatshirt

**Home Living** (full coverage):
- `blanket` - Fleece Blanket (4 sizes)
- `pillow` - Throw Pillow (5 sizes)
- `towel` - Towel (3 types)
- `rug` - Area Rug (4 sizes)
- `duvet` - Duvet Cover (3 sizes)

**Wall Art** (full coverage):
- `poster` - Poster (6 sizes: 8×10 to 24×36)
- `canvas` - Canvas Print (9 sizes)
- `framed_print` - Framed Print (4 sizes)

**Drinkware** (transparent):
- `mug` - Ceramic Mug (11oz, 15oz)
- `travel_mug` - Travel Mug (15oz)
- `water_bottle` - Water Bottle (20oz, 30oz)

**Accessories** (transparent):
- `phone_case` - Phone Case (iPhone 14, 14 Pro, Samsung S23)
- `tote_bag` - Tote Bag (2 sizes)
- `sticker` - Die-Cut Sticker (4 sizes)

## Workflow

### 1. Test Crop System

First, verify that crop system works correctly:

```bash
# Generate test image
python scripts/create_test_image.py

# Test all crops
python scripts/test_product_crops.py test_images/test_image.png

# Verify crop quality
python scripts/verify_crops.py test_output/crop_test_*/

# Open HTML report in browser
# file:///.../test_output/crop_test_*/index.html
```

### 2. Test AI Generation (Dry Run)

Test the full workflow without uploading:

```bash
python scripts/generate_product_from_ai.py \
  --prompt "cute red panda astronaut" \
  --animal "red panda" \
  --dry-run
```

### 3. Generate Single Product Line

Create actual products for one design:

```bash
python scripts/generate_product_from_ai.py \
  --prompt "majestic lion king" \
  --animal "lion" \
  --families poster canvas tshirt
```

### 4. Batch Generate Multiple Designs

Create products for multiple designs from CSV:

```bash
# Test first
python scripts/batch_generate_products.py example_prompts.csv --dry-run

# Production
python scripts/batch_generate_products.py example_prompts.csv --delay 120
```

## Requirements

- Python 3.11+
- All dependencies from `requirements.txt`
- OpenAI API key for DALL-E and GPT-4
- Printify API key
- Etsy API credentials (for publishing)
- Telegram bot token (for notifications)

## Environment Variables

Required in `.env`:
```bash
OPENAI_API_KEY=sk-...
PRINTIFY_API_KEY=...
ETSY_API_KEY=...
ETSY_SHOP_ID=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

## Output Structure

```
artomate/
├── data/
│   ├── ai_images/          # Generated AI images
│   ├── print_files/        # Print-ready product files
│   └── videos/             # Social media videos
├── test_output/            # Test crop output
│   └── crop_test_*/
│       ├── apparel/
│       ├── home_living/
│       ├── wall_art/
│       ├── drinkware/
│       ├── accessories/
│       └── index.html
└── exports/                # Export data
```

## Tips

1. **Always test first with --dry-run** before production runs
2. **Use delay between generations** to avoid API rate limits
3. **Check HTML reports** to verify crop quality
4. **Start with specific families** before generating all products
5. **Monitor logs** for errors and warnings

## Troubleshooting

**"API rate limit exceeded":**
- Increase `--delay` in batch generation
- Reduce number of concurrent requests

**"Crop quality issues":**
- Run `verify_crops.py` to identify problems
- Check HTML report visually
- Verify source image quality (min 1024×1024)

**"Printify upload failed":**
- Check API credentials in `.env`
- Verify blueprint IDs in `printify_product_families.py`
- Check print file dimensions match Printify requirements

**"Out of memory":**
- Reduce number of families in single run
- Use `--families` to generate specific products only
- Large products (King duvet) require more memory
