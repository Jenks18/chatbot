#!/bin/bash

# ToxicoGPT - Quick Start Script
# This script sets up and runs the entire toxicology chatbot system

set -e

echo "======================================"
echo "🧬 ToxicoGPT Setup & Deployment"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠️  Please review and update .env file with your settings"
    echo ""
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/papers data/vectorstore
echo "✓ Data directories created"
echo ""

# Build and start containers
echo "🐳 Building and starting Docker containers..."
echo "This may take a few minutes on first run..."
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker ps | grep -q "toxicology-backend"; then
    echo "✓ Backend service is running"
else
    echo "❌ Backend service failed to start"
    docker-compose logs backend
    exit 1
fi

if docker ps | grep -q "toxicology-frontend"; then
    echo "✓ Frontend service is running"
else
    echo "❌ Frontend service failed to start"
    docker-compose logs frontend
    exit 1
fi

if docker ps | grep -q "toxicology-model"; then
    echo "✓ Model server is running"
else
    echo "❌ Model server failed to start"
    docker-compose logs model_server
    exit 1
fi

echo ""
echo "======================================"
echo "✅ ToxicoGPT is now running!"
echo "======================================"
echo ""
echo "📥 Download AI model (required on first run):"
echo "   docker exec -it toxicology-model ollama pull llama3:8b"
echo ""
echo "🌐 Access the application:"
echo "   Chat Interface:   http://localhost:3000"
echo "   Admin Dashboard:  http://localhost:3000/admin"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Health Check:     http://localhost:8000/health"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop the application:"
echo "   docker-compose down"
echo ""
echo "======================================"
