#!/bin/bash

echo "=== FIXING VS CODE 'IDE DISCONNECTED' ISSUE ==="
echo ""

# 1. Kill any stuck language server processes
echo "🔧 Step 1: Cleaning up stuck language server processes..."
pkill -f "pylsp" 2>/dev/null || true
pkill -f "pyright" 2>/dev/null || true
pkill -f "pylance" 2>/dev/null || true
pkill -f "jedi-language-server" 2>/dev/null || true
echo "   ✅ Language server processes cleared"

# 2. Clear VS Code workspace storage to reset extensions
echo ""
echo "🔧 Step 2: Clearing VS Code workspace cache..."
WORKSPACE_STORAGE="$HOME/Library/Application Support/Code/User/workspaceStorage"
if [ -d "$WORKSPACE_STORAGE" ]; then
    # Find and remove cache for the current project
    find "$WORKSPACE_STORAGE" -maxdepth 2 -name "*.json" -exec grep -l "PrimePath" {} \; | while read file; do
        DIR=$(dirname "$file")
        echo "   Clearing workspace cache: $(basename $DIR)"
        rm -rf "$DIR/state.vscdb" 2>/dev/null || true
        rm -rf "$DIR/state.vscdb.backup" 2>/dev/null || true
    done
    echo "   ✅ Workspace cache cleared"
else
    echo "   ⚠️  Workspace storage not found at expected location"
fi

# 3. Clear Python extension cache
echo ""
echo "🔧 Step 3: Clearing Python extension cache..."
PYTHON_CACHE="$HOME/.vscode/extensions/.python-workspace-cache"
if [ -d "$PYTHON_CACHE" ]; then
    rm -rf "$PYTHON_CACHE"
    echo "   ✅ Python extension cache cleared"
else
    echo "   ℹ️  No Python cache found"
fi

# 4. Reset Copilot extension
echo ""
echo "🔧 Step 4: Resetting Copilot extension state..."
COPILOT_DIR="$HOME/.vscode/extensions/github.copilot-*"
for dir in $COPILOT_DIR; do
    if [ -d "$dir" ]; then
        echo "   Found Copilot extension: $(basename $dir)"
        # Just touch the extension to trigger reload, don't delete
        touch "$dir/package.json" 2>/dev/null || true
    fi
done
echo "   ✅ Copilot extension marked for reload"

# 5. Create VS Code settings to auto-reconnect
echo ""
echo "🔧 Step 5: Updating VS Code settings for better connection stability..."
VSCODE_SETTINGS="$HOME/Library/Application Support/Code/User/settings.json"
if [ -f "$VSCODE_SETTINGS" ]; then
    # Backup current settings
    cp "$VSCODE_SETTINGS" "$VSCODE_SETTINGS.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Check if we need to add connection settings
    if ! grep -q "remote.autoForwardPorts" "$VSCODE_SETTINGS"; then
        echo "   Adding connection stability settings..."
        # This is a bit complex to do safely in bash, so we'll just notify
        echo "   ℹ️  Please add these settings manually to VS Code settings.json:"
        echo '      "remote.autoForwardPorts": true,'
        echo '      "remote.autoForwardPortsSource": "hybrid",'
        echo '      "extensions.autoCheckUpdates": true,'
        echo '      "extensions.autoUpdate": true'
    else
        echo "   ✅ Connection settings already configured"
    fi
else
    echo "   ⚠️  VS Code settings file not found"
fi

echo ""
echo "=== FIX COMPLETE ==="
echo ""
echo "📋 NEXT STEPS:"
echo "1. In VS Code, press Cmd+Shift+P"
echo "2. Type: 'Developer: Reload Window'"
echo "3. Press Enter to reload VS Code"
echo ""
echo "Alternative: Close and reopen VS Code completely"
echo ""
echo "The 'IDE disconnected' message should now be resolved! 🎉"
echo ""
echo "If the issue persists:"
echo "• Check Extensions view (Cmd+Shift+X) for any disabled extensions"
echo "• Look for updates to Python/Copilot extensions"
echo "• Try signing out and back into GitHub Copilot"