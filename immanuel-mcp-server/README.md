# Immanuel MCP Server

A high-performance Python MCP (Model Context Protocol) server for the `theriftlab/immanuel-python` astrology library, designed for seamless integration with Claude Desktop and other MCP-compatible AI applications.

## Features

- **Complete MCP Protocol Support**: Full implementation of MCP v2024-11-05 specification
- **Comprehensive Astrological Tools**: Generate natal charts, progressions, solar returns, composites, and synastry
- **Rich Resource Library**: Access to astrological reference data including planets, signs, houses, and aspects
- **Intelligent Prompts**: Pre-built templates for astrological interpretations and reports
- **High Performance**: Built with FastAPI and async/await for optimal performance
- **Type Safety**: Fully typed with comprehensive type hints and Pydantic validation
- **Extensive Testing**: >90% test coverage with unit and integration tests

## Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd immanuel-mcp-server
   ```

2. **Install dependencies using uv:**
   
   **Linux/macOS:**
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e .
   ```
   
   **Windows:**
   ```cmd
   uv venv
   .venv\Scripts\activate
   uv pip install -e .
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the server:**
   
   **Linux/macOS:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   
   **Windows:**
   ```cmd
   # Option 1: Use the batch script
   start_server.bat
   
   # Option 2: Direct command
   .venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Windows Quick Setup

For Windows users, we provide additional scripts and documentation:

1. **Quick verification**: Run `scripts\verify_windows_install.bat` to check your setup
2. **Easy startup**: Use `start_server.bat` to start the server with automatic environment handling
3. **Detailed guide**: See [Windows Setup Guide](docs/windows_setup.md) for complete instructions
4. **PowerShell support**: Use `start_server.ps1` for PowerShell users

## MCP Integration

### Claude Desktop Configuration

#### For Linux/macOS

Add the following to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "immanuel-astrology": {
      "command": "uvicorn",
      "args": ["app.main:app", "--host", "127.0.0.1", "--port", "8000"],
      "cwd": "/path/to/immanuel-mcp-server"
    }
  }
}
```

#### For Windows

**Option 1: Using Batch Script (Recommended)**
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

**Option 2: Using Full Path to uvicorn**
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

**Option 3: Using Python Module**
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

> **Windows Users**: Replace `C:\\path\\to\\immanuel-mcp-server` with your actual project path. See [Windows Setup Guide](docs/windows_setup.md) for detailed instructions.

### Available Tools

| Tool | Description |
|------|-------------|
| `generate_natal_chart` | Generate a complete natal chart with planets, houses, and aspects |
| `generate_progressed_chart` | Create a progressed chart for personal evolution analysis |
| `generate_solar_return` | Generate solar return charts for yearly forecasts |
| `generate_composite_chart` | Create relationship composite charts |
| `calculate_synastry` | Perform compatibility analysis between two charts |
| `get_transits` | Calculate current planetary transits |
| `interpret_aspects` | Get detailed aspect interpretations |
| `calculate_dignities` | Calculate essential dignities for planets |

### Resources

Access astrological reference data:

- `astrological_objects` - Planets, asteroids, and points
- `house_systems` - Available house calculation systems
- `aspect_patterns` - Aspect types and orbs
- `sign_meanings` - Zodiac sign interpretations
- `planet_meanings` - Planetary symbolism
- `house_meanings` - Astrological house meanings

### Prompts

Pre-built interpretation templates:

- `natal_chart_interpretation` - Comprehensive birth chart analysis
- `transit_report` - Current planetary movement analysis
- `compatibility_analysis` - Relationship compatibility assessment
- `progression_forecast` - Personal evolution forecast

## API Usage Examples

### Generate a Natal Chart

```json
{
  "name": "generate_natal_chart",
  "arguments": {
    "date_time": "1990-05-15 14:30:00",
    "latitude": "32n43",
    "longitude": "117w09",
    "timezone": "America/Los_Angeles",
    "house_system": "placidus"
  }
}
```

### Calculate Synastry

```json
{
  "name": "calculate_synastry",
  "arguments": {
    "person1": {
      "date_time": "1990-05-15 14:30:00",
      "coordinates": {
        "latitude": "32n43",
        "longitude": "117w09"
      }
    },
    "person2": {
      "date_time": "1992-08-22 10:15:00", 
      "coordinates": {
        "latitude": "40n45",
        "longitude": "73w59"
      }
    }
  }
}
```

### Get Resource Data

```json
{
  "uri": "astrological_objects"
}
```

## Configuration

The server can be configured via environment variables or `.env` file:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development

# MCP Configuration
MCP_SERVER_NAME=immanuel-astrology
MCP_SERVER_VERSION=1.0.0

# Astrology Configuration
DEFAULT_HOUSE_SYSTEM=placidus
DEFAULT_OBJECTS=sun,moon,mercury,venus,mars,jupiter,saturn,uranus,neptune,pluto
DEFAULT_ASPECT_ORB=8.0

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest -m unit
pytest -m integration
```

