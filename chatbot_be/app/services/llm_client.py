"""
llm_client.py
Service to interact with DeepSeek LLM via Ollama's local API.
"""

import httpx
from typing import List

class DeepSeekLLMClient:
    """
    Client for communicating with DeepSeek LLM running locally via Ollama.
    """
    def __init__(self, base_url: str = "http://localhost:11434/api/generate", model: str = "deepseek-coder"):
        self.base_url = base_url
        self.model = model

    async def generate(self, prompt: str, context: List[str] = None) -> str:
        """
        Generate a response from DeepSeek LLM using Ollama.
        Args:
            prompt (str): The user question
            context (List[str], optional): Context documents to include
        Returns:
            str: Generated answer
        """
        # Combine context and prompt
        if context:
            context_text = "\n".join([f"- {doc}" for doc in context])
            # Add explicit instructions for counting
            instructions = (
                "You are a helpful assistant. "
                "Based on the context below, answer the user's question. "
                "If the user asks for a count, count the number of items in the context. "
                "If the user asks for a list, list the items. "
                "If the user asks for details, provide details from the context. "
            )
            full_prompt = f"{instructions}\n\nContext:\n{context_text}\n\nQuestion: {prompt}\nAnswer:"
        else:
            full_prompt = prompt

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                data = response.json()
                print(data)
                return data.get("response", "No answer generated.")
            except httpx.HTTPStatusError as e:
                # Log status code and response text
                return f"HTTP error {e.response.status_code}: {e.response.text}"
            except httpx.RequestError as e:
                # Log request error details
                return f"Request error: {str(e)}"
            except Exception as e:
                # Log any other error
                return f"Unexpected error calling DeepSeek LLM: {str(e)}"

# Global instance for reuse
llm_client = DeepSeekLLMClient()
