@echo off
REM Immanuel MCP Server - Silent MCP-compliant startup script
REM This script provides ONLY JSON-RPC communication for Claude Desktop

REM Get the directory where this script is located and change to it
cd /d "%~dp0"

REM Set MCP mode to disable console output
set MCP_MODE=true
set PYTHONUNBUFFERED=1

REM Check if virtual environment exists (silently)
if not exist ".venv\Scripts\python.exe" (
    REM If no virtual environment, exit silently (Claude Desktop will show connection error)
    exit /b 1
)

REM Start the MCP server with no console output
REM All logs go to files, only JSON-RPC goes to stdout
.venv\Scripts\python.exe app\mcp_main.py