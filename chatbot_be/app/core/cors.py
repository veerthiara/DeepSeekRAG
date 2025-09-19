"""
CORS configuration for the FastAPI application.
Handles cross-origin resource sharing settings.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware for the FastAPI application."""
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )