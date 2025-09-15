"""
main.py
Entry point for the FastAPI application.
"""

from fastapi import FastAPI, HTTPException
from chatbot_be.db import get_db_pool
from chatbot_be.routers import customers, rag
from chatbot_be.rag.rag_service import rag_service

app = FastAPI(title="DeepSeek RAG Chatbot Backend")

# Include routers for modular endpoints
app.include_router(customers.router)
app.include_router(rag.router)

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    await get_db_pool()
    # Initialize RAG service in the background
    await rag_service.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    pool = await get_db_pool()
    await pool.close()
