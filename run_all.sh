#!/usr/bin/env bash
# Start RAG Scholar (Groq Cloud backend — no Ollama needed)
set -e
BACKEND="/home/dell/hackathon/backend"
VENV="$BACKEND/.venv"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎓 RAG Scholar — Starting (Groq Cloud)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check .env has API key
if grep -q "GROQ_API_KEY=your_groq" "$BACKEND/.env" 2>/dev/null || ! grep -q "GROQ_API_KEY=gsk_" "$BACKEND/.env" 2>/dev/null; then
  echo ""
  echo "  ⚠️  Set your Groq API key first:"
  echo "     echo 'GROQ_API_KEY=gsk_xxx' > $BACKEND/.env"
  echo "     Get a free key at: https://console.groq.com"
  echo ""
fi

echo "  → Web UI:  http://localhost:8000"
echo "  → API docs: http://localhost:8000/docs"
echo ""

"$VENV/bin/python3" "$BACKEND/main.py"
