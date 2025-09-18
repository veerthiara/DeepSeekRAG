"""
query_router.py
Intelligently determines the best approach for answering user questions:
- RAG: For conceptual questions or when context is needed
- SQL: For specific data queries, counts, filters
- Hybrid: For complex questions requiring both approaches
"""

from typing import Dict, List, Optional, Tuple, Any
import re
from enum import Enum

class QueryType(Enum):
    """Enumeration of different query processing approaches."""
    RAG = "RAG"              # Vector search with LLM reasoning
    SQL = "SQL"              # Direct database queries
    HYBRID = "HYBRID"        # Combination of both approaches
    CLARIFICATION = "CLARIFICATION"  # Need more info from user

class QueryRouter:
    """
    Analyzes user questions and determines the optimal processing strategy.
    Uses pattern matching and keyword analysis to route queries intelligently.
    """
    
    def __init__(self):
        # Keywords that typically indicate SQL queries (specific data requests)
        self.sql_indicators = [
            # Counting keywords
            "how many", "count", "total", "number of", "sum", "average", "max", "min",
            
            # Filtering keywords  
            "where", "filter", "specific", "exactly", "precise", "show me all",
            
            # Comparison keywords
            "compare", "difference", "versus", "vs", "between", "greater than", "less than",
            
            # Data exploration keywords
            "list all", "show all", "find all", "get all", "top", "bottom", "highest", "lowest"
        ]
        
        # Keywords that typically indicate RAG queries (conceptual questions)
        self.rag_indicators = [
            # Conceptual keywords
            "what is", "explain", "describe", "tell me about", "how does", "why",
            
            # General information keywords
            "information about", "details about", "overview", "summary", "background",
            
            # Advice/recommendation keywords
            "recommend", "suggest", "advice", "should i", "best", "better", "ideal"
        ]
        
        # Keywords that might require clarification
        self.clarification_indicators = [
            "it", "that", "this", "them", "those", "these"  # Ambiguous references
        ]
        
        # Database entity keywords (help identify what data we're dealing with)
        self.entity_keywords = {
            "products": ["product", "item", "food", "beverage", "category", "supplier"],
            "customers": ["customer", "client", "buyer", "company", "contact"],
            "orders": ["order", "purchase", "sale", "transaction", "delivery"],
            "employees": ["employee", "staff", "worker", "manager"],
            "regions": ["region", "territory", "area", "location", "country", "city"]
        }
    
    def analyze_query(self, question: str, session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze a user question and determine the best processing approach.
        
        Args:
            question: The user's question
            session_context: Optional conversation context from current session
            
        Returns:
            Dict containing:
            - query_type: QueryType enum value
            - confidence: Float 0-1 indicating confidence in routing decision
            - reasoning: String explaining why this route was chosen
            - entities: List of detected entities (products, customers, etc.)
            - clarification_needed: Optional clarification questions
        """
        question_lower = question.lower().strip()
        
        # Clean the question (remove extra spaces, punctuation for analysis)
        clean_question = re.sub(r'[^\w\s]', ' ', question_lower)
        clean_question = re.sub(r'\s+', ' ', clean_question)
        
        # Initialize analysis result
        analysis = {
            "original_question": question,
            "query_type": QueryType.RAG,  # Default
            "confidence": 0.0,
            "reasoning": "",
            "entities": [],
            "clarification_needed": None,
            "suggested_followups": []
        }
        
        # Detect entities in the question
        detected_entities = self._detect_entities(clean_question)
        analysis["entities"] = detected_entities
        
        # Check for ambiguous references that might need clarification
        if self._needs_clarification(question_lower, session_context):
            analysis["query_type"] = QueryType.CLARIFICATION
            analysis["confidence"] = 0.8
            analysis["reasoning"] = "Question contains ambiguous references that need clarification"
            analysis["clarification_needed"] = self._generate_clarification(question_lower, session_context)
            return analysis
        
        # Score the question for different query types
        sql_score = self._calculate_sql_score(clean_question)
        rag_score = self._calculate_rag_score(clean_question)
        
        # Consider session context if available
        if session_context:
            sql_score, rag_score = self._adjust_scores_with_context(
                sql_score, rag_score, session_context, clean_question
            )
        
        # Determine query type based on scores
        if sql_score > rag_score and sql_score > 0.6:
            analysis["query_type"] = QueryType.SQL
            analysis["confidence"] = min(sql_score, 0.95)
            analysis["reasoning"] = f"Question appears to request specific data (SQL score: {sql_score:.2f})"
        elif rag_score > 0.7:
            analysis["query_type"] = QueryType.RAG
            analysis["confidence"] = min(rag_score, 0.95)
            analysis["reasoning"] = f"Question appears conceptual or needs context (RAG score: {rag_score:.2f})"
        elif abs(sql_score - rag_score) < 0.2:  # Scores are close
            analysis["query_type"] = QueryType.HYBRID
            analysis["confidence"] = 0.7
            analysis["reasoning"] = "Question could benefit from both data retrieval and contextual reasoning"
        else:
            # Default to RAG for safety
            analysis["query_type"] = QueryType.RAG
            analysis["confidence"] = 0.5
            analysis["reasoning"] = "Unclear intent, defaulting to contextual search"
        
        # Generate suggested follow-up questions
        analysis["suggested_followups"] = self._generate_followups(analysis)
        
        return analysis
    
    def _detect_entities(self, question: str) -> List[str]:
        """Detect which database entities (tables/concepts) the question refers to."""
        entities = []
        
        for entity_type, keywords in self.entity_keywords.items():
            if any(keyword in question for keyword in keywords):
                entities.append(entity_type)
        
        return entities
    
    def _calculate_sql_score(self, question: str) -> float:
        """Calculate how likely this question needs SQL processing."""
        score = 0.0
        total_indicators = len(self.sql_indicators)
        
        # Check for SQL indicator keywords
        matches = 0
        for indicator in self.sql_indicators:
            if indicator in question:
                matches += 1
                # Give higher weight to certain patterns
                if indicator in ["how many", "count", "total"]:
                    score += 0.3
                elif indicator in ["list all", "show all", "get all"]:
                    score += 0.25
                else:
                    score += 0.2
        
        # Boost score if multiple SQL indicators are present
        if matches > 1:
            score *= 1.2
        
        # Check for number patterns (likely requesting counts/calculations)
        if re.search(r'\b\d+\b', question):
            score += 0.1
        
        # Look for question words that typically need specific data
        sql_question_words = ["which", "where", "when", "who"]
        for word in sql_question_words:
            if question.startswith(word):
                score += 0.15
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_rag_score(self, question: str) -> float:
        """Calculate how likely this question needs RAG processing."""
        score = 0.0
        
        # Check for RAG indicator keywords
        matches = 0
        for indicator in self.rag_indicators:
            if indicator in question:
                matches += 1
                # Give higher weight to certain patterns
                if indicator in ["what is", "explain", "describe"]:
                    score += 0.3
                elif indicator in ["tell me about", "information about"]:
                    score += 0.25
                else:
                    score += 0.2
        
        # Boost score if multiple RAG indicators are present
        if matches > 1:
            score *= 1.2
        
        # Questions starting with "what", "how", "why" often need context
        rag_question_words = ["what", "how", "why"]
        for word in rag_question_words:
            if question.startswith(word):
                score += 0.2
        
        # Long questions often need more context
        if len(question.split()) > 10:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _needs_clarification(self, question: str, session_context: Optional[Dict[str, Any]]) -> bool:
        """Check if the question contains ambiguous references that need clarification."""
        # Check for pronouns without clear antecedents
        for indicator in self.clarification_indicators:
            if question.startswith(indicator) or f" {indicator} " in question:
                # If there's no recent context, we need clarification
                if not session_context or not session_context.get("topic"):
                    return True
        
        return False
    
    def _generate_clarification(self, question: str, session_context: Optional[Dict[str, Any]]) -> str:
        """Generate a clarification question for ambiguous queries."""
        if question.startswith(("it", "that", "this")):
            return "I'm not sure what you're referring to. Could you be more specific about what you'd like to know?"
        elif question.startswith(("them", "those", "these")):
            return "Which items are you asking about? Could you clarify what you'd like to know more about?"
        else:
            return "Could you provide more details about what you're looking for?"
    
    def _adjust_scores_with_context(self, sql_score: float, rag_score: float, 
                                  session_context: Dict[str, Any], question: str) -> Tuple[float, float]:
        """Adjust routing scores based on conversation context."""
        # If user was just doing SQL queries, slightly favor SQL for follow-ups
        if session_context.get("last_query_type") == "SQL":
            sql_score *= 1.1
        
        # If user was exploring a topic conceptually, favor RAG for follow-ups
        elif session_context.get("last_query_type") == "RAG":
            rag_score *= 1.1
        
        # If the question is a follow-up (contains "also", "and", "more")
        followup_words = ["also", "and", "more", "additionally", "furthermore"]
        if any(word in question for word in followup_words):
            # Maintain the same query type as previous
            last_type = session_context.get("last_query_type")
            if last_type == "SQL":
                sql_score *= 1.2
            elif last_type == "RAG":
                rag_score *= 1.2
        
        return sql_score, rag_score
    
    def _generate_followups(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate suggested follow-up questions based on the analysis."""
        followups = []
        entities = analysis["entities"]
        query_type = analysis["query_type"]
        
        if "products" in entities:
            if query_type == QueryType.SQL:
                followups.extend([
                    "Would you like to see the top-selling products?",
                    "Are you interested in products from a specific category?",
                    "Do you want to compare products by price or popularity?"
                ])
            else:
                followups.extend([
                    "Would you like to know more about product categories?",
                    "Are you interested in learning about suppliers?",
                    "Do you want to understand how products are organized?"
                ])
        
        if "customers" in entities:
            if query_type == QueryType.SQL:
                followups.extend([
                    "Would you like to see customer order statistics?",
                    "Are you interested in customers from specific regions?",
                    "Do you want to analyze customer purchasing patterns?"
                ])
            else:
                followups.extend([
                    "Would you like to understand customer demographics?",
                    "Are you interested in customer relationship management?",
                    "Do you want to learn about customer segmentation?"
                ])
        
        # Limit to 3 followups to avoid overwhelming the user
        return followups[:3]

# Global router instance
query_router = QueryRouter()