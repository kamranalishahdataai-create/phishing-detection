#!/usr/bin/env bash
# Build script for Render.com deployment

set -e

echo "🔧 Starting Render build..."

# Upgrade pip
pip install --upgrade pip

# Install dependencies (CPU-only PyTorch)
pip install -r requirements-render.txt

# Create necessary directories
mkdir -p backend/logs

echo "✅ Build complete!"
