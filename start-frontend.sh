#!/bin/bash

# Start frontend server

cd "$(dirname "$0")/frontend"

if [ ! -d "node_modules" ]; then
    echo "❌ Node modules not found. Run ./setup-local.sh first"
    exit 1
fi

echo "⚛️  Starting Next.js frontend..."
export NEXT_PUBLIC_API_URL="http://localhost:8000"

npm run dev
