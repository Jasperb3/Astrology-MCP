"""
FastAPI application for the Immanuel MCP Server.

This module creates and configures the FastAPI application with all routes,
middleware, and error handling for the MCP server.
"""

import time
from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import ValidationError as PydanticValidationError

from app.config import get_settings, MCP_CAPABILITIES
from app.models.requests import (
    HealthResponse, 
    ErrorResponse, 
    ValidationErrorResponse,
    ValidationErrorDetail,
    ServerInfoResponse
)
from app.utils.logging import configure_logging, get_logger
from app.utils.exceptions import ImmanuelMCPError
from app.routes.mcp import router as mcp_router
from app.routes.health import router as health_router

# Configure logging
settings = get_settings()
configure_logging(settings.log_level, settings.is_development)
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Immanuel MCP Server",
    description="Model Context Protocol server for the Immanuel astrology library",
    version=settings.mcp_server_version,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

if not settings.is_development:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", settings.host]
    )

# Global variables for uptime tracking
start_time = time.time()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Any) -> Any:
    """Add request processing time to response headers."""
    start_time_req = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time_req
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log request
    logger.info(
        "Request processed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time
    )
    
    return response


@app.exception_handler(ImmanuelMCPError)
async def immanuel_mcp_error_handler(request: Request, exc: ImmanuelMCPError) -> JSONResponse:
    """Handle custom Immanuel MCP errors."""
    logger.error(
        "Immanuel MCP error",
        error=exc.message,
        error_code=exc.error_code,
        details=exc.details,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=exc.error_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.message,
            details=exc.details,
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )


@app.exception_handler(PydanticValidationError)
async def validation_error_handler(request: Request, exc: PydanticValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    details = [
        ValidationErrorDetail(
            field=".".join(str(x) for x in error["loc"]),
            message=error["msg"],
            type=error["type"],
            input=error.get("input")
        )
        for error in exc.errors()
    ]
    
    logger.warning(
        "Validation error",
        path=request.url.path,
        errors=exc.errors()
    )
    
    return JSONResponse(
        status_code=400,
        content=ValidationErrorResponse(
            details=details,
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.warning(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTPException",
            message=exc.detail,
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(
        "Unexpected error",
        error=str(exc),
        error_type=exc.__class__.__name__,
        path=request.url.path,
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred" if not settings.is_development else str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with server information."""
    uptime = time.time() - start_time
    
    return ServerInfoResponse(
        name=settings.mcp_server_name,
        version=settings.mcp_server_version,
        protocol_version=settings.mcp_protocol_version,
        description="Model Context Protocol server for the Immanuel astrology library",
        capabilities=list(MCP_CAPABILITIES.keys()),
        supported_chart_types=["natal", "progressed", "solar_return", "composite", "synastry", "transits"],
        supported_house_systems=["placidus", "koch", "porphyrius", "regiomontanus", "campanus", "equal", "whole_sign"],
        supported_objects=settings.default_objects_list
    ).model_dump()


# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(mcp_router, prefix="/mcp", tags=["mcp"])


@app.on_event("startup")
async def startup_event() -> None:
    """Application startup event."""
    logger.info(
        "Starting Immanuel MCP Server",
        version=settings.mcp_server_version,
        environment=settings.environment,
        host=settings.host,
        port=settings.port
    )


@app.on_event("shutdown") 
async def shutdown_event() -> None:
    """Application shutdown event."""
    logger.info("Shutting down Immanuel MCP Server")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload and settings.is_development,
        log_level=settings.log_level.lower(),
        access_log=settings.is_development
    )