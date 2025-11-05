#!/bin/bash

# Quick Start Script for Groq Compound Model

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🚀 GROQ COMPOUND MODEL - QUICK START              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Groq API key is set
if grep -q "gsk_your_actual_api_key_here" backend/.env; then
    echo "⚠️  GROQ_API_KEY not configured!"
    echo ""
    echo "1. Get your FREE Groq API key:"
    echo "   👉 https://console.groq.com/keys"
    echo ""
    echo "2. Edit backend/.env and replace:"
    echo "   GROQ_API_KEY=gsk_your_actual_api_key_here"
    echo "   with your actual key"
    echo ""
    echo "3. Run this script again"
    exit 1
fi

echo "✅ Groq API key found"
echo ""

# Start the backend
echo "Starting backend with Groq compound model..."
echo "Features enabled:"
echo "  • web_search - Search the web for latest drug information"
echo "  • code_interpreter - Analyze drug data structures"
echo "  • visit_website - Fetch information from medical databases"
echo ""

cd "$(dirname "$0")"

PYTHONPATH=backend DEV_SQLITE=1 \
./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo ""
echo "Backend stopped."
