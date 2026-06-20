#!/usr/bin/env bash
# ─────────────────────────────────────────────────────
# run.sh — Start RAG Scholar server
# ─────────────────────────────────────────────────────
set -e
cd "$(dirname "$0")/backend"

# Activate venv
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎓 RAG Scholar — Starting server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  → Open: http://localhost:8000"
echo "  → API:  http://localhost:8000/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
