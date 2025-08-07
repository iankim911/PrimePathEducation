@echo off
echo Starting Serena MCP Server for PrimePath project...
echo.
echo This will start the Serena IDE assistant with:
echo - Context: ide-assistant (for development tasks)
echo - Project: PrimePath_ Django application
echo - Transport: stdio (for Claude integration)
echo.

REM Start Serena MCP server with appropriate settings
C:\Users\ianki\.local\bin\uvx --from git+https://github.com/oraios/serena serena start-mcp-server ^
    --context ide-assistant ^
    --project "C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_" ^
    --transport stdio

pause