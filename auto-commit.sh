#!/bin/bash

# Auto-commit script - runs every 2 hours when files change
# Only commits when there are actual changes

echo "🔍 Checking for changes..."

# Check if there are any changes
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Changes detected, creating auto-commit..."
    
    # Add all changes
    git add .
    
    # Create commit with timestamp
    current_time=$(date +"%Y-%m-%d %H:%M")
    git commit -m "auto-commit: progress saved $current_time"
    
    # Try to push to GitHub
    git push origin main 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Changes saved and pushed to GitHub"
    else
        echo "💾 Changes saved locally (GitHub push failed - check connection)"
    fi
else
    echo "✨ No changes to commit"
fi