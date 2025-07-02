# Immanuel MCP Server - Silent MCP-compliant PowerShell startup script
# This script provides ONLY JSON-RPC communication for Claude Desktop

param(
    [switch]$Test = $false
)

# Get script directory and change to project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Set MCP mode environment variables
$env:MCP_MODE = "true"
$env:PYTHONUNBUFFERED = "1"

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    if ($Test) {
        Write-Host "ERROR: Virtual environment not found" -ForegroundColor Red
        Write-Host "Please run: uv venv && uv pip install -e ." -ForegroundColor Yellow
    }
    exit 1
}

try {
    # Start the MCP server with no console output
    # All logs go to files, only JSON-RPC goes to stdout
    if ($Test) {
        Write-Host "Starting MCP server in test mode..." -ForegroundColor Green
        & ".venv\Scripts\python.exe" app\mcp_main.py
    } else {
        # Silent mode for Claude Desktop
        & ".venv\Scripts\python.exe" app\mcp_main.py
    }
}
catch {
    if ($Test) {
        Write-Host "ERROR: Failed to start MCP server: $($_.Exception.Message)" -ForegroundColor Red
    }
    exit 1
}