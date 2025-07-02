@echo off
REM Test script to verify MCP mode works correctly

echo Testing MCP mode configuration...
echo.

cd /d "%~dp0.."

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
    echo Please run: uv venv && uv pip install -e .
    pause
    exit /b 1
)

echo Testing MCP server startup (will run for 5 seconds)...
echo.

REM Start the MCP server in the background
start /B .venv\Scripts\python.exe app\mcp_main.py

REM Wait a moment for startup
timeout /t 3 /nobreak >nul

REM Check if the process is running
tasklist /FI "IMAGENAME eq python.exe" | find /I "python.exe" >nul
if errorlevel 1 (
    echo ERROR: MCP server failed to start
    echo Check logs\mcp_server.log for details
    pause
    exit /b 1
) else (
    echo SUCCESS: MCP server is running
)

REM Test if logs directory was created
if exist "logs\mcp_server.log" (
    echo SUCCESS: Log file created at logs\mcp_server.log
    echo.
    echo Last 5 lines from log:
    powershell -Command "Get-Content logs\mcp_server.log -Tail 5"
) else (
    echo WARNING: No log file found
)

echo.
echo Stopping test server...
taskkill /F /IM python.exe >nul 2>&1

echo.
echo MCP mode test completed.
echo.
echo If successful, you can use this configuration in Claude Desktop:
echo {
echo   "mcpServers": {
echo     "immanuel-astrology": {
echo       "command": "%CD%\\start_server_mcp.bat",
echo       "cwd": "%CD%"
echo     }
echo   }
echo }
echo.
pause