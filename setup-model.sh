#!/bin/bash

# Download and setup AI model for toxicology

echo "======================================"
echo "🤖 Downloading AI Model"
echo "======================================"
echo ""

# Check which model to download
MODEL_NAME="${1:-llama3:8b}"

echo "Downloading model: $MODEL_NAME"
echo "This may take several minutes depending on your internet connection..."
echo ""

docker exec -it toxicology-model ollama pull $MODEL_NAME

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Model downloaded successfully!"
    echo ""
    echo "Available models for toxicology:"
    echo "  - llama3:8b (recommended, general purpose)"
    echo "  - mistral (fast, efficient)"
    echo "  - meditron (specialized for medical/toxicology)"
    echo ""
    echo "To use a different model, update MODEL_NAME in .env file"
    echo ""
else
    echo ""
    echo "❌ Model download failed"
    echo "Please check your internet connection and Docker status"
    exit 1
fi
