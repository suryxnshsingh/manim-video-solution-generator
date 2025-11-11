#!/bin/bash

# AI Video Solution Generator - Run Script

set -e

echo "=================================="
echo "AI Video Solution Generator"
echo "=================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create a .env file with your OpenAI API key:"
    echo "  cp .env.example .env"
    echo "  # Edit .env and add your OPENAI_API_KEY"
    exit 1
fi

# Check if OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  Warning: OPENAI_API_KEY might not be set in .env file"
    echo "Please ensure your .env file contains a valid OpenAI API key"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build Docker image if needed
echo "🐳 Checking Docker setup..."
if ! docker images | grep -q "manim-video"; then
    echo "Building Docker image (this may take a few minutes)..."
    docker-compose build
fi

echo ""
echo "🚀 Starting video generation..."
echo "This will take several minutes (5-10 minutes typically)"
echo ""

# Run the generator
docker-compose run --rm manim-video-generator python main.py

echo ""
echo "✅ Done! Check the output/final/ directory for your video."
