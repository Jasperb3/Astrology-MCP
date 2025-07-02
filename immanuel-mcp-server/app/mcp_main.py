"""
MCP-specific entry point for the Immanuel MCP Server.

This entry point is designed specifically for Model Context Protocol usage,
ensuring clean JSON-RPC communication without console output pollution.
"""

import os
import sys
import logging
from pathlib import Path

# Set MCP mode before importing other modules
os.environ["MCP_MODE"] = "true"
os.environ["PYTHONUNBUFFERED"] = "1"

import uvicorn
from app.main import app
from app.config import get_settings
from app.utils.logging import configure_logging


def setup_mcp_logging() -> None:
    """Configure logging specifically for MCP mode."""
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure file-only logging
    log_file = logs_dir / "mcp_server.log"
    
    # Set up basic file logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            # No console handler for MCP mode
        ],
        force=True  # Override any existing configuration
    )
    
    # Disable uvicorn console logging
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers = []
    uvicorn_logger.addHandler(logging.FileHandler(log_file))
    uvicorn_logger.propagate = False

    # Disable uvicorn access logs
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.handlers = []
    uvicorn_access.addHandler(logging.FileHandler(log_file))
    uvicorn_access.propagate = False

    # Disable uvicorn error logs
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.handlers = []
    uvicorn_error.addHandler(logging.FileHandler(log_file))
    uvicorn_error.propagate = False


def main() -> None:
    """Main entry point for MCP server."""
    try:
        # Set up MCP-specific logging
        setup_mcp_logging()
        
        # Get settings
        settings = get_settings()
        
        # Log startup to file only
        logger = logging.getLogger(__name__)
        logger.info(f"Starting Immanuel MCP Server in MCP mode on {settings.host}:{settings.port}")
        
        # Configure uvicorn for MCP mode
        config = uvicorn.Config(
            app=app,
            host=settings.host,
            port=settings.port,
            log_level="error",  # Minimal logging to console
            access_log=False,   # No access logs to console
            log_config=None,    # Disable default log config
            use_colors=False,   # No ANSI colors
        )
        
        # Create server
        server = uvicorn.Server(config)
        
        # Run server - this blocks and handles JSON-RPC over stdin/stdout
        server.run()
        
    except KeyboardInterrupt:
        # Clean shutdown on Ctrl+C
        logger.info("MCP server interrupted, shutting down")
        sys.exit(0)
    except Exception as e:
        # Log error to file
        logger = logging.getLogger(__name__)
        logger.error(f"MCP server failed to start: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()