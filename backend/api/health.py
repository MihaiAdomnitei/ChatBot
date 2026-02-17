"""
Health Router - API endpoints for health checks and monitoring.

Endpoints:
- GET /health - Basic health check
- GET /health/ready - Readiness check (model loaded)
- GET /health/live - Liveness check (API responsive)
"""

import time
from typing import Annotated, Optional
from fastapi import APIRouter, Depends

from ai import PatientChatEngine
from api.schemas import HealthResponse
from api.dependencies import get_engine_optional


# Store startup time for uptime calculation
_startup_time: Optional[float] = None

def set_startup_time():
    """Set the startup time when the application starts."""
    global _startup_time
    _startup_time = time.time()

def get_uptime() -> Optional[float]:
    """Get the uptime in seconds since startup."""
    if _startup_time is None:
        return None
    return time.time() - _startup_time


# Create router
router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


# Type alias for optional engine dependency
EngineOptionalDep = Annotated[Optional[PatientChatEngine], Depends(get_engine_optional)]


# ============================================
# Endpoints
# ============================================

@router.get(
    "",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the overall health status of the API including model status."
)
async def health_check(
    engine: EngineOptionalDep
) -> HealthResponse:
    """
    Comprehensive health check endpoint.

    Returns:
    - status: 'healthy' if everything is working, 'degraded' if model not loaded
    - model_loaded: Whether the AI model is ready
    - version: API version
    - uptime_seconds: Server uptime
    """
    model_loaded = engine is not None
    status = "healthy" if model_loaded else "degraded"

    return HealthResponse(
        status=status,
        model_loaded=model_loaded,
        version="1.0.0",
        uptime_seconds=get_uptime()
    )


@router.get(
    "/ready",
    response_model=HealthResponse,
    summary="Readiness check",
    description="Checks if the API is ready to serve requests (model loaded)."
)
async def readiness_check(
    engine: EngineOptionalDep
) -> HealthResponse:
    """
    Readiness probe for Kubernetes/container orchestration.

    Returns healthy only if the model is loaded and ready.
    """
    model_loaded = engine is not None
    status = "ready" if model_loaded else "not_ready"

    return HealthResponse(
        status=status,
        model_loaded=model_loaded,
        version="1.0.0",
        uptime_seconds=get_uptime()
    )


@router.get(
    "/live",
    response_model=HealthResponse,
    summary="Liveness check",
    description="Checks if the API process is alive and responding."
)
async def liveness_check(
    engine: EngineOptionalDep
) -> HealthResponse:
    """
    Liveness probe for Kubernetes/container orchestration.

    Returns healthy as long as the API can respond.
    """
    return HealthResponse(
        status="alive",
        model_loaded=engine is not None,
        version="1.0.0",
        uptime_seconds=get_uptime()
    )

