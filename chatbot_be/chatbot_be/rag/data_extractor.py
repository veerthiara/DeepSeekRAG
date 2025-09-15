"""
data_extractor.py
Service to extract relevant data from the database for RAG embedding.
"""

from typing import List
import asyncpg
from chatbot_be.db import get_db_pool

async def fetch_product_descriptions() -> List[str]:
    """
    Fetch product descriptions from the Northwind database.
    Returns:
        List[str]: List of product descriptions.
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT product_name || ': ' || COALESCE(quantity_per_unit, '') AS description FROM products;")
        return [row['description'] for row in rows]
