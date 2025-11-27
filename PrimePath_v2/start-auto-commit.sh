#!/bin/bash

echo "🚀 Starting auto-commit every 2 hours..."
echo "Press Ctrl+C to stop"

while true; do
    ./auto-commit.sh
    echo "⏰ Next auto-commit in 2 hours..."
    sleep 7200  # 2 hours = 7200 seconds
done