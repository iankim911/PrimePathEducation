# Chrome MCP Server - Troubleshooting & Setup Log
*Successfully Connected: August 11, 2025*

## Problem Summary
Chrome MCP tools were showing "Failed to connect to MCP server" error despite the extension being installed and MCP server showing as connected in Claude.

## Root Causes Identified
1. Native messaging host needed proper registration with correct extension ID
2. Permissions on native host files needed fixing
3. Chrome extension service worker goes inactive after 30 seconds without DevTools

## Solution Steps That Fixed It

### 1. Install mcp-chrome-bridge globally
```bash
npm install -g mcp-chrome-bridge
```
Location: `/Users/ian/.npm-global/lib/node_modules/mcp-chrome-bridge/`

### 2. Register Native Messaging Host
```bash
mcp-chrome-bridge register --force
```
This created: `/Users/ian/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.chromemcp.nativehost.json`

### 3. Fix Permissions
```bash
mcp-chrome-bridge fix-permissions
```

### 4. Add MCP Server to Claude
```bash
claude mcp add chrome-mcp /Users/ian/.npm-global/lib/node_modules/mcp-chrome-bridge/dist/mcp/mcp-server-stdio.js
```

### 5. Verify Configuration
Native host config should contain:
```json
{
  "name": "com.chromemcp.nativehost",
  "description": "Node.js Host for Browser Bridge Extension",
  "path": "/Users/ian/.npm-global/lib/node_modules/mcp-chrome-bridge/dist/run_host.sh",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://hbdgbgagpkpjffpklnamcljpakneikee/"
  ]
}
```

### 6. Keep Service Worker Active (IMPORTANT)
- Go to `chrome://extensions/`
- Find "chrome-mcp-server" extension
- Click on "service worker" link to open DevTools
- **Keep DevTools window open** (prevents service worker from going inactive)

## Quick Start for Future Sessions

### Every Time You Start Claude:
1. **Open Chrome first**
2. Go to `chrome://extensions/`
3. Click "service worker" link for chrome-mcp-server extension
4. **Keep the DevTools window open** (minimized is fine)
5. Start Claude - Chrome MCP should connect automatically

### Verify Connection:
```bash
claude mcp list
```
Should show: `chrome-mcp: ... - ✓ Connected`

## Key File Locations
- **Native Host Config**: `/Users/ian/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.chromemcp.nativehost.json`
- **MCP Bridge**: `/Users/ian/.npm-global/lib/node_modules/mcp-chrome-bridge/`
- **Extension ID**: `hbdgbgagpkpjffpklnamcljpakneikee`

## Troubleshooting Commands
```bash
# Check MCP server status
claude mcp list

# Re-register if needed
mcp-chrome-bridge register --force

# Fix permissions if needed  
mcp-chrome-bridge fix-permissions

# View native host config
cat "/Users/ian/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.chromemcp.nativehost.json"
```

## Common Issues & Fixes

### "Failed to connect to MCP server"
1. Check Chrome DevTools is open for service worker
2. Restart Claude
3. If still failing, re-register: `mcp-chrome-bridge register --force`

### Service Worker Shows "Inactive"
- Must click "service worker" link and keep DevTools open
- This is a Chrome limitation - service workers auto-suspend after 30 seconds without DevTools

### Chrome Not Responding
1. Quit Chrome completely (Cmd+Q)
2. Restart Chrome
3. Re-open service worker DevTools
4. Restart Claude

## Working Test
Once connected, test with:
- Check open tabs: `mcp__chrome-mcp__get_windows_and_tabs`
- Navigate: `mcp__chrome-mcp__chrome_navigate` with URL parameter
- Take screenshot: `mcp__chrome-mcp__chrome_screenshot`

---
*Note: The Chrome extension service worker MUST have DevTools open to stay active. This is a Chrome security feature and cannot be bypassed.*