@echo off
REM Immanuel MCP Server - Windows Startup Script
REM This script activates the virtual environment and starts the server

echo Starting Immanuel MCP Server...

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found at .venv\Scripts\
    echo Please run the following commands first:
    echo   uv venv
    echo   uv pip install -e .
    pause
    exit /b 1
)

REM Check if uv is available
where uv >nul 2>&1
if errorlevel 1 (
    echo WARNING: uv not found in PATH. Using pip fallback.
    goto :use_venv
)

REM Activate virtual environment and start server
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Verify uvicorn is available
where uvicorn >nul 2>&1
if errorlevel 1 (
    echo ERROR: uvicorn not found. Installing dependencies...
    uv pip install -e .
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Starting server on http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
uvicorn app.main:app --host 127.0.0.1 --port 8000
goto :end

:use_venv
echo Using virtual environment Python...
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

:end
echo Server stopped.
if "%1" neq "--no-pause" pause