"""
Health check endpoints for the Immanuel MCP Server.

This module provides health and readiness checks for monitoring
and load balancer integration.
"""

import time
from datetime import datetime

from fastapi import APIRouter, Depends

from app.config import get_settings, Settings
from app.models.requests import HealthResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Track server start time for uptime calculation
start_time = time.time()


@router.get("/", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """
    Basic health check endpoint.
    
    Returns server status and basic information.
    """
    uptime = time.time() - start_time
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version=settings.mcp_server_version,
        uptime=uptime
    )


@router.get("/ready", response_model=HealthResponse)
async def readiness_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """
    Readiness check endpoint.
    
    Performs deeper checks to ensure the server is ready to serve requests.
    This could include checking dependencies, database connections, etc.
    """
    uptime = time.time() - start_time
    
    # In a real implementation, you might check:
    # - Database connectivity
    # - External service availability
    # - Required environment variables
    # - File system permissions
    
    try:
        # Basic check - ensure we can import immanuel
        import immanuel
        logger.debug("Immanuel library check passed", version=getattr(immanuel, '__version__', 'unknown'))
        
        return HealthResponse(
            status="ready",
            timestamp=datetime.utcnow().isoformat(),
            version=settings.mcp_server_version,
            uptime=uptime
        )
    except ImportError as e:
        logger.error("Readiness check failed", error=str(e))
        return HealthResponse(
            status="not_ready",
            timestamp=datetime.utcnow().isoformat(),
            version=settings.mcp_server_version,
            uptime=uptime
        )


@router.get("/liveness", response_model=HealthResponse)
async def liveness_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """
    Liveness check endpoint.
    
    Simple check to verify the server process is running.
    Used by orchestrators to determine if the container should be restarted.
    """
    uptime = time.time() - start_time
    
    return HealthResponse(
        status="alive",
        timestamp=datetime.utcnow().isoformat(),
        version=settings.mcp_server_version,
        uptime=uptime
    )