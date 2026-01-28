#!/bin/bash

# Start Crop Tester UI
# Usage: ./start_crop_ui.sh

cd "$(dirname "$0")"

echo "🎨 Starting Crop Tester UI..."
echo "📍 Opening at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""

streamlit run ui/crop_tester_ui.py
