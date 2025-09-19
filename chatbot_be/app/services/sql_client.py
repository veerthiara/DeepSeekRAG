"""
sql_client.py
SQL client service for executing natural language to SQL queries.
Uses LangChain SQL Agent to interact with the PostgreSQL Northwind database.
"""

import logging
from typing import Dict, Any, Optional
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.llms import Ollama
import asyncio
from app.core.config import settings
from app.core.exceptions import SQLServiceException

logger = logging.getLogger(__name__)

class SQLClient:
    """Service for executing natural language SQL queries using LangChain."""
    
    def __init__(self):
        self._db: Optional[SQLDatabase] = None
        self._agent = None
        self._llm = None
        
    def _get_database(self) -> SQLDatabase:
        """Get or create SQLDatabase connection."""
        if self._db is None:
            try:
                database_url = settings.database_url
                logger.info(f"Connecting to database: {database_url.split('@')[1] if '@' in database_url else database_url}")
                
                self._db = SQLDatabase.from_uri(
                    database_url,
                    include_tables=None,  # Include all tables
                    sample_rows_in_table_info=3
                )
                
                logger.info("Successfully connected to PostgreSQL database")
                
            except Exception as e:
                logger.error(f"Failed to connect to database: {str(e)}")
                raise SQLServiceException(f"Database connection failed: {str(e)}")
        
        return self._db
    
    def _get_llm(self) -> Ollama:
        """Get or create Ollama LLM instance."""
        if self._llm is None:
            self._llm = Ollama(
                model=settings.llm_model,
                temperature=settings.llm_temperature
            )
        return self._llm
    
    def _get_agent(self):
        """Get or create SQL agent."""
        if self._agent is None:
            try:
                db = self._get_database()
                llm = self._get_llm()
                
                self._agent = create_sql_agent(
                    llm=llm,
                    db=db,
                    verbose=True,
                    handle_parsing_errors=True
                )
                
                logger.info("SQL agent created successfully")
                
            except Exception as e:
                logger.error(f"Failed to create SQL agent: {str(e)}")
                raise SQLServiceException(f"SQL agent creation failed: {str(e)}")
        
        return self._agent
    
    async def execute_natural_language_query(self, question: str) -> Dict[str, Any]:
        """
        Execute a natural language query against the database.
        
        Args:
            question: Natural language question to convert to SQL and execute
            
        Returns:
            Dictionary containing the query results and metadata
        """
        try:
            agent = self._get_agent()
            
            # Execute the query in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, agent.run, question)
            
            return {
                "success": True,
                "question": question,
                "answer": result,
                "query_type": "natural_language_sql"
            }
            
        except Exception as e:
            logger.error(f"Error executing natural language query: {str(e)}")
            return {
                "success": False,
                "question": question,
                "error": str(e),
                "query_type": "natural_language_sql"
            }
    
    def execute_natural_language_query_sync(self, question: str) -> str:
        """
        Synchronous version for compatibility.
        
        Args:
            question: Natural language question to convert to SQL and execute
            
        Returns:
            String containing the answer
        """
        try:
            agent = self._get_agent()
            result = agent.run(question)
            return result
            
        except Exception as e:
            logger.error(f"Error executing natural language query: {str(e)}")
            raise SQLServiceException(f"SQL Agent failed: {str(e)}")
    
    async def get_table_info(self) -> Dict[str, Any]:
        """
        Get information about available tables in the database.
        
        Returns:
            Dictionary containing table information
        """
        try:
            db = self._get_database()
            
            return {
                "success": True,
                "table_info": db.get_table_info(),
                "usable_table_names": db.get_usable_table_names()
            }
            
        except Exception as e:
            logger.error(f"Error getting table info: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_connection(self) -> Dict[str, Any]:
        """
        Validate the database connection.
        
        Returns:
            Dictionary containing connection status
        """
        try:
            db = self._get_database()
            
            # Try a simple query to validate connection
            result = db.run("SELECT 1 as test")
            
            return {
                "success": True,
                "message": "Database connection is valid",
                "test_result": result
            }
            
        except Exception as e:
            logger.error(f"Database connection validation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Global SQL client instance
sql_client = SQLClient()

# Legacy function names for backward compatibility
async def ask_sql_agent(question: str) -> str:
    """Legacy function for backward compatibility."""
    result = await sql_client.execute_natural_language_query(question)
    if result["success"]:
        return result["answer"]
    else:
        raise SQLServiceException(result["error"])

def ask_sql_agent_sync(question: str) -> str:
    """Legacy synchronous function for backward compatibility."""
    return sql_client.execute_natural_language_query_sync(question)
