#!/bin/bash
echo "=== ARTOMATE LEVEL 1 TEST ==="
echo ""

echo "1. Testing CLI..."
artomate --version

echo ""
echo "2. Testing database..."
artomate stats

echo ""
echo "3. Creating test job (no API key needed)..."
artomate create --theme "mountain landscape" --style "minimalist" --niche "wall-art"

echo ""
echo "4. Checking job status..."
artomate status

echo ""
echo "5. Testing trend analyzer..."
python3 << 'PYEOF'
from artomate.workers.trend_analyzer import TrendAnalyzer

analyzer = TrendAnalyzer()
trends = analyzer.get_trending_themes(limit=5)

print("\n🔥 Top 5 Trending Themes:")
for i, trend in enumerate(trends, 1):
    print(f"{i}. {trend['theme']} ({trend['style']}) - Score: {trend.get('trend_score', 0):.0f}")
PYEOF

echo ""
echo "6. Testing feed export (empty data)..."
python3 << 'PYEOF'
from artomate.workers.feed_exporter import FeedExporter
from pathlib import Path

exporter = FeedExporter()
# Export with no data (just to test it works)
path = exporter.export_products(format="json")
print(f"✓ Created empty export: {path}")
PYEOF

echo ""
echo "=== LEVEL 1 COMPLETE ✓ ==="
