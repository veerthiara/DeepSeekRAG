"""
conversational_router.py
API endpoints for the new conversational AI system.
Provides session-aware, intelligent query routing with enhanced responses.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from ..rag.conversational_service import ConversationalService, ConversationalResponse
from ..rag.rag_service import RAGService

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/chat", tags=["Conversational AI"])

# Pydantic models for request/response
class ChatRequest(BaseModel):
    """Request model for chat interactions."""
    question: str = Field(..., description="User's question or message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    user_preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="User preferences for response style, length, etc."
    )

class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    answer: str = Field(..., description="AI's response to the user's question")
    confidence: float = Field(..., description="Confidence score (0-1) for the response")
    query_type_used: str = Field(..., description="Type of processing used (RAG/SQL/HYBRID/CLARIFICATION)")
    session_id: str = Field(..., description="Session ID for this conversation")
    reasoning: str = Field(..., description="Explanation of why this approach was chosen")
    sources: List[str] = Field(..., description="Sources used to generate the response")
    sql_query: Optional[str] = Field(None, description="SQL query used (if applicable)")
    suggested_followups: List[str] = Field(..., description="Suggested follow-up questions")
    clarification_needed: Optional[str] = Field(None, description="Clarification request if question is ambiguous")
    conversation_summary: str = Field(..., description="Summary of recent conversation")
    timestamp: str = Field(..., description="Response timestamp")

class SessionStatsResponse(BaseModel):
    """Response model for session statistics."""
    session_id: str
    created_at: str
    last_activity: str
    total_interactions: int
    current_context: Dict[str, Any]
    conversation_summary: str

class GlobalStatsResponse(BaseModel):
    """Response model for global system statistics."""
    active_sessions: int
    query_statistics: Dict[str, int]
    system_status: str

# Initialize services (these will be properly injected in production)
rag_service = None
conversational_service = None

def get_conversational_service() -> ConversationalService:
    """
    Dependency to get the conversational service instance.
    In production, this would be properly initialized with dependency injection.
    """
    global conversational_service, rag_service
    
    if conversational_service is None:
        # Initialize services if not already done
        if rag_service is None:
            from ..rag.rag_service import RAGService
            rag_service = RAGService()
        
        # Create the conversational service
        conversational_service = ConversationalService(rag_service)
    
    return conversational_service

@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    conv_service: ConversationalService = Depends(get_conversational_service)
) -> ChatResponse:
    """
    Ask a question to the conversational AI system.
    
    This endpoint provides intelligent, context-aware responses by:
    1. Analyzing the question to determine optimal processing approach
    2. Maintaining conversation history and context
    3. Routing to appropriate AI services (RAG, SQL, or hybrid)
    4. Providing suggestions for follow-up questions
    
    Args:
        request: ChatRequest containing the question and optional session info
        conv_service: Injected conversational service instance
        
    Returns:
        ChatResponse with complete answer and metadata
        
    Raises:
        HTTPException: If processing fails or invalid request
    """
    try:
        # Validate input
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Log the incoming request
        logger.info(f"Received question: {request.question[:100]}... (Session: {request.session_id})")
        
        # Process the question through conversational service
        response: ConversationalResponse = await conv_service.ask_question(
            question=request.question,
            session_id=request.session_id,
            user_preferences=request.user_preferences
        )
        
        # Convert to API response format
        chat_response = ChatResponse(**response.to_dict())
        
        # Log the response type and confidence
        logger.info(f"Generated {chat_response.query_type_used} response with confidence {chat_response.confidence:.2f}")
        
        return chat_response
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process question: {str(e)}"
        )

@router.post("/clarify", response_model=ChatResponse)
async def provide_clarification(
    request: ChatRequest,
    conv_service: ConversationalService = Depends(get_conversational_service)
) -> ChatResponse:
    """
    Provide clarification or follow-up information for a previous question.
    
    This endpoint is specifically designed for handling clarifications
    and follow-up questions in an ongoing conversation.
    
    Args:
        request: ChatRequest with clarification and session_id
        conv_service: Injected conversational service instance
        
    Returns:
        ChatResponse with clarified answer
    """
    if not request.session_id:
        raise HTTPException(
            status_code=400, 
            detail="Session ID is required for clarifications"
        )
    
    return await ask_question(request, conv_service)

@router.get("/session/{session_id}/stats", response_model=SessionStatsResponse)
async def get_session_stats(
    session_id: str,
    conv_service: ConversationalService = Depends(get_conversational_service)
) -> SessionStatsResponse:
    """
    Get statistics and information about a specific conversation session.
    
    Args:
        session_id: The session identifier
        conv_service: Injected conversational service instance
        
    Returns:
        SessionStatsResponse with session details
        
    Raises:
        HTTPException: If session not found
    """
    try:
        stats = conv_service.get_session_statistics(session_id)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return SessionStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session statistics: {str(e)}"
        )

@router.get("/session/{session_id}/history")
async def get_session_history(
    session_id: str,
    limit: int = 10,
    conv_service: ConversationalService = Depends(get_conversational_service)
) -> Dict[str, Any]:
    """
    Get conversation history for a specific session.
    
    Args:
        session_id: The session identifier
        limit: Maximum number of interactions to return
        conv_service: Injected conversational service instance
        
    Returns:
        Dictionary containing conversation history
    """
    try:
        session = conv_service.session_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get recent history
        history = session.conversation_history[-limit:] if limit > 0 else session.conversation_history
        
        return {
            "session_id": session_id,
            "total_interactions": len(session.conversation_history),
            "returned_interactions": len(history),
            "history": [
                {
                    "timestamp": interaction["timestamp"].isoformat(),
                    "question": interaction["question"],
                    "answer": interaction["answer"],
                    "query_type": interaction["query_type"],
                    "metadata": interaction["metadata"]
                }
                for interaction in history
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session history: {str(e)}"
        )

@router.delete("/session/{session_id}")
async def end_session(
    session_id: str,
    conv_service: ConversationalService = Depends(get_conversational_service)
) -> Dict[str, str]:
    """
    Manually end a conversation session.
    
    Args:
        session_id: The session identifier to end
        conv_service: Injected conversational service instance
        
    Returns:
        Confirmation message
    """
    try:
        if session_id in conv_service.session_manager.sessions:
            del conv_service.session_manager.sessions[session_id]
            return {"message": f"Session {session_id} ended successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to end session: {str(e)}"
        )

@router.get("/stats", response_model=GlobalStatsResponse)
async def get_global_stats(
    conv_service: ConversationalService = Depends(get_conversational_service)
) -> GlobalStatsResponse:
    """
    Get global system statistics and health information.
    
    Args:
        conv_service: Injected conversational service instance
        
    Returns:
        GlobalStatsResponse with system statistics
    """
    try:
        stats = conv_service.get_global_statistics()
        return GlobalStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error getting global stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get global statistics: {str(e)}"
        )

class FeedbackRequest(BaseModel):
    """Request model for feedback submission."""
    session_id: str = Field(..., description="Session identifier")
    interaction_index: int = Field(..., description="Index of the interaction to rate")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    comment: Optional[str] = Field(None, description="Optional feedback comment")

@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    conv_service: ConversationalService = Depends(get_conversational_service)
) -> Dict[str, str]:
    """
    Submit feedback for a specific interaction.
    
    This endpoint allows users to rate responses and provide feedback
    for continuous improvement of the AI system.
    
    Args:
        request: FeedbackRequest with session info and feedback details
        conv_service: Injected conversational service instance
        
    Returns:
        Confirmation message
    """
    try:
        session = conv_service.session_manager.get_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if request.interaction_index >= len(session.conversation_history):
            raise HTTPException(status_code=400, detail="Invalid interaction index")
        
        # Add feedback to the interaction metadata
        interaction = session.conversation_history[request.interaction_index]
        if "feedback" not in interaction["metadata"]:
            interaction["metadata"]["feedback"] = {}
        
        interaction["metadata"]["feedback"].update({
            "rating": request.rating,
            "comment": request.comment,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Feedback submitted for session {request.session_id}, interaction {request.interaction_index}: {request.rating}/5")
        
        return {"message": "Feedback submitted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit feedback: {str(e)}"
        )