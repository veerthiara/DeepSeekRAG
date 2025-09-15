"""
rag.py
Router for RAG-based question answering endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from chatbot_be.rag.rag_service import rag_service

router = APIRouter(prefix="/rag", tags=["rag"])

class QuestionRequest(BaseModel):
    """Request model for asking questions."""
    question: str

class QuestionResponse(BaseModel):
    """Response model for question answers."""
    question: str
    answer: str
    context: list[str]
    context_count: int

@router.post("/ask", response_model=QuestionResponse, summary="Ask a question using RAG")
async def ask_question(request: QuestionRequest):
    """
    Ask a question and get an answer using Retrieval-Augmented Generation.
    
    This endpoint:
    1. Takes your question
    2. Searches for relevant context in the product database
    3. Generates an answer based on the retrieved information
    
    Args:
        request: QuestionRequest containing the user's question
        
    Returns:
        QuestionResponse with the answer and context used
    """
    try:
        result = await rag_service.answer_question(request.question)
        return QuestionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@router.get("/health", summary="Check if RAG service is ready")
async def health_check():
    """
    Check if the RAG service is initialized and ready to answer questions.
    """
    return {
        "status": "ready" if rag_service.is_initialized else "initializing",
        "service": "RAG Question Answering"
    }