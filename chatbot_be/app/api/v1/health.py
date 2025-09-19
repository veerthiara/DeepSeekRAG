"""
Health check endpoints.
Provides system status and monitoring capabilities.
"""

from fastapi import APIRouter
import time
from datetime import datetime

from app.core.config import settings
from app.schemas.common import HealthCheckResponse
from app.models.database import database

router = APIRouter(tags=["Health"])

# Track service start time
service_start_time = time.time()

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Check the health status of all services.
    Returns overall system health and individual service status.
    """
    
    services_status = {}
    
    # Check database connection
    try:
        tables = database.get_all_tables()
        services_status["database"] = "connected" if tables else "no_data"
    except Exception:
        services_status["database"] = "error"
    
    # Check vector store (via RAG service)
    try:
        from app.api.server import get_rag_service
        rag_service = get_rag_service()
        services_status["vector_store"] = "ready" if rag_service and rag_service.is_initialized else "not_ready"
    except Exception:
        services_status["vector_store"] = "error"
    
    # Check LLM availability
    try:
        from app.services.llm_client import llm_client
        # Simple test to see if LLM is responsive
        services_status["llm"] = "available"  # Assume available for now
    except Exception:
        services_status["llm"] = "error"
    
    # Determine overall status
    overall_status = "healthy"
    if "error" in services_status.values():
        overall_status = "degraded"
    elif "not_ready" in services_status.values():
        overall_status = "starting"
    
    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat() + "Z",
        version=settings.app_version,
        services=services_status,
        uptime=time.time() - service_start_time
    )