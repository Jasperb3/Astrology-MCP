@echo off
REM Immanuel MCP Server - Complete Windows Setup Script
REM This script sets up everything needed for Windows users

echo ====================================
echo Immanuel MCP Server - Windows Setup
echo ====================================
echo.

set SCRIPT_DIR=%~dp0..
cd /d "%SCRIPT_DIR%"

echo Setting up Immanuel MCP Server in: %CD%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found in PATH
    echo Please install Python 3.11+ from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found

REM Check if uv is available, install if not
where uv >nul 2>&1
if errorlevel 1 (
    echo ⚠️  uv not found. Installing uv...
    python -m pip install uv
    if errorlevel 1 (
        echo ❌ Failed to install uv
        pause
        exit /b 1
    )
    echo ✅ uv installed successfully
) else (
    echo ✅ uv already available
)

REM Create virtual environment
echo.
echo Creating virtual environment...
if exist ".venv" (
    echo Virtual environment already exists, recreating...
    rmdir /s /q .venv
)

uv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment created

REM Install dependencies
echo.
echo Installing dependencies...
uv pip install -e .
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed successfully

REM Create environment file
echo.
if not exist ".env" (
    echo Creating environment configuration...
    copy .env.example .env >nul
    echo ✅ Environment file created (.env)
) else (
    echo ✅ Environment file already exists
)

REM Test the installation
echo.
echo Testing installation...
call .venv\Scripts\activate.bat
python -c "import app; print('✅ App imports successfully')" 2>nul
if errorlevel 1 (
    echo ❌ Installation test failed
    pause
    exit /b 1
)

REM Display configuration instructions
echo.
echo ====================================
echo Setup Complete! 🎉
echo ====================================
echo.
echo Your Immanuel MCP Server is ready to use.
echo.
echo Project path: %CD%
echo.
echo Next steps:
echo 1. Copy the project path above
echo 2. Open Claude Desktop
echo 3. Go to Settings ^> Developer ^> Edit Config
echo 4. Add this configuration:
echo.
echo {
echo   "mcpServers": {
echo     "immanuel-astrology": {
echo       "command": "%CD%\\start_server.bat",
echo       "args": ["--no-pause"],
echo       "cwd": "%CD%"
echo     }
echo   }
echo }
echo.
echo 5. Save and restart Claude Desktop
echo 6. Test with: "Generate a natal chart for May 15, 1990 at 2:30 PM in Los Angeles"
echo.
echo Helpful commands:
echo - Test server: start_server.bat
echo - Verify setup: scripts\verify_windows_install.bat
echo - Documentation: docs\windows_setup.md
echo.
echo Have fun exploring astrology with AI! ✨
echo.
pause