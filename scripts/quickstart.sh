#!/bin/bash
# Quick start script for CodeAudit local development

set -e

echo "======================================"
echo "CodeAudit - Quick Start"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY before continuing"
    echo "   Then run this script again."
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -q -r requirements.txt

echo "Initializing database..."
python scripts/init_db.py

echo ""
echo "======================================"
echo "✓ Setup Complete!"
echo "======================================"
echo ""
echo "To start the application:"
echo ""
echo "1. Start the API:"
echo "   uvicorn api.main:app --reload"
echo ""
echo "2. (Optional) Start the worker in another terminal:"
echo "   python workers/code_review_worker.py"
echo ""
echo "3. Start the frontend in another terminal:"
echo "   cd frontend && npm install && npm start"
echo ""
echo "Then visit: http://localhost:3000"
echo "API Docs: http://localhost:8080/docs"
echo ""
