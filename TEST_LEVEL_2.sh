#!/bin/bash
echo "=== ARTOMATE LEVEL 2 TEST (OpenAI Required) ==="
echo ""

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set in .env"
    echo ""
    echo "To run this test:"
    echo "1. Add to .env: OPENAI_API_KEY=sk-..."
    echo "2. Run: source .env && ./TEST_LEVEL_2.sh"
    echo ""
    echo "Skipping Level 2..."
    exit 0
fi

echo "✓ OpenAI API key found"
echo ""

echo "Testing image generation..."
python3 << 'PYEOF'
from artomate.core.job_manager import JobManager
from artomate.workers.image_generator import ImageGenerator

# Create job
manager = JobManager()
job = manager.create_job(
    theme="minimalist cat",
    style="japandi",
    niche="wall-art",
    keywords=["cat", "minimalist", "zen"]
)

print(f"✓ Created job {job.id}")

# Generate image
generator = ImageGenerator()
print("\n🎨 Generating image with DALL-E 3...")
print("(This takes 30-60 seconds...)")

try:
    assets = generator.generate_for_job(job, count=1)
    print(f"\n✓ Generated {len(assets)} asset(s)")
    
    for asset in assets:
        print(f"  - Asset {asset.id}: {asset.width}x{asset.height}")
        print(f"    Path: {asset.storage_path}")
        print(f"    Size: {asset.file_size_bytes:,} bytes")
        
except Exception as e:
    print(f"\n✗ Generation failed: {e}")
    import traceback
    traceback.print_exc()
PYEOF

echo ""
echo "=== LEVEL 2 COMPLETE ==="
