#!/bin/bash

# Local setup script for ToxicoGPT (without Docker)

echo "======================================"
echo "🧬 ToxicoGPT Local Setup"
echo "======================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION found"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✓ Node.js $NODE_VERSION found"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found. Installing via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install postgresql@15
        brew services start postgresql@15
    else
        echo "❌ Please install PostgreSQL manually: https://www.postgresql.org/download/"
        exit 1
    fi
else
    echo "✓ PostgreSQL found"
fi

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found. Installing..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✓ Ollama found"
fi

echo ""
echo "📁 Setting up project..."

# Setup Backend
echo "🐍 Setting up Python backend..."
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  Created virtual environment"
fi

source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Backend dependencies installed"

cd ..

# Setup Frontend
echo "⚛️  Setting up Node.js frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    npm install
    echo "✓ Frontend dependencies installed"
else
    echo "✓ Frontend dependencies already installed"
fi

cd ..

# Setup Database
echo "💾 Setting up PostgreSQL database..."

# Create database and user
psql postgres -c "CREATE DATABASE toxicology_gpt;" 2>/dev/null || echo "  Database already exists"
psql postgres -c "CREATE USER toxgpt_user WITH PASSWORD 'toxgpt_pass_2025';" 2>/dev/null || echo "  User already exists"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE toxicology_gpt TO toxgpt_user;" 2>/dev/null

# Initialize schema
psql toxicology_gpt < backend/db/init.sql 2>/dev/null
echo "✓ Database initialized"

# Start Ollama if not running
echo "🤖 Checking Ollama service..."
if ! pgrep -x "ollama" > /dev/null; then
    echo "  Starting Ollama..."
    ollama serve > /dev/null 2>&1 &
    sleep 2
    echo "✓ Ollama started"
else
    echo "✓ Ollama already running"
fi

# Check if model exists
if ! ollama list | grep -q "llama3:8b"; then
    echo ""
    echo "📥 Downloading AI model (this will take 5-10 minutes)..."
    ollama pull llama3:8b
    echo "✓ Model downloaded"
else
    echo "✓ Model already downloaded"
fi

echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "To start the application:"
echo ""
echo "  Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn main:app --reload"
echo ""
echo "  Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:3000"
echo ""
