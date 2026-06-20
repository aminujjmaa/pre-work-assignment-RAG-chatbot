#!/usr/bin/env bash
# Full one-shot install script for RAG Scholar
# Run: bash install_all.sh
set -e

BACKEND="/home/dell/hackathon/backend"
VENV="$BACKEND/.venv"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  RAG Scholar — Full Install"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Tesseract
echo "[1/5] Tesseract OCR..."
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng libgl1 2>/dev/null || true

# 2. venv
echo "[2/5] Python venv..."
python3 -m venv "$VENV"

# 3. CPU PyTorch
echo "[3/5] PyTorch (CPU only, ~250MB)..."
"$VENV/bin/pip" install --quiet torch --index-url https://download.pytorch.org/whl/cpu

# 4. All other deps
echo "[4/5] Python requirements..."
"$VENV/bin/pip" install --quiet -r "$BACKEND/requirements.txt"

# 5. Ollama model
echo "[5/5] Pulling Ollama LLM (llama3.2:3b, ~2GB)..."
if command -v ollama &>/dev/null; then
  ollama pull llama3.2:3b || /snap/bin/ollama pull llama3.2:3b || true
elif [ -f /snap/bin/ollama ]; then
  /snap/bin/ollama pull llama3.2:3b || true
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Installation complete!"
echo ""
echo "  To download sample PDFs (10 books, ~200+ pages each):"
echo "    python3 /home/dell/hackathon/download_pdfs.py"
echo ""
echo "  To start the server:"
echo "    bash /home/dell/hackathon/run_all.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
