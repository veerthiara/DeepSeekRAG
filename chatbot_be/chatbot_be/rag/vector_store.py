"""
vector_store.py
Service for embedding text and storing/searching vectors using FAISS.
"""

from typing import List, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class VectorStore:
    """
    Handles embedding and vector search using FAISS.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.texts = []  # Store original texts for retrieval

    def build_index(self, texts: List[str]):
        """
        Embed a list of texts and build a FAISS index.
        Args:
            texts (List[str]): List of texts to embed and index.
        """
        self.texts = texts
        embeddings = self.model.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for the most similar texts to the query.
        Args:
            query (str): The query string.
            top_k (int): Number of top results to return.
        Returns:
            List[Tuple[str, float]]: List of (text, score) tuples.
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        query_emb = self.model.encode([query]).astype('float32')
        D, I = self.index.search(query_emb, top_k)
        results = [(self.texts[i], float(D[0][idx])) for idx, i in enumerate(I[0])]
        return results
