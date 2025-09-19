"""
rag_service.py
Service that combines vector search with LLM to answer questions using RAG.
"""

from typing import List, Dict, Any
import asyncio
from app.services.data_extractor import data_extractor
from app.services.vector_store import VectorStore
from app.services.llm_client import llm_client
from app.core.exceptions import RAGServiceException
from app.core.config import settings

class RAGService:
    """
    Retrieval-Augmented Generation service that answers questions using context from the vector store.
    """
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.is_initialized = False
    
    async def initialize(self):
        """
        Initialize the RAG service by building the vector store.
        This should be called once at startup.
        """
        if not self.is_initialized:
            print("Initializing RAG service...")
            try:
                product_data = await data_extractor.get_product_descriptions()
                
                # Convert product dictionaries to text strings for embedding
                descriptions = []
                for product in product_data:
                    # Format product information as readable text
                    text = f"Product: {product.get('product_name', 'Unknown')} - "
                    text += f"Category: {product.get('category_name', 'Unknown')} - "
                    text += f"Price: ${product.get('unit_price', 0)} - "
                    text += f"Description: {product.get('category_description', 'No description available')}"
                    descriptions.append(text)
                
                # Add some fallback descriptions if database is empty
                if not descriptions:
                    descriptions = [
                        "Product: Sample Product 1 - Category: Electronics - Price: $99.99 - Description: High-quality electronic device",
                        "Product: Sample Product 2 - Category: Books - Price: $19.99 - Description: Educational book for learning",
                        "Product: Sample Product 3 - Category: Clothing - Price: $49.99 - Description: Comfortable casual wear"
                    ]
                
                self.vector_store.build_index(descriptions)
                self.is_initialized = True
                print(f"RAG service initialized with {len(descriptions)} documents.")
                
            except Exception as e:
                print(f"Error initializing RAG service: {str(e)}")
                # Use fallback descriptions
                fallback_descriptions = [
                    "Product: Sample Product 1 - Category: Electronics - Price: $99.99 - Description: High-quality electronic device",
                    "Product: Sample Product 2 - Category: Books - Price: $19.99 - Description: Educational book for learning",
                    "Product: Sample Product 3 - Category: Clothing - Price: $49.99 - Description: Comfortable casual wear"
                ]
                self.vector_store.build_index(fallback_descriptions)
                self.is_initialized = True
                print(f"RAG service initialized with {len(fallback_descriptions)} fallback documents.")
    
    async def search_context(self, query: str, top_k: int = 3) -> List[str]:
        """
        Search for relevant context from the vector store.
        
        Args:
            query (str): User's question
            top_k (int): Number of relevant documents to retrieve
            
        Returns:
            List[str]: List of relevant context documents
        """
        if not self.is_initialized:
            await self.initialize()
        
        results = self.vector_store.search(query, top_k)
        # Extract just the text content (ignore scores for now)
        context_docs = [result[0] for result in results]
        return context_docs
    
    async def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a question using RAG approach with DeepSeek LLM.
        
        Args:
            question (str): User's question
        Returns:
            Dict[str, Any]: Contains the answer and retrieved context
        """
        # Step 1: Retrieve relevant context
        context_docs = await self.search_context(question, top_k=3)
        
        # Step 2: Generate answer using DeepSeek LLM
        try:
            answer = await llm_client.generate(question, context_docs)
        except Exception as e:
            answer = f"Error generating answer with DeepSeek LLM: {str(e)}"
        
        return {
            "question": question,
            "answer": answer,
            "context": context_docs,
            "context_count": len(context_docs)
        }
    
    def _generate_simple_answer(self, question: str, context_docs: List[str]) -> str:
        """
        Generate a simple answer based on retrieved context.
        This is a placeholder - you'll replace this with LLM integration.
        
        Args:
            question (str): User's question
            context_docs (List[str]): Retrieved context documents
            
        Returns:
            str: Generated answer
        """
        if not context_docs:
            return "I couldn't find relevant information to answer your question."
        
        # Simple keyword-based matching for demonstration
        question_lower = question.lower()
        
        if "product" in question_lower or "what" in question_lower:
            return f"Based on our product database, here are the most relevant items:\n\n" + \
                   "\n".join([f"• {doc}" for doc in context_docs[:3]])
        
        elif "how many" in question_lower or "count" in question_lower:
            return f"I found {len(context_docs)} relevant products in our database."
        
        else:
            return f"Here's what I found related to your question:\n\n" + \
                   "\n".join([f"• {doc}" for doc in context_docs[:3]])

# Global instance for reuse
rag_service = RAGService()