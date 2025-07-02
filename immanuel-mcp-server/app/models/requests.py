"""
Request and response models for API endpoints.

This module defines Pydantic models for HTTP request/response handling,
validation, and serialization.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class HealthResponse(BaseModel):
    """Health check response."""
    model_config = ConfigDict(extra="forbid")
    
    status: str = "healthy"
    timestamp: str
    version: str
    uptime: float


class ErrorResponse(BaseModel):
    """Standard error response."""
    model_config = ConfigDict(extra="forbid")
    
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str


class ValidationErrorDetail(BaseModel):
    """Validation error detail."""
    model_config = ConfigDict(extra="forbid")
    
    field: str
    message: str
    type: str
    input: Any


class ValidationErrorResponse(BaseModel):
    """Validation error response."""
    model_config = ConfigDict(extra="forbid")
    
    error: str = "validation_error"
    message: str = "Request validation failed"
    details: List[ValidationErrorDetail]
    timestamp: str


class APIResponse(BaseModel):
    """Generic API response wrapper."""
    model_config = ConfigDict(extra="forbid")
    
    success: bool = True
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None
    timestamp: str


class ServerInfoResponse(BaseModel):
    """Server information response."""
    model_config = ConfigDict(extra="forbid")
    
    name: str
    version: str
    protocol_version: str
    description: str
    capabilities: List[str]
    supported_chart_types: List[str]
    supported_house_systems: List[str]
    supported_objects: List[str]