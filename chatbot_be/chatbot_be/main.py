"""
main.py
Entry point for the FastAPI application.
"""

from fastapi import FastAPI, HTTPException
from chatbot_be.db import get_db_pool
from chatbot_be.routers import customers

app = FastAPI(title="DeepSeek RAG Chatbot Backend")

# Include routers for modular endpoints
app.include_router(customers.router)

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    await get_db_pool()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    pool = await get_db_pool()
    await pool.close()
