"""
Common schemas used across the application.
Defines shared data structures and utility schemas.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class HealthCheckResponse(BaseModel):
    """Response model for health check endpoints."""
    status: str = Field(..., description="Overall service status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="Application version")
    services: Dict[str, str] = Field(..., description="Status of individual services")
    uptime: float = Field(..., description="Service uptime in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-09-18T10:30:00Z",
                "version": "1.0.0",
                "services": {
                    "database": "connected",
                    "vector_store": "ready",
                    "llm": "available"
                },
                "uptime": 3600.5
            }
        }

class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "The provided input is invalid",
                "details": {"field": "question", "issue": "cannot be empty"},
                "timestamp": "2025-09-18T10:30:00Z"
            }
        }