"""
FastAPI application server setup.
Main entry point for the DeepSeek RAG Chatbot API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from app.core.config import settings
from app.core.cors import setup_cors
from app.core.exceptions import ChatbotBaseException
from app.api.v1 import chat, health, rag, sql
from app.services.rag_service import RAGService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track application startup time
app_start_time = time.time()

def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        description="Intelligent chatbot with RAG and SQL capabilities",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Setup CORS
    setup_cors(app)
    
    # Include API routers
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(chat.router, prefix="/api/v1")
    app.include_router(rag.router, prefix="/api/v1")
    app.include_router(sql.router, prefix="/api/v1")
    
    return app

# Create application instance
app = create_application()

# Global services
rag_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global rag_service
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    try:
        # Initialize RAG service
        rag_service = RAGService()
        await rag_service.initialize()
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down application")

@app.exception_handler(ChatbotBaseException)
async def chatbot_exception_handler(request, exc: ChatbotBaseException):
    """Handle custom chatbot exceptions."""
    return HTTPException(
        status_code=500,
        detail={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details
        }
    )

@app.get("/")
async def root():
    """Root endpoint with basic application info."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "uptime": time.time() - app_start_time
    }

# Make services available to other modules
def get_rag_service() -> RAGService:
    """Get the global RAG service instance."""
    return rag_service