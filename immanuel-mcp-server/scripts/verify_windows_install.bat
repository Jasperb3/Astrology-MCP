@echo off
REM Immanuel MCP Server - Windows Installation Verification Script
REM This script verifies that the installation is correct and ready for Claude Desktop

echo ====================================
echo Immanuel MCP Server - Installation Verification
echo ====================================
echo.

set ERROR_COUNT=0
set SCRIPT_DIR=%~dp0..

REM Change to project directory
cd /d "%SCRIPT_DIR%"
echo Current directory: %CD%
echo.

REM 1. Check Python installation
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo   ❌ FAIL: Python not found in PATH
    echo      Solution: Install Python 3.11+ and add to PATH
    set /a ERROR_COUNT+=1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo   ✅ PASS: Python !PYTHON_VERSION! found
)
echo.

REM 2. Check uv installation
echo [2/8] Checking uv package manager...
where uv >nul 2>&1
if errorlevel 1 (
    echo   ⚠️  WARNING: uv not found in PATH
    echo      Fallback: Will use pip if needed
) else (
    for /f "tokens=2" %%i in ('uv --version 2^>^&1') do set UV_VERSION=%%i
    echo   ✅ PASS: uv !UV_VERSION! found
)
echo.

REM 3. Check virtual environment
echo [3/8] Checking virtual environment...
if not exist ".venv\Scripts\activate.bat" (
    echo   ❌ FAIL: Virtual environment not found
    echo      Solution: Run 'uv venv' to create virtual environment
    set /a ERROR_COUNT+=1
) else (
    echo   ✅ PASS: Virtual environment exists
)
echo.

REM 4. Check virtual environment activation
echo [4/8] Testing virtual environment activation...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    where python >nul 2>&1
    if errorlevel 1 (
        echo   ❌ FAIL: Cannot activate virtual environment
        set /a ERROR_COUNT+=1
    ) else (
        echo   ✅ PASS: Virtual environment activates correctly
    )
) else (
    echo   ⏭️  SKIP: No virtual environment to test
)
echo.

REM 5. Check uvicorn installation
echo [5/8] Checking uvicorn installation...
if exist ".venv\Scripts\uvicorn.exe" (
    echo   ✅ PASS: uvicorn executable found
) else (
    call .venv\Scripts\activate.bat 2>nul
    python -m uvicorn --version >nul 2>&1
    if errorlevel 1 (
        echo   ❌ FAIL: uvicorn not installed
        echo      Solution: Run 'uv pip install -e .' to install dependencies
        set /a ERROR_COUNT+=1
    ) else (
        echo   ✅ PASS: uvicorn available via python -m uvicorn
    )
)
echo.

REM 6. Check project dependencies
echo [6/8] Checking project dependencies...
call .venv\Scripts\activate.bat 2>nul
python -c "import app; print('✅ PASS: Main app module imports successfully')" 2>nul
if errorlevel 1 (
    echo   ❌ FAIL: Cannot import main app module
    echo      Solution: Run 'uv pip install -e .' to install dependencies
    set /a ERROR_COUNT+=1
)
echo.

REM 7. Test server startup (quick test)
echo [7/8] Testing server startup (5 second test)...
call .venv\Scripts\activate.bat 2>nul
start /b python -c "
import uvicorn
import sys
import os
sys.path.insert(0, os.getcwd())
try:
    from app.main import app
    print('✅ PASS: Server configuration is valid')
except Exception as e:
    print(f'❌ FAIL: Server startup error: {e}')
    sys.exit(1)
"
if errorlevel 1 (
    set /a ERROR_COUNT+=1
)
echo.

REM 8. Check startup scripts
echo [8/8] Checking startup scripts...
if exist "start_server.bat" (
    echo   ✅ PASS: start_server.bat exists
) else (
    echo   ❌ FAIL: start_server.bat not found
    set /a ERROR_COUNT+=1
)

if exist "start_server.ps1" (
    echo   ✅ PASS: start_server.ps1 exists
) else (
    echo   ⚠️  WARNING: start_server.ps1 not found
)
echo.

REM Summary
echo ====================================
echo Verification Summary
echo ====================================
if %ERROR_COUNT% EQU 0 (
    echo ✅ SUCCESS: All checks passed!
    echo.
    echo The Immanuel MCP Server is ready to use.
    echo.
    echo Next steps:
    echo 1. Copy your project path: %CD%
    echo 2. Configure Claude Desktop with one of these options:
    echo.
    echo    Option A - Batch Script (Recommended):
    echo    {
    echo      "mcpServers": {
    echo        "immanuel-astrology": {
    echo          "command": "%CD%\\start_server.bat",
    echo          "args": ["--no-pause"],
    echo          "cwd": "%CD%"
    echo        }
    echo      }
    echo    }
    echo.
    echo    Option B - Direct uvicorn:
    echo    {
    echo      "mcpServers": {
    echo        "immanuel-astrology": {
    echo          "command": "%CD%\\.venv\\Scripts\\uvicorn.exe",
    echo          "args": ["app.main:app", "--host", "127.0.0.1", "--port", "8000"],
    echo          "cwd": "%CD%"
    echo        }
    echo      }
    echo    }
    echo.
    echo 3. Restart Claude Desktop
    echo 4. Test with: "Generate a natal chart for someone born on 1990-05-15 at 2:30 PM in Los Angeles"
) else (
    echo ❌ FAILED: %ERROR_COUNT% issues found
    echo.
    echo Please fix the issues above before configuring Claude Desktop.
    echo.
    echo Common solutions:
    echo - Install Python 3.11+ from python.org
    echo - Install uv: pip install uv
    echo - Create virtual environment: uv venv
    echo - Install dependencies: uv pip install -e .
    echo.
    echo For detailed help, see: docs\windows_setup.md
)

echo.
echo Press any key to exit...
pause >nul