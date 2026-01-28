#!/bin/bash
echo "🚀 Starting Artomate Full Stack..."
echo ""

# Start API in background
echo "Starting API server..."
/workspaces/artomate/.venv/bin/uvicorn artomate.api.main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
API_PID=$!
echo "  ✓ API running (PID: $API_PID)"

# Wait a bit
sleep 2

# Start UI in background
echo "Starting UI..."
/workspaces/artomate/.venv/bin/streamlit run ui/streamlit_app.py --server.port 8501 > logs/ui.log 2>&1 &
UI_PID=$!
echo "  ✓ UI running (PID: $UI_PID)"

echo ""
echo "=== Artomate is running! ==="
echo ""
echo "  📊 API: http://localhost:8000"
echo "  📚 API Docs: http://localhost:8000/docs"
echo "  🎨 UI: http://localhost:8501"
echo ""
echo "Logs:"
echo "  tail -f logs/api.log"
echo "  tail -f logs/ui.log"
echo ""
echo "To stop:"
echo "  kill $API_PID $UI_PID"
echo ""

# Save PIDs
echo "$API_PID" > logs/api.pid
echo "$UI_PID" > logs/ui.pid
