# Immanuel MCP Server - PowerShell Startup Script
# This script activates the virtual environment and starts the server

param(
    [switch]$NoPause,
    [string]$Host = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$Reload = $false
)

Write-Host "Starting Immanuel MCP Server..." -ForegroundColor Green

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found at .venv\Scripts\" -ForegroundColor Red
    Write-Host "Please run the following commands first:" -ForegroundColor Yellow
    Write-Host "  uv venv" -ForegroundColor White
    Write-Host "  uv pip install -e ." -ForegroundColor White
    
    if (-not $NoPause) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

# Function to check if command exists
function Test-Command($Command) {
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            return $true
        }
    }
    catch {
        return $false
    }
}

# Check execution policy
$executionPolicy = Get-ExecutionPolicy
if ($executionPolicy -eq "Restricted") {
    Write-Host "WARNING: PowerShell execution policy is Restricted." -ForegroundColor Yellow
    Write-Host "You may need to run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
}

try {
    # Activate virtual environment
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & ".venv\Scripts\Activate.ps1"
    
    # Check if uvicorn is available
    if (-not (Test-Command "uvicorn")) {
        Write-Host "uvicorn not found. Installing dependencies..." -ForegroundColor Yellow
        
        if (Test-Command "uv") {
            & uv pip install -e .
        } else {
            Write-Host "uv not found. Using pip..." -ForegroundColor Yellow
            & python -m pip install -e .
        }
        
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install dependencies"
        }
    }
    
    # Build uvicorn command
    $uvicornArgs = @(
        "app.main:app",
        "--host", $Host,
        "--port", $Port.ToString()
    )
    
    if ($Reload) {
        $uvicornArgs += "--reload"
    }
    
    Write-Host "Starting server on http://$($Host):$($Port)" -ForegroundColor Green
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    
    # Start the server
    & uvicorn @uvicornArgs
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    
    # Fallback to direct Python execution
    Write-Host "Trying fallback method..." -ForegroundColor Yellow
    try {
        $pythonArgs = @(
            "-m", "uvicorn",
            "app.main:app",
            "--host", $Host,
            "--port", $Port.ToString()
        )
        
        if ($Reload) {
            $pythonArgs += "--reload"
        }
        
        & ".venv\Scripts\python.exe" @pythonArgs
    }
    catch {
        Write-Host "FALLBACK FAILED: $($_.Exception.Message)" -ForegroundColor Red
        if (-not $NoPause) {
            Read-Host "Press Enter to exit"
        }
        exit 1
    }
}
finally {
    Write-Host "Server stopped." -ForegroundColor Yellow
    if (-not $NoPause) {
        Read-Host "Press Enter to exit"
    }
}