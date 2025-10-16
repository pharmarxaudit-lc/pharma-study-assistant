#!/bin/bash

# Pharmacy Exam Prep - Local Development Startup Script

# Get the directory where the script is located and navigate to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

echo "🚀 Starting Pharmacy Exam Prep Application..."
echo ""

# Check if .env file exists in project root
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found in project root!"
    echo "Please create .env file with your ANTHROPIC_API_KEY"
    exit 1
fi

# Check if API key is set
if grep -q "your-api-key-here" .env; then
    echo "❌ Error: Please set your ANTHROPIC_API_KEY in .env file"
    exit 1
fi

# Kill any existing process on port 5001
echo "🔍 Checking for existing processes on port 5001..."
if lsof -ti:5001 > /dev/null 2>&1; then
    echo "⚠️  Port 5001 is in use. Stopping existing process..."
    lsof -ti:5001 | xargs kill -9
    sleep 2
fi

# Create necessary directories
mkdir -p uploads outputs backend/static

# Check if frontend is built
if [ ! -d "frontend/dist" ]; then
    echo "📦 Frontend not built. Building now..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

# Copy frontend to backend static
echo "📋 Copying frontend build to backend..."
cp -r frontend/dist/* backend/static/

# Start the Flask server
echo "🔧 Starting Flask backend server on port 5001..."
cd backend
PORT=5001 python app.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Save PID for stop script
echo $BACKEND_PID > .app.pid

# Wait a moment for server to start
sleep 3

# Check if server started successfully
if curl -s http://localhost:5001/api/health > /dev/null; then
    echo ""
    echo "✅ Application started successfully!"
    echo ""
    echo "📍 Access the application at: http://localhost:5001"
    echo "🏥 Health check: http://localhost:5001/api/health"
    echo "📊 Backend PID: $BACKEND_PID"
    echo "📝 Logs: tail -f logs/backend.log"
    echo ""
    echo "To stop the application, run: ./stop_app.sh"
else
    echo ""
    echo "❌ Failed to start application"
    echo "Check logs/backend.log for errors"
    exit 1
fi
