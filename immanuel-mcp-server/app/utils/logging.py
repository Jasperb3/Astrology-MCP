"""
Structured logging configuration for the Immanuel MCP Server.

This module sets up structured logging using structlog for consistent
and searchable log output across the application.
"""

import logging
import sys
import os
from pathlib import Path
from typing import Any, Dict

import structlog
from structlog.types import EventDict, Processor


def add_correlation_id(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add correlation ID to log entries if available."""
    # This could be enhanced to extract correlation IDs from request context
    return event_dict


def filter_sensitive_data(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Filter sensitive data from log entries."""
    sensitive_keys = {"password", "token", "api_key", "secret"}
    
    def _filter_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively filter sensitive keys from dictionary."""
        filtered = {}
        for key, value in d.items():
            if key.lower() in sensitive_keys:
                filtered[key] = "[REDACTED]"
            elif isinstance(value, dict):
                filtered[key] = _filter_dict(value)
            else:
                filtered[key] = value
        return filtered
    
    # Filter the event dict itself
    return _filter_dict(event_dict)


def configure_logging(log_level: str = "INFO", is_development: bool = True) -> None:
    """Configure structured logging for the application."""
    
    # Check if running in MCP mode
    mcp_mode = os.getenv("MCP_MODE", "false").lower() == "true"
    
    if mcp_mode:
        # MCP mode: File-only logging, no console output
        configure_mcp_logging(log_level)
        return
    
    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Define processors
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        add_correlation_id,
        filter_sensitive_data,
    ]
    
    if is_development:
        # Development: pretty console output
        processors.extend([
            structlog.dev.set_exc_info,
            structlog.dev.ConsoleRenderer(colors=True)
        ])
    else:
        # Production: JSON output
        processors.extend([
            structlog.processors.dict_tracebacks,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ])
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def configure_mcp_logging(log_level: str = "INFO") -> None:
    """Configure logging specifically for MCP mode (file-only, no console output)."""
    
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Set up file logging only
    log_file = logs_dir / "mcp_server.log"
    
    # Configure stdlib logging to file only
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode='a', encoding='utf-8')
        ],
        level=getattr(logging, log_level.upper()),
        force=True  # Override any existing configuration
    )
    
    # Define processors for file output (no colors, structured)
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        add_correlation_id,
        filter_sensitive_data,
        # Always use JSON output for MCP mode (easier to parse in logs)
        structlog.processors.dict_tracebacks,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
    
    # Configure structlog for file-only output
    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """Get a configured logger instance."""
    return structlog.get_logger(name)