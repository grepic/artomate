#!/bin/bash
echo "=== ARTOMATE LEVEL 4 TEST (REST API) ==="
echo ""

echo "Starting FastAPI server in background..."
uvicorn artomate.api.main:app --host 127.0.0.1 --port 8000 > /tmp/api.log 2>&1 &
API_PID=$!

echo "Waiting for server to start..."
sleep 3

echo ""
echo "Testing API endpoints..."

# Test health
echo "1. Health check:"
curl -s http://localhost:8000/health | python3 -m json.tool

echo ""
echo "2. Root endpoint:"
curl -s http://localhost:8000/ | python3 -m json.tool

echo ""
echo "3. Create job via API:"
curl -s -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{"theme": "ocean waves", "style": "minimalist", "niche": "wall-art"}' | python3 -m json.tool

echo ""
echo "4. Get analytics:"
curl -s http://localhost:8000/api/analytics/stats | python3 -m json.tool

echo ""
echo "Stopping API server..."
kill $API_PID 2>/dev/null

echo ""
echo "✓ API server logs in /tmp/api.log"
echo ""
echo "To run API manually:"
echo "  uvicorn artomate.api.main:app --reload"
echo "  Open http://localhost:8000/docs"
echo ""
echo "=== LEVEL 4 COMPLETE ==="
