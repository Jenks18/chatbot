#!/bin/bash
# Quick setup script for local testing with SQLite

set -e

echo "🚀 Setting up local development environment with SQLite..."

# Create .env.local file
cat > .env.local << 'EOF'
# Local Development with SQLite
DEV_SQLITE=1

# DeepSeek AI Model
DEEPSEEK_API_KEY=sk-052da17567ab438bb0ea6e80b346a85d
DEEPSEEK_MODEL=deepseek-chat

# Public API Keys
OPENFDA_API_KEY=rH2feOTgRtT4WRuooKmDqiHlKuDqmhhJK6GqTeAb
NCBI_API_KEY=5141dbd81188ce3fc0547dbcf18a3fbe9209

# API Caching
API_CACHE_DURATION_DAYS=30
ENABLE_API_CACHING=true

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

echo "✅ Created .env.local file"

# Initialize database
echo "📊 Initializing SQLite database..."
cd backend
python3 << 'PYTHON'
import sys
import os
sys.path.insert(0, os.getcwd())
os.environ['DEV_SQLITE'] = '1'

from db.database import Base, engine
Base.metadata.create_all(engine)
print("✅ Database tables created successfully!")
PYTHON

cd ..

echo ""
echo "✨ Setup complete!"
echo ""
echo "To start the application:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    cd backend"
echo "    uvicorn main:app --reload --port 8000"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    npm run dev"
echo ""
echo "Then open: http://localhost:3000"
echo ""
