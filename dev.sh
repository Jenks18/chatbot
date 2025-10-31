#!/bin/bash

# Start both backend and frontend in development mode

echo "🚀 Starting ToxicoGPT in development mode..."
echo ""

# Check if backend is already running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend already running on http://localhost:8000"
else
    echo "🐍 Starting backend..."
    cd backend && source venv/bin/activate && python main.py &
    BACKEND_PID=$!
    echo "   Backend PID: $BACKEND_PID"
    sleep 3
fi

# Start frontend
echo "⚛️  Starting frontend..."
cd frontend && npm run dev

# This will keep running until you press Ctrl+C
