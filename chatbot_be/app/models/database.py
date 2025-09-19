"""
database.py
Database connection and model definitions.
Handles PostgreSQL connection for the Northwind database running in Docker.
"""

import asyncpg
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.core.exceptions import ChatbotBaseException

class DatabaseConnection:
    """Manages PostgreSQL database connections for the Northwind database."""
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
    
    async def get_pool(self) -> asyncpg.Pool:
        """Get or create a database connection pool."""
        if self._pool is None:
            try:
                self._pool = await asyncpg.create_pool(
                    host=settings.db_host,
                    port=settings.db_port,
                    user=settings.db_user,
                    password=settings.db_password,
                    database=settings.db_name,
                    min_size=1,
                    max_size=5
                )
            except Exception as e:
                raise ChatbotBaseException(f"Failed to connect to database: {str(e)}")
        
        return self._pool
    
    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries."""
        try:
            pool = await self.get_pool()
            async with pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                
                # Convert asyncpg.Record objects to dictionaries
                results = []
                for row in rows:
                    results.append(dict(row))
                
                return results
                
        except Exception as e:
            raise ChatbotBaseException(f"Database query failed: {str(e)}")
    
    async def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return number of affected rows."""
        try:
            pool = await self.get_pool()
            async with pool.acquire() as conn:
                result = await conn.execute(query, *params)
                # Extract row count from result string like "UPDATE 1"
                return int(result.split()[-1]) if result else 0
                
        except Exception as e:
            raise ChatbotBaseException(f"Database update failed: {str(e)}")
    
    async def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema information for a specific table."""
        query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = $1
        ORDER BY ordinal_position
        """
        return await self.execute_query(query, (table_name.lower(),))
    
    async def get_all_tables(self) -> List[str]:
        """Get list of all table names in the database."""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        """
        results = await self.execute_query(query)
        return [row['table_name'] for row in results]
    
    async def close(self):
        """Close the database connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None

# Global database instance
database = DatabaseConnection()