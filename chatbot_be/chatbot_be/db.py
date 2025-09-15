"""
db.py
Database connection pool management for async PostgreSQL access.
"""

import asyncpg
from typing import Optional

_DB_POOL: Optional[asyncpg.Pool] = None

async def get_db_pool() -> asyncpg.Pool:
    """
    Get or create a global asyncpg connection pool.
    Returns:
        asyncpg.Pool: The connection pool instance.
    """
    global _DB_POOL
    if _DB_POOL is None:
        _DB_POOL = await asyncpg.create_pool(
            user="postgres",
            password="postgres",
            database="northwind",
            host="localhost",
            port=5432,
            min_size=1,
            max_size=5
        )
    return _DB_POOL
