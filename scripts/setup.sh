#!/bin/bash
# AI-Agent-Local-Infrastructure — Setup Script
# Run this script after cloning to set up the environment.

set -e

echo "============================================"
echo " AI-Agent-Local-Infrastructure Setup"
echo "============================================"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Please install Python 3.10+"
    exit 1
fi

echo "[1/4] Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "[2/4] Installing Hermes Agent..."
pip install --upgrade pip
pip install hermes-agent

echo "[3/4] Setting up config..."
if [ ! -f config.yaml ]; then
    cp config/config.yaml.example config.yaml
    echo "  → Created config.yaml from template"
    echo "  → Edit config.yaml with your API keys and credentials"
else
    echo "  → config.yaml already exists, skipping"
fi

echo "[4/4] Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit config.yaml with your credentials"
echo "  2. Create .env with your API keys"
echo "  3. Run: source .venv/bin/activate && hermes"
echo ""
echo "============================================"
