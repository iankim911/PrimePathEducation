# Chrome MCP Setup Status

## Completed Steps ✅
1. Installed mcp-chrome-bridge npm package globally
2. Registered native messaging host (`~/.npm-global/bin/mcp-chrome-bridge register`)
3. Downloaded and installed chrome-mcp-server v0.0.6 extension from GitHub
4. Extension ID: `hbdgbgagpkpjffpklnamclijpakneikee` 
5. Activated service worker (now shows as active in DevTools)
6. MCP server shows as "Connected" in `claude mcp list`

## Current Issue
- Claude shows "Not connected" when trying to use Chrome MCP functions
- Both chrome-mcp-server and Browser MCP extensions are installed (might be conflicting)

## Next Steps to Try
1. Disable Browser MCP extension (ID: bjfgambnhccakkhmkepdoekmckoijdlc)
2. Check if chrome-mcp-server extension needs additional configuration
3. Verify native host registration matches extension ID

## Test Command
After setup, test with: Can you use Chrome MCP to get browser tabs?

## Files/Configs
- Native host config: ~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.chromemcp.nativehost.json
- Extension location: Loaded from chrome-mcp-server-0.0.6.zip
- MCP server: ~/.npm-global/lib/node_modules/mcp-chrome-bridge/