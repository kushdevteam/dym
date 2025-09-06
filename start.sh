#!/bin/bash

# Start script for Solana Narrative Scanner
echo "🚀 Starting Solana Narrative Scanner..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📋 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys before running again"
    exit 1
fi

# Start the API server
echo "🔥 Starting FastAPI server..."
cd api && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# Wait a moment for API to start
sleep 3

# Start the dashboard
echo "🎨 Starting Next.js dashboard..."
cd ../dashboard && npm run dev &
DASHBOARD_PID=$!

echo "✅ Services started!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔌 API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "echo 'Stopping services...'; kill $API_PID $DASHBOARD_PID; exit" INT
wait