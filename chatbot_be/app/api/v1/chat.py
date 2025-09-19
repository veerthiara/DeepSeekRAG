"""
Chat endpoints for conversational AI.
Main interface for the intelligent chatbot with session management.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
from datetime import datetime

from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.session import FeedbackRequest, FeedbackResponse, SessionStatsResponse
from app.core.exceptions import ChatbotBaseException
from app.services.conversational_service import ConversationalService
from app.services.rag_service import RAGService

router = APIRouter(tags=["Chat"])
logger = logging.getLogger(__name__)

# Initialize services
conversational_service = None

def get_conversational_service() -> ConversationalService:
    """Get or create the conversational service."""
    global conversational_service
    if not conversational_service:
        from app.api.server import get_rag_service
        rag_service = get_rag_service()
        conversational_service = ConversationalService(rag_service)
    return conversational_service

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Main chat endpoint for conversational AI.
    Handles session management, query routing, and intelligent responses.
    """
    try:
        # Get conversational service
        conv_service = get_conversational_service()
        
        # Process the question
        result = await conv_service.ask_question(
            question=request.question,
            session_id=request.session_id,
            user_preferences=request.user_preferences or {}
        )
        
        # Convert ConversationalResponse to ChatResponse
        return ChatResponse(
            answer=result.answer,
            confidence=result.confidence,
            query_type_used=result.query_type_used,
            session_id=result.session_id,
            reasoning=result.reasoning,
            sources=result.sources,
            sql_query=result.sql_query,
            suggested_followups=result.suggested_followups,
            clarification_needed=result.clarification_needed,
            conversation_summary=result.conversation_summary,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        # Return a friendly error response instead of raising HTTPException
        return ChatResponse(
            answer=f"I apologize, but I encountered an error processing your request: {str(e)}",
            confidence=0.0,
            query_type_used="ERROR",
            session_id=request.session_id or "error_session",
            reasoning="Error occurred during processing",
            sources=["Error handler"],
            sql_query=None,
            suggested_followups=["Please try rephrasing your question"],
            clarification_needed=None,
            conversation_summary="Error occurred",
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

@router.post("/chat/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for a chat interaction.
    Helps improve the AI's responses over time.
    """
    try:
        # TODO: Implement feedback storage
        
        return FeedbackResponse(
            success=True,
            message="Thank you for your feedback! (Currently in development)",
            feedback_id=f"fb_{request.session_id}_{int(datetime.utcnow().timestamp())}"
        )
        
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/session/{session_id}", response_model=SessionStatsResponse)
async def get_session_stats(session_id: str):
    """
    Get statistics and information about a chat session.
    """
    try:
        # TODO: Implement session stats retrieval
        
        return SessionStatsResponse(
            session_id=session_id,
            created_at=datetime.utcnow().isoformat() + "Z",
            last_activity=datetime.utcnow().isoformat() + "Z",
            total_interactions=0,
            query_types_used={},
            user_preferences={}
        )
        
    except Exception as e:
        logger.error(f"Session stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))