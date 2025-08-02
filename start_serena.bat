@echo off
cd /d "C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_\serena"
echo Starting Serena MCP Server...
uv run serena start-mcp-server --context ide-assistant --project "C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_"
pause