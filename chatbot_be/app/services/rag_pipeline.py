"""
rag_pipeline.py
Script to extract data, embed, and build the FAISS vector store for RAG.
"""

import asyncio
from chatbot_be.rag.data_extractor import fetch_product_descriptions
from chatbot_be.rag.vector_store import VectorStore

async def build_rag_index():
    """
    Extracts product descriptions, generates embeddings, and builds the FAISS index.
    """
    print("Extracting product descriptions from database...")
    descriptions = await fetch_product_descriptions()
    print(f"Fetched {len(descriptions)} descriptions.")

    print("Building vector store with embeddings...")
    vs = VectorStore()
    vs.build_index(descriptions)
    print("Vector store built and ready for retrieval!")
    # Optionally, save the index to disk for reuse
    # faiss.write_index(vs.index, "vector.index")

if __name__ == "__main__":
    asyncio.run(build_rag_index())
