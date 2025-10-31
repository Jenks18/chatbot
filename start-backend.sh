#!/bin/bash

# Start backend server

cd "$(dirname "$0")/backend"

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup-local.sh first"
    exit 1
fi

echo "🐍 Starting FastAPI backend..."
source venv/bin/activate

export DATABASE_URL="postgresql://toxgpt_user:toxgpt_pass_2025@localhost:5432/toxicology_gpt"
export MODEL_SERVER_URL="http://localhost:11434"
export MODEL_NAME="llama3.2:3b"
export CORS_ORIGINS="http://localhost:3000,http://localhost:3001"

# Run without file watching to avoid reload loop
uvicorn main:app --host 0.0.0.0 --port 8000
