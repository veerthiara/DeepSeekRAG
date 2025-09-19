"""
Main application entry point.
Runs the FastAPI server with proper configuration.
"""

import uvicorn
from app.api.server import app
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.api.server:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info"
    )