# Windows Setup Guide

Complete setup guide for running the Immanuel MCP Server on Windows with Claude Desktop.

## Prerequisites

### Required Software

1. **Python 3.11 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation
   - Verify: `python --version`

2. **uv Package Manager** (Recommended)
   - Install: `pip install uv`
   - Or use the installer: [uv installation guide](https://github.com/astral-sh/uv)
   - Verify: `uv --version`

3. **Git** (Optional, for cloning)
   - Download from [git-scm.com](https://git-scm.com/download/win)

### PowerShell Execution Policy

If using PowerShell scripts, you may need to allow script execution:

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Installation Methods

### Method 1: Using Batch Script (Recommended)

1. **Download/Clone the project**
   ```cmd
   git clone <repository-url>
   cd immanuel-mcp-server
   ```

2. **Run the setup**
   ```cmd
   # Create virtual environment and install dependencies
   uv venv
   uv pip install -e .
   ```

3. **Test the installation**
   ```cmd
   start_server.bat
   ```

### Method 2: Using PowerShell

1. **Download/Clone the project**
   ```powershell
   git clone <repository-url>
   cd immanuel-mcp-server
   ```

2. **Run the setup**
   ```powershell
   # Create virtual environment and install dependencies
   uv venv
   uv pip install -e .
   ```

3. **Test the installation**
   ```powershell
   .\start_server.ps1
   ```

### Method 3: Manual Setup

1. **Create virtual environment**
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```cmd
   pip install -e .
   ```

3. **Start server**
   ```cmd
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

## Claude Desktop Integration

### Configuration Location

Claude Desktop configuration file location:
```
%APPDATA%\Claude\claude_desktop_config.json
```

Typical full path:
```
C:\Users\{YourUsername}\AppData\Roaming\Claude\claude_desktop_config.json
```

### Configuration Options

#### Option 1: Using MCP-Compliant Script (Recommended)

```json
{
  "mcpServers": {
    "immanuel-astrology": {
      "command": "C:\\path\\to\\immanuel-mcp-server\\start_server_mcp.bat",
      "cwd": "C:\\path\\to\\immanuel-mcp-server"
    }
  }
}
```

#### Option 2: Using Regular Batch Script (Development)

```json
{
  "mcpServers": {
    "immanuel-astrology": {
      "command": "C:\\path\\to\\immanuel-mcp-server\\start_server.bat",
      "args": ["--no-pause"],
      "cwd": "C:\\path\\to\\immanuel-mcp-server"
    }
  }
}
```

#### Option 2: Using PowerShell

```json
{
  "mcpServers": {
    "immanuel-astrology": {
      "command": "powershell.exe",
      "args": [
        "-ExecutionPolicy", "Bypass",
        "-File", "C:\\path\\to\\immanuel-mcp-server\\start_server.ps1",
        "-NoPause"
      ],
      "cwd": "C:\\path\\to\\immanuel-mcp-server"
    }
  }
}
```

#### Option 3: Direct uvicorn (Full Path)

```json
{
  "mcpServers": {
    "immanuel-astrology": {
      "command": "C:\\path\\to\\immanuel-mcp-server\\.venv\\Scripts\\uvicorn.exe",
      "args": ["app.main:app", "--host", "127.0.0.1", "--port", "8000"],
      "cwd": "C:\\path\\to\\immanuel-mcp-server"
    }
  }
}
```

#### Option 4: Using Python Module

```json
{
  "mcpServers": {
    "immanuel-astrology": {
      "command": "C:\\path\\to\\immanuel-mcp-server\\.venv\\Scripts\\python.exe",
      "args": ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
      "cwd": "C:\\path\\to\\immanuel-mcp-server"
    }
  }
}
```

### Finding the Correct Path

To find your project path, run this in the project directory:

```cmd
echo %CD%
```

Or in PowerShell:
```powershell
Get-Location
```

## Troubleshooting

### Common Issues

#### 1. "uvicorn is not recognized"

**Problem**: `uvicorn` not found in PATH

**Solutions**:
- Use the batch script (`start_server.bat`) which handles virtual environment activation
- Use the full path to uvicorn: `C:\path\to\.venv\Scripts\uvicorn.exe`
- Use `python -m uvicorn` instead of direct `uvicorn`

#### 2. "Python is not recognized"

**Problem**: Python not in PATH

**Solutions**:
- Reinstall Python with "Add to PATH" option checked
- Add Python to PATH manually:
  - Add `C:\Users\{Username}\AppData\Local\Programs\Python\Python311\`
  - Add `C:\Users\{Username}\AppData\Local\Programs\Python\Python311\Scripts\`

#### 3. PowerShell Execution Policy

**Problem**: Cannot run PowerShell scripts

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 4. Virtual Environment Issues

**Problem**: Virtual environment not activating

**Solutions**:
- Delete `.venv` folder and recreate: `uv venv`
- Use absolute paths in Claude Desktop config
- Check that uv is properly installed

#### 5. Port Already in Use

**Problem**: Port 8000 is busy

**Solutions**:
- Kill the process using port 8000
- Use a different port in the configuration
- Check for other running servers

### Verification Commands

```cmd
# Check Python installation
python --version

# Check uv installation
uv --version

# Check if server starts
start_server.bat

# Test health endpoint
curl http://127.0.0.1:8000/health/
```

### Debug Mode

To run in debug mode for troubleshooting:

```cmd
# Batch script with debugging
start_server.bat

# PowerShell with debugging
.\start_server.ps1 -Reload

# Manual debug mode
.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload --log-level debug
```

## Performance Tips

### Virtual Environment Location

Keep virtual environments on the same drive as your project for better performance.

### Windows Defender

Add exclusions for:
- Project directory
- Python installation directory
- Virtual environment directory

### Antivirus Software

Some antivirus software may interfere with Python execution. Add exclusions if needed.

## Environment Variables

Create a `.env` file in the project root with Windows-specific settings:

```env
# Windows-specific settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
HOST=127.0.0.1
PORT=8000

# Windows paths (use forward slashes or double backslashes)
LOG_FILE=logs/immanuel.log
```

## Advanced Configuration

### Multiple Python Versions

If you have multiple Python versions, specify the exact version:

```cmd
# Use specific Python version with uv
uv venv --python python3.11
```

### Custom Installation Directory

```cmd
# Install to custom location
uv venv --location C:\custom\path\.venv
```

### Service Installation

To run as a Windows service, consider using:
- [NSSM (Non-Sucking Service Manager)](https://nssm.cc/)
- Python `python-windows-service` package
- Windows Task Scheduler

## Security Considerations

1. **Firewall**: Windows Firewall may block the server. Add an exception if needed.
2. **User Permissions**: Run with minimal required permissions.
3. **Network Access**: By default, server only listens on localhost (127.0.0.1).
4. **Virtual Environment**: Always use virtual environments to isolate dependencies.

## Getting Help

If you encounter issues:

1. Check the [main README](../README.md) for general setup
2. Run the verification script: `scripts\verify_windows_install.bat`
3. Check Claude Desktop logs in `%APPDATA%\Claude\logs\`
4. Enable debug logging in the server configuration
5. Create an issue on GitHub with:
   - Windows version
   - Python version
   - Error messages
   - Configuration used