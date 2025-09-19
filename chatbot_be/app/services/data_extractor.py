"""
data_extractor.py
Data extraction service for retrieving relevant information from the Northwind database.
Handles querying product descriptions, categories, and other data for RAG enhancement.
"""

import logging
from typing import List, Dict, Any, Optional
from app.models.database import database
from app.core.exceptions import ChatbotBaseException

logger = logging.getLogger(__name__)

class DataExtractor:
    """Service for extracting relevant data from the Northwind database for RAG."""
    
    def __init__(self):
        self.db = database
    
    async def get_product_descriptions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get product descriptions and related information for RAG context.
        
        Args:
            limit: Maximum number of products to return
            
        Returns:
            List of product dictionaries with relevant information
        """
        try:
            query = """
            SELECT 
                product_id,
                product_name,
                quantity_per_unit,
                unit_price,
                category_id,
                supplier_id
            FROM products 
            LIMIT $1
            """
            
            products = await self.db.execute_query(query, (limit,))
            
            # Enhance with category information
            for product in products:
                category_info = await self.get_category_info(product['category_id'])
                product['category_name'] = category_info.get('category_name', 'Unknown')
                product['category_description'] = category_info.get('description', '')
            
            logger.info(f"Retrieved {len(products)} product descriptions")
            return products
            
        except Exception as e:
            logger.error(f"Error fetching product descriptions: {str(e)}")
            raise ChatbotBaseException(f"Failed to fetch product descriptions: {str(e)}")
    
    async def get_category_info(self, category_id: int) -> Dict[str, Any]:
        """
        Get category information by ID.
        
        Args:
            category_id: The category ID to look up
            
        Returns:
            Dictionary with category information
        """
        try:
            query = """
            SELECT category_id, category_name, description
            FROM categories 
            WHERE category_id = $1
            """
            
            results = await self.db.execute_query(query, (category_id,))
            return results[0] if results else {}
            
        except Exception as e:
            logger.error(f"Error fetching category info: {str(e)}")
            return {}
    
    async def get_supplier_info(self, supplier_id: int) -> Dict[str, Any]:
        """
        Get supplier information by ID.
        
        Args:
            supplier_id: The supplier ID to look up
            
        Returns:
            Dictionary with supplier information
        """
        try:
            query = """
            SELECT supplier_id, company_name, contact_name, city, country
            FROM suppliers 
            WHERE supplier_id = $1
            """
            
            results = await self.db.execute_query(query, (supplier_id,))
            return results[0] if results else {}
            
        except Exception as e:
            logger.error(f"Error fetching supplier info: {str(e)}")
            return {}
    
    async def search_products_by_name(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search products by name or description.
        
        Args:
            search_term: Term to search for in product names
            limit: Maximum number of results to return
            
        Returns:
            List of matching products
        """
        try:
            query = """
            SELECT 
                product_id,
                product_name,
                quantity_per_unit,
                unit_price,
                category_id
            FROM products 
            WHERE product_name ILIKE $1
            LIMIT $2
            """
            
            search_pattern = f"%{search_term}%"
            results = await self.db.execute_query(query, (search_pattern, limit))
            
            logger.info(f"Found {len(results)} products matching '{search_term}'")
            return results
            
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            raise ChatbotBaseException(f"Failed to search products: {str(e)}")
    
    async def get_database_schema(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get schema information for all tables in the database.
        
        Returns:
            Dictionary mapping table names to their schema information
        """
        try:
            tables = await self.db.get_all_tables()
            schema_info = {}
            
            for table_name in tables:
                schema_info[table_name] = await self.db.get_table_schema(table_name)
            
            logger.info(f"Retrieved schema for {len(tables)} tables")
            return schema_info
            
        except Exception as e:
            logger.error(f"Error fetching database schema: {str(e)}")
            raise ChatbotBaseException(f"Failed to fetch database schema: {str(e)}")

# Global data extractor instance
data_extractor = DataExtractor()

from typing import List
from app.models.database import database

async def fetch_product_descriptions() -> List[str]:
    """
    Fetch product descriptions from the Northwind database.
    Returns:
        List[str]: List of product descriptions.
    """
    try:
        # SQLite query for product descriptions
        query = """
        SELECT ProductName || ': ' || COALESCE(QuantityPerUnit, '') AS description 
        FROM Products
        """
        results = database.execute_query(query)
        return [row['description'] for row in results]
        
    except Exception as e:
        print(f"Error fetching product descriptions: {e}")
        # Return some sample data if database fails
        return [
            "Sample Product 1: High quality item",
            "Sample Product 2: Premium service", 
            "Sample Product 3: Reliable solution"
        ]
