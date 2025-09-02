#!/bin/bash

# Semantic Search Engine Development Startup Script

set -e  # Exit on any error

echo "🚀 Starting Semantic Search Engine Development Environment"
echo "=================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env file with your API keys before continuing"
    echo "   Required: OPENAI_API_KEY, ARES_API_KEY"
    exit 1
fi

# Check if API keys are set
if ! grep -q "^OPENAI_API_KEY=your_openai_api_key_here" .env; then
    echo "✅ OpenAI API key appears to be configured"
else
    echo "❌ Please set your OPENAI_API_KEY in .env file"
    exit 1
fi

if ! grep -q "^ARES_API_KEY=your_ares_api_key_here" .env; then
    echo "✅ ARES API key appears to be configured"
else
    echo "❌ Please set your ARES_API_KEY in .env file"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command_exists uv; then
    echo "❌ uv is required but not installed"
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ All prerequisites found"

# Start backend in background
echo "🐍 Setting up Python backend..."
cd backend

echo "🔧 Installing dependencies with uv..."
uv sync

echo "🚀 Starting FastAPI backend server..."
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Give backend time to start
sleep 3

cd ..

# Start frontend in background
echo "⚛️  Setting up React frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

echo "🚀 Starting React development server..."
npm start &
FRONTEND_PID=$!

cd ..

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down development servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

echo ""
echo "🎉 Development environment started successfully!"
echo "=================================================="
echo "📍 Frontend: http://localhost:3000"
echo "📍 Backend:  http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Tips:"
echo "   - Press Ctrl+C to stop all servers"
echo "   - Edit .env to configure API keys and settings"
echo "   - Check logs above for any startup errors"
echo ""
echo "⏳ Servers are starting... (Frontend may take 30-60 seconds)"

# Wait for user to press Ctrl+C
wait