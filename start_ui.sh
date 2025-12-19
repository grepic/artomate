#!/bin/bash
echo "🎨 Starting Artomate UI..."
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "⚠️  Streamlit not installed"
    echo "Installing: pip install streamlit"
    pip install streamlit
fi

# Start Streamlit
streamlit run ui/streamlit_app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --theme.primaryColor "#1f77b4" \
    --theme.backgroundColor "#0e1117" \
    --theme.secondaryBackgroundColor "#262730"