### Code Quality

```bash
# Format code
black app/ tests/
isort app/ tests/

# Lint code
ruff app/ tests/

# Type checking
mypy app/
```

### Development Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Deployment

### Docker

```bash
# Build image
docker build -t immanuel-mcp-server .

# Run container
docker run -p 8000:8000 immanuel-mcp-server
```

### Production

For production deployment, consider:

- Use a production ASGI server like Gunicorn with Uvicorn workers
- Set up proper logging and monitoring
- Configure SSL/TLS termination
- Set appropriate rate limiting
- Use environment-specific configuration

## Architecture

The server is built with a modular architecture:

```
app/
├── main.py              # FastAPI application
├── config.py            # Configuration management
├── models/              # Pydantic data models
│   ├── mcp.py          # MCP protocol models
│   ├── astrology.py    # Astrological data models
│   └── requests.py     # API request/response models
├── services/            # Business logic layer
│   ├── mcp_service.py  # MCP protocol handling
│   ├── chart_service.py # Chart generation
│   └── validation.py   # Input validation
├── routes/              # API endpoints
│   ├── mcp.py          # MCP protocol routes
│   └── health.py       # Health check routes
└── utils/               # Utilities
    ├── logging.py      # Structured logging
    └── exceptions.py   # Custom exceptions
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure code quality checks pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Windows Issues

**"uvicorn is not recognized"**
- Use the batch script: `start_server.bat`
- Or use full path: `C:\path\to\.venv\Scripts\uvicorn.exe`
- Or use Python module: `python -m uvicorn app.main:app`

**Claude Desktop connection fails**
- Verify paths in configuration use double backslashes: `C:\\path\\to\\project`
- Run verification: `scripts\verify_windows_install.bat`
- Check Claude Desktop logs in `%APPDATA%\Claude\logs\`

**Virtual environment issues**
- Delete `.venv` and recreate: `uv venv && uv pip install -e .`
- Ensure uv is installed: `pip install uv`

See [Windows Setup Guide](docs/windows_setup.md) for detailed troubleshooting.

### General Issues

**Port already in use**
- Change port in configuration
- Kill existing process: `taskkill /f /im uvicorn.exe` (Windows) or `pkill uvicorn` (Linux/macOS)

**Import errors**
- Reinstall dependencies: `uv pip install -e .`
- Check Python version: `python --version` (needs 3.11+)

**Permission denied**
- Run as administrator (Windows) or use `sudo` (Linux/macOS)
- Check file permissions in project directory

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review the test suite for usage examples
- Windows users: See [Windows Setup Guide](docs/windows_setup.md)

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Immanuel](https://github.com/theriftlab/immanuel-python) astrology library
- Implements [Model Context Protocol](https://modelcontextprotocol.io/) specification