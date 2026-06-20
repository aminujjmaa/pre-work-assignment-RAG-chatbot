#!/usr/bin/env bash
# ─────────────────────────────────────────────────────
# setup.sh — Install all dependencies for RAG Scholar
# ─────────────────────────────────────────────────────
set -e
cd "$(dirname "$0")/backend"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  RAG Scholar — Dependency Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Tesseract OCR (optional, for scanned PDFs)
if ! command -v tesseract &>/dev/null; then
  echo "[1/4] Installing Tesseract OCR..."
  sudo apt-get install -y tesseract-ocr tesseract-ocr-eng 2>/dev/null || echo "Skipping tesseract (no sudo)"
else
  echo "[1/4] Tesseract already installed ✓"
fi

# Python venv
echo "[2/4] Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install CPU-only PyTorch first (smaller, faster)
echo "[3/4] Installing PyTorch (CPU)..."
pip install --quiet torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install all other requirements
echo "[4/4] Installing Python requirements..."
pip install --quiet -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Make sure Ollama is running:  ollama serve"
echo "  2. Pull an LLM model:            ollama pull llama3.2:3b"
echo "  3. Start the server:             ./run.sh"
