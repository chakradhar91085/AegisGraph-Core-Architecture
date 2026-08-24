import httpx
import logging
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    async def generate(self, prompt: str, context: str = "") -> str:
        """
        Generate a response using Ollama given a prompt and retrieved context.
        """
        system_prompt = "You are a helpful assistant. Use the following context to answer the question if relevant.\n\nContext:\n" + context
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
            except Exception as e:
                logger.error(f"Error communicating with Ollama: {e}")
                raise

    async def check_health(self) -> bool:
        """Verify the Ollama service is reachable"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                return True
            except Exception:
                return False

    async def classify_intent(self, query: str, allowed_intents: list[str]) -> str:
        """
        Use Ollama to classify a natural-language query into one of the allowed intents.
        Returns the intent string, or "unsupported_intent" on failure.
        """
        system_prompt = (
            "You are a strict intent classification engine.\n"
            "Classify the user's query into EXACTLY one of the following intents:\n"
            f"{allowed_intents}\n\n"
            "Respond ONLY with a valid JSON object in this exact format:\n"
            '{"intent": "<value>"}\n'
            "Do not include any other text, explanation, or markdown formatting."
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "stream": False,
            "format": "json"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                content = data.get("message", {}).get("content", "").strip()
                
                # Parse JSON
                import json
                result = json.loads(content)
                intent_val = result.get("intent", "unsupported_intent")
                
                # Validate
                if intent_val in allowed_intents:
                    return intent_val
                
                logger.warning(f"Ollama returned invalid intent: {intent_val}")
                return "unsupported_intent"
            except Exception as e:
                logger.error(f"Error during Ollama intent classification: {e}")
                return "unsupported_intent"

# Global instance
ollama_client = OllamaClient()
