#!/bin/bash
set -e

cd "$(dirname "$0")/backend"

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "⚠️  Configure sua ANTHROPIC_API_KEY em backend/.env"
fi

if [ ! -d "venv" ]; then
  echo "📦 Criando ambiente virtual..."
  python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

echo "🚀 Iniciando Minha Vida em http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
