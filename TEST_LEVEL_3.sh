#!/bin/bash
echo "=== ARTOMATE LEVEL 3 TEST (Printify + Rendering) ==="
echo ""

echo "Testing render engine (works without API keys)..."
python3 << 'PYEOF'
from artomate.workers.render_engine import RenderEngine
from artomate.core.job_manager import JobManager
from PIL import Image
import tempfile
from pathlib import Path

# Create a test image
temp_dir = Path(tempfile.mkdtemp())
test_image = temp_dir / "test.png"

# Create 1024x1024 test image
img = Image.new('RGB', (1024, 1024), color='blue')
img.save(test_image)

print(f"✓ Created test image: {test_image}")

# Test rendering
renderer = RenderEngine()

print("\n🎨 Testing crop modes:")
modes = ["contain", "cover"]

for mode in modes:
    rendered = renderer.render_image(
        source_path=test_image,
        target_width=4500,
        target_height=5400,
        mode=mode
    )
    print(f"  ✓ {mode}: {rendered.size}")

print("\n✓ Render engine working!")

# Cleanup
import shutil
shutil.rmtree(temp_dir)
PYEOF

echo ""
echo "Testing Printify worker (requires API key)..."

if [ -z "$PRINTIFY_API_TOKEN" ]; then
    echo "⚠️  PRINTIFY_API_TOKEN not set"
    echo "Skipping Printify test..."
else
    echo "✓ Printify credentials found"
    python3 << 'PYEOF'
from artomate.integrations.printify_client import PrintifyClient

try:
    client = PrintifyClient()
    shops = client.get_shops()
    print(f"✓ Connected to Printify")
    print(f"  Found {len(shops)} shop(s)")
except Exception as e:
    print(f"✗ Printify connection failed: {e}")
PYEOF
fi

echo ""
echo "=== LEVEL 3 COMPLETE ==="
