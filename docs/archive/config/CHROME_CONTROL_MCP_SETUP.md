# Chrome Control MCP Setup - Working Solution

## Overview
This document describes the **working method** to set up Chrome automation in Claude using the built-in Chrome Control extension. 

**Important**: The third-party `mcp-chrome-bridge` solution does NOT work reliably and should be avoided.

## Prerequisites
- Claude Desktop App (macOS)
- Google Chrome installed
- Claude's built-in Chrome Control extension (comes with Claude)

## Setup Steps

### 1. Locate Claude's Built-in Chrome Control Extension
Claude comes with a pre-installed Chrome Control extension located at:
```
~/Library/Application Support/Claude/Claude Extensions/ant.dir.ant.anthropic.chrome-control/
```

### 2. Add Chrome Control to MCP Configuration
Run this command in your terminal:
```bash
claude mcp add chrome-control "node" "$HOME/Library/Application Support/Claude/Claude Extensions/ant.dir.ant.anthropic.chrome-control/server/index.js"
```

### 3. Verify Configuration
Check that Chrome Control is configured:
```bash
claude mcp list
```

You should see:
```
chrome-control: node /Users/[username]/Library/Application Support/Claude/Claude Extensions/ant.dir.ant.anthropic.chrome-control/server/index.js - ✓ Connected
```

### 4. Restart Claude
**Important**: After adding the MCP server, you must restart Claude for the tools to become available.

### 5. Test Chrome Control Tools
After restart, the following tools will be available in Claude:
- `mcp__chrome-control__open_url` - Open URLs in Chrome
- `mcp__chrome-control__get_current_tab` - Get current tab info
- `mcp__chrome-control__list_tabs` - List all open tabs
- `mcp__chrome-control__close_tab` - Close specific tabs
- `mcp__chrome-control__switch_to_tab` - Switch to a tab
- `mcp__chrome-control__reload_tab` - Reload tabs
- `mcp__chrome-control__go_back` - Navigate back in history
- `mcp__chrome-control__go_forward` - Navigate forward
- `mcp__chrome-control__execute_javascript` - Execute JS in tabs
- `mcp__chrome-control__get_page_content` - Get page text content

## How It Works
- Uses native macOS AppleScript automation
- No browser extension required
- No need to keep DevTools open
- No 30-second timeout issues
- Direct communication with Chrome via Claude's built-in extension

## Troubleshooting

### Tools Not Available After Setup
1. Make sure you've restarted Claude after adding the MCP server
2. Verify connection with `claude mcp list`
3. If still not working, try removing and re-adding:
   ```bash
   claude mcp remove chrome-control
   claude mcp add chrome-control "node" "$HOME/Library/Application Support/Claude/Claude Extensions/ant.dir.ant.anthropic.chrome-control/server/index.js"
   ```
   Then restart Claude again

### Chrome Not Responding
1. Make sure Chrome is running
2. Check that Chrome has accessibility permissions in System Preferences > Security & Privacy > Privacy > Accessibility

## What NOT to Use
❌ **Do NOT use `mcp-chrome-bridge`** - This third-party solution has issues:
- Requires keeping Chrome DevTools open
- Service worker times out after 30 seconds
- Complex setup with browser extension
- Unreliable connection

## Example Usage in Claude
Once set up, you can use Chrome Control in Claude like this:

```python
# Open a URL
mcp__chrome-control__open_url(url="http://127.0.0.1:8000/", new_tab=True)

# Get current tab info
mcp__chrome-control__get_current_tab()

# List all tabs
mcp__chrome-control__list_tabs()

# Execute JavaScript
mcp__chrome-control__execute_javascript(code="document.title", tab_id=123456)
```

## Benefits
✅ No browser extension needed
✅ No DevTools requirement
✅ No timeout issues
✅ Native Claude integration
✅ Reliable and stable
✅ Simple one-command setup

---
*Last Updated: December 2024*
*This is the correct, working method for Chrome automation in Claude*