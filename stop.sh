#!/bin/bash

# Stop and clean up ToxicoGPT services

echo "Stopping all ToxicoGPT services..."
docker-compose down

if [ "$1" == "--clean" ]; then
    echo ""
    echo "🧹 Cleaning up volumes and data..."
    docker-compose down -v
    echo "✓ All data has been removed"
    echo "⚠️  You will need to download the AI model again on next start"
fi

echo ""
echo "✅ ToxicoGPT has been stopped"
