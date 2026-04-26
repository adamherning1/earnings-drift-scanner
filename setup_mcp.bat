@echo off
echo Installing Massive MCP Server...

REM Install using uv (Python package installer)
pip install uv
uv tool install "mcp_massive @ git+https://github.com/massive-com/mcp_massive@v0.9.1"

REM Set API key
set MASSIVE_API_KEY=W9yf_4m5NsX89ZNS5jGSfYkVorDBPiGfN

REM Run the MCP server
echo.
echo Starting MCP server to discover endpoints...
mcp_massive

pause