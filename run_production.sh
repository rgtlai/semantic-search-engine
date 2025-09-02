#!/bin/bash

# Semantic Search Engine Production Startup Script

set -e  # Exit on any error

echo "🏭 Starting Semantic Search Engine Production Environment"
echo "======================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create one based on .env.example"
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

if ! command_exists node; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ All prerequisites found"

# Build frontend
echo "⚛️  Building React frontend for production..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

echo "🏗️  Building optimized React build..."
npm run build

cd ..

# Setup backend
echo "🐍 Setting up Python backend for production..."
cd backend

if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment and installing dependencies..."
source venv/bin/activate

# Install/upgrade pip and dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Additional production dependencies
pip install gunicorn

echo "📂 Copying React build to backend static folder..."
rm -rf app/static/*
mkdir -p app/static
cp -r ../frontend/build/* app/static/

echo "🚀 Starting production server with Gunicorn..."
echo ""
echo "🎉 Production server starting..."
echo "================================"
echo "📍 Application: http://localhost:8000"
echo "📍 API Docs:    http://localhost:8000/docs"
echo ""

# Start with Gunicorn
gunicorn app.main:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --log-level info \
    --access-logfile - \
    --error-logfile -