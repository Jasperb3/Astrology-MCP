"""
Custom exceptions for the Immanuel MCP Server.

This module defines application-specific exceptions with proper error codes
and messages for different error scenarios.
"""

from typing import Any, Dict, Optional


class ImmanuelMCPError(Exception):
    """Base exception for all Immanuel MCP Server errors."""
    
    def __init__(
        self,
        message: str,
        error_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ImmanuelMCPError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code=400, details=details)


class ChartGenerationError(ImmanuelMCPError):
    """Raised when chart generation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code=422, details=details)


class MCPProtocolError(ImmanuelMCPError):
    """Raised when MCP protocol handling fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code=400, details=details)


class ToolNotFoundError(ImmanuelMCPError):
    """Raised when requested tool is not found."""
    
    def __init__(self, tool_name: str) -> None:
        message = f"Tool '{tool_name}' not found"
        super().__init__(message, error_code=404, details={"tool_name": tool_name})


class ResourceNotFoundError(ImmanuelMCPError):
    """Raised when requested resource is not found."""
    
    def __init__(self, resource_uri: str) -> None:
        message = f"Resource '{resource_uri}' not found"
        super().__init__(
            message, 
            error_code=404, 
            details={"resource_uri": resource_uri}
        )


class PromptNotFoundError(ImmanuelMCPError):
    """Raised when requested prompt is not found."""
    
    def __init__(self, prompt_name: str) -> None:
        message = f"Prompt '{prompt_name}' not found"
        super().__init__(
            message, 
            error_code=404, 
            details={"prompt_name": prompt_name}
        )


class ConfigurationError(ImmanuelMCPError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code=500, details=details)


class RateLimitExceededError(ImmanuelMCPError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, error_code=429)


class InternalServerError(ImmanuelMCPError):
    """Raised for internal server errors."""
    
    def __init__(self, message: str = "Internal server error") -> None:
        super().__init__(message, error_code=500)