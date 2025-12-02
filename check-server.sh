#!/bin/bash

# Server Health Check Script for PrimePath Development
# Automatically checks if the Next.js dev server is running and restarts if needed

PORT=3000
SERVER_URL="http://localhost:$PORT"
LOG_FILE="/tmp/nextjs.log"

echo "🔍 Checking server status..."

# Check if server responds
if curl -f -s -o /dev/null -w "%{http_code}" -m 2 "$SERVER_URL" | grep -q "200"; then
    echo "✅ Server is running on port $PORT"
    exit 0
else
    echo "❌ Server is not responding"
    
    # Kill any existing Next.js processes
    echo "🔄 Cleaning up existing processes..."
    pkill -f "next dev" 2>/dev/null || true
    sleep 1
    
    # Start the server in background
    echo "🚀 Starting Next.js development server..."
    nohup npm run dev > "$LOG_FILE" 2>&1 &
    SERVER_PID=$!
    
    echo "⏳ Waiting for server to start (PID: $SERVER_PID)..."
    
    # Wait for server to be ready (max 30 seconds)
    for i in {1..30}; do
        if curl -f -s -o /dev/null -w "%{http_code}" -m 1 "$SERVER_URL" 2>/dev/null | grep -q "200"; then
            echo "✅ Server started successfully!"
            echo "📍 URL: $SERVER_URL"
            echo "📄 Logs: $LOG_FILE"
            exit 0
        fi
        sleep 1
        echo -n "."
    done
    
    echo ""
    echo "❌ Server failed to start after 30 seconds"
    echo "Check logs at: $LOG_FILE"
    exit 1
fi