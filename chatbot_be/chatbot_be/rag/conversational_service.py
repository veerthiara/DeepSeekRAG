"""
conversational_service.py
Main orchestrator for conversational AI that combines session management,
smart query routing, and context-aware responses.
"""

from typing import Dict, List, Optional, Any, Tuple
import asyncio
from datetime import datetime

from .session_manager import SessionManager, ConversationSession, session_manager
from .query_router import QueryRouter, QueryType, query_router
from .rag_service import RAGService
from .sql_client import ask_sql_agent

class ConversationalResponse:
    """
    Represents a complete response from the conversational AI system.
    Includes the answer, context, and suggestions for follow-up questions.
    """
    
    def __init__(self):
        self.answer: str = ""
        self.confidence: float = 0.0
        self.query_type_used: str = ""
        self.session_id: str = ""
        self.reasoning: str = ""
        self.sources: List[str] = []  # Context sources used
        self.sql_query: Optional[str] = None  # If SQL was used
        self.suggested_followups: List[str] = []
        self.clarification_needed: Optional[str] = None
        self.conversation_summary: str = ""
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for JSON serialization."""
        return {
            "answer": self.answer,
            "confidence": self.confidence,
            "query_type_used": self.query_type_used,
            "session_id": self.session_id,
            "reasoning": self.reasoning,
            "sources": self.sources,
            "sql_query": self.sql_query,
            "suggested_followups": self.suggested_followups,
            "clarification_needed": self.clarification_needed,
            "conversation_summary": self.conversation_summary,
            "timestamp": datetime.now().isoformat()
        }

class ConversationalService:
    """
    Main service that provides intelligent, context-aware responses to user questions.
    Manages conversation flow, routes queries appropriately, and maintains context.
    """
    
    def __init__(self, rag_service: RAGService):
        """
        Initialize the conversational service with required components.
        
        Args:
            rag_service: Service for vector search and RAG queries
        """
        self.session_manager = session_manager
        self.query_router = query_router
        self.rag_service = rag_service
        
        # Performance tracking
        self.query_stats = {
            "total_queries": 0,
            "rag_queries": 0,
            "sql_queries": 0,
            "hybrid_queries": 0,
            "clarification_requests": 0
        }
    
    async def ask_question(self, 
                          question: str, 
                          session_id: Optional[str] = None,
                          user_preferences: Optional[Dict[str, Any]] = None) -> ConversationalResponse:
        """
        Main entry point for asking questions to the conversational AI.
        
        Args:
            question: User's question
            session_id: Optional session ID for conversation continuity
            user_preferences: Optional user preferences (response length, detail level, etc.)
            
        Returns:
            ConversationalResponse with complete answer and context
        """
        # Initialize response object
        response = ConversationalResponse()
        
        # Get or create session
        session_id, session = self.session_manager.get_or_create_session(session_id)
        response.session_id = session_id
        response.conversation_summary = session.get_conversation_summary()
        
        # Clean up expired sessions periodically
        if self.query_stats["total_queries"] % 10 == 0:
            self.session_manager.cleanup_expired_sessions()
        
        try:
            # Analyze the query to determine best approach
            query_analysis = self.query_router.analyze_query(
                question, 
                session.current_context
            )
            
            response.reasoning = query_analysis["reasoning"]
            response.confidence = query_analysis["confidence"]
            response.suggested_followups = query_analysis["suggested_followups"]
            
            # Handle clarification requests
            if query_analysis["query_type"] == QueryType.CLARIFICATION:
                response.clarification_needed = query_analysis["clarification_needed"]
                response.answer = self._generate_clarification_response(query_analysis, session)
                response.query_type_used = "CLARIFICATION"
                self.query_stats["clarification_requests"] += 1
                
                # Don't add to session history yet - wait for clarification
                return response
            
            # Route the query to appropriate processor(s)
            if query_analysis["query_type"] == QueryType.RAG:
                response = await self._handle_rag_query(question, session, query_analysis, response)
                
            elif query_analysis["query_type"] == QueryType.SQL:
                response = await self._handle_sql_query(question, session, query_analysis, response)
                
            elif query_analysis["query_type"] == QueryType.HYBRID:
                response = await self._handle_hybrid_query(question, session, query_analysis, response)
            
            # Add interaction to session history
            session.add_interaction(
                question=question,
                answer=response.answer,
                query_type=response.query_type_used,
                metadata={
                    "confidence": response.confidence,
                    "sources": response.sources,
                    "sql_query": response.sql_query,
                    "entities": query_analysis["entities"]
                }
            )
            
            # Update statistics
            self.query_stats["total_queries"] += 1
            
            return response
            
        except Exception as e:
            # Handle errors gracefully
            response.answer = f"I encountered an error while processing your question: {str(e)}. Could you please rephrase your question?"
            response.confidence = 0.0
            response.query_type_used = "ERROR"
            response.reasoning = "Error occurred during processing"
            
            return response
    
    async def _handle_rag_query(self, question: str, session: ConversationSession, 
                               analysis: Dict[str, Any], response: ConversationalResponse) -> ConversationalResponse:
        """
        Handle questions that need vector search and contextual reasoning.
        """
        # Enhance question with conversation context if available
        enhanced_question = self._enhance_question_with_context(question, session)
        
        # Use RAG service to get answer
        rag_answer = await self.rag_service.answer_question(enhanced_question)
        
        response.answer = self._improve_rag_answer(rag_answer, session, analysis)
        response.query_type_used = "RAG"
        response.sources = ["Vector search results"]  # Could be enhanced to show actual sources
        
        self.query_stats["rag_queries"] += 1
        
        return response
    
    async def _handle_sql_query(self, question: str, session: ConversationSession,
                               analysis: Dict[str, Any], response: ConversationalResponse) -> ConversationalResponse:
        """
        Handle questions that need specific data from the database.
        """
        # Enhance question with context if needed
        enhanced_question = self._enhance_question_with_context(question, session)
        
        # Use SQL agent function to get answer
        sql_result = await ask_sql_agent(enhanced_question)
        
        response.answer = self._improve_sql_answer(sql_result, session, analysis)
        response.query_type_used = "SQL"
        response.sql_query = "SQL query executed"  # We don't get the query back from the function
        response.sources = ["Database query"]
        
        self.query_stats["sql_queries"] += 1
        
        return response
    
    async def _handle_hybrid_query(self, question: str, session: ConversationSession,
                                  analysis: Dict[str, Any], response: ConversationalResponse) -> ConversationalResponse:
        """
        Handle complex questions that benefit from both RAG and SQL approaches.
        """
        # Run both RAG and SQL in parallel for efficiency
        rag_task = self.rag_service.answer_question(question)
        sql_task = ask_sql_agent(question)
        
        try:
            # Wait for both results with timeout
            rag_result, sql_result = await asyncio.wait_for(
                asyncio.gather(rag_task, sql_task), 
                timeout=30.0
            )
            
            # Combine results intelligently
            combined_answer = self._combine_rag_sql_results(
                rag_result, sql_result, question, analysis
            )
            
            response.answer = combined_answer
            response.query_type_used = "HYBRID"
            response.sources = ["Vector search", "Database query"]
            response.sql_query = "SQL query executed"
            
            self.query_stats["hybrid_queries"] += 1
            
        except asyncio.TimeoutError:
            # Fallback to RAG if hybrid processing takes too long
            response.answer = await self.rag_service.answer_question(question)
            response.query_type_used = "RAG_FALLBACK"
            response.sources = ["Vector search (fallback)"]
            response.reasoning += " (Timeout occurred, used RAG fallback)"
        
        return response
    
    def _enhance_question_with_context(self, question: str, session: ConversationSession) -> str:
        """
        Enhance the user's question with relevant conversation context.
        This helps provide better answers by including recent conversation history.
        """
        if not session.conversation_history:
            return question
        
        # Get recent context
        recent_context = session.get_conversation_summary(last_n=2)
        
        # If the question uses pronouns or references, include context
        ambiguous_words = ["it", "that", "this", "them", "they", "also", "more"]
        if any(word in question.lower() for word in ambiguous_words):
            enhanced = f"Previous conversation:\n{recent_context}\n\nCurrent question: {question}"
            return enhanced
        
        return question
    
    def _improve_rag_answer(self, rag_answer: str, session: ConversationSession, 
                           analysis: Dict[str, Any]) -> str:
        """
        Improve RAG answers by adding conversational elements and context.
        """
        # Basic answer from RAG
        improved_answer = rag_answer
        
        # Add conversational tone
        if session.conversation_history:
            improved_answer = f"Building on our previous discussion, {rag_answer.lower()}"
        
        # Add entity-specific context if relevant
        entities = analysis.get("entities", [])
        if entities:
            entity_context = self._get_entity_context(entities)
            if entity_context:
                improved_answer += f"\n\n{entity_context}"
        
        return improved_answer
    
    def _improve_sql_answer(self, sql_answer: str, session: ConversationSession,
                           analysis: Dict[str, Any]) -> str:
        """
        Improve SQL answers by adding interpretation and context.
        """
        improved_answer = sql_answer
        
        # Add interpretation for numerical results
        if any(char.isdigit() for char in sql_answer):
            improved_answer += "\n\nLet me know if you'd like me to break down these numbers or explore related data!"
        
        # Suggest related queries based on entities
        entities = analysis.get("entities", [])
        if entities:
            suggestions = self._get_related_query_suggestions(entities)
            if suggestions:
                improved_answer += f"\n\nYou might also be interested in: {', '.join(suggestions)}"
        
        return improved_answer
    
    def _combine_rag_sql_results(self, rag_result: str, sql_result: str, 
                                question: str, analysis: Dict[str, Any]) -> str:
        """
        Intelligently combine results from both RAG and SQL approaches.
        """
        # If SQL found specific data, lead with that
        if sql_result and any(char.isdigit() for char in sql_result):
            combined = f"Based on the database query: {sql_result}\n\n"
            combined += f"For additional context: {rag_result}"
        else:
            # Lead with RAG for conceptual information
            combined = f"{rag_result}\n\n"
            if sql_result:
                combined += f"From the database: {sql_result}"
        
        return combined
    
    def _generate_clarification_response(self, analysis: Dict[str, Any], 
                                       session: ConversationSession) -> str:
        """
        Generate a helpful clarification response when the query is ambiguous.
        """
        clarification = analysis["clarification_needed"]
        
        # Add context from recent conversation if available
        if session.conversation_history:
            recent_topics = [
                interaction["metadata"].get("entities", []) 
                for interaction in session.conversation_history[-2:]
            ]
            flat_topics = [topic for sublist in recent_topics for topic in sublist]
            
            if flat_topics:
                unique_topics = list(set(flat_topics))
                clarification += f"\n\nWe were recently discussing: {', '.join(unique_topics)}"
        
        return clarification
    
    def _get_entity_context(self, entities: List[str]) -> str:
        """
        Get additional context information for detected entities.
        """
        context_map = {
            "products": "This database contains product information including categories, suppliers, and pricing.",
            "customers": "Customer data includes company information, contacts, and geographic details.",
            "orders": "Order information includes purchase details, dates, and customer relationships.",
            "employees": "Employee data covers staff information, territories, and reporting relationships."
        }
        
        contexts = [context_map.get(entity) for entity in entities if entity in context_map]
        return " ".join(contexts) if contexts else ""
    
    def _get_related_query_suggestions(self, entities: List[str]) -> List[str]:
        """
        Generate suggestions for related queries based on detected entities.
        """
        suggestions_map = {
            "products": ["product categories", "supplier information", "pricing analysis"],
            "customers": ["customer regions", "order history", "contact details"],
            "orders": ["order trends", "delivery information", "sales analysis"],
            "employees": ["territory assignments", "sales performance", "team structure"]
        }
        
        suggestions = []
        for entity in entities:
            if entity in suggestions_map:
                suggestions.extend(suggestions_map[entity])
        
        return suggestions[:3]  # Limit suggestions
    
    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics and summary for a specific session.
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        return {
            "session_id": session_id,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "total_interactions": len(session.conversation_history),
            "current_context": session.current_context,
            "conversation_summary": session.get_conversation_summary()
        }
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """
        Get overall system statistics.
        """
        return {
            "active_sessions": len(self.session_manager.sessions),
            "query_statistics": self.query_stats,
            "system_status": "operational"
        }