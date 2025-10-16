#!/bin/bash

# Pharmacy Exam Prep - Stop Application Script

# Get the directory where the script is located and navigate to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

echo "🛑 Stopping Pharmacy Exam Prep Application..."

# Kill all Flask/Python processes related to this app
echo "🔍 Finding all Flask processes..."
FLASK_PIDS=$(ps aux | grep '[p]ython.*app.py' | awk '{print $2}')

if [ -n "$FLASK_PIDS" ]; then
    echo "⚠️  Found Flask processes: $FLASK_PIDS"
    for PID in $FLASK_PIDS; do
        echo "   Stopping PID: $PID"
        kill $PID 2>/dev/null
    done
    sleep 2

    # Force kill if still running
    REMAINING=$(ps aux | grep '[p]ython.*app.py' | awk '{print $2}')
    if [ -n "$REMAINING" ]; then
        echo "⚠️  Force stopping remaining processes..."
        kill -9 $REMAINING 2>/dev/null
    fi
else
    echo "ℹ️  No Flask processes found"
fi

# Kill any process on port 5001 (backup)
if lsof -ti:5001 > /dev/null 2>&1; then
    echo "⚠️  Stopping processes on port 5001..."
    lsof -ti:5001 | xargs kill -9 2>/dev/null
fi

# Clean up PID file
if [ -f ".app.pid" ]; then
    rm .app.pid
fi

echo "✅ All application processes stopped!"
echo ""
echo "Verify with: ps aux | grep app.py"
