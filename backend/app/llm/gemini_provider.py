"""
AegisGraph — Gemini LLM Provider.

Wraps the existing GeminiClient into the BaseLLMProvider interface.
Preserves all existing retry logic and structured extraction.
"""
import logging
import asyncio
import json
from typing import Optional
from app.llm.base_provider import BaseLLMProvider
from app.core.config import settings
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("GEMINI_API_KEY not found. GeminiProvider will not function.")
        self.model = "gemini-flash-latest"

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def _generate_with_retry(self, **kwargs):
        """Retry API calls on 429/503 errors with short backoff."""
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                return await self.client.aio.models.generate_content(**kwargs)
            except Exception as e:
                error_str = str(e)
                if ("429" in error_str or "503" in error_str) and attempt < max_retries:
                    wait = 3 * (attempt + 1)
                    logger.warning(f"Gemini API error ({'503' if '503' in error_str else '429'}). "
                                   f"Retrying in {wait}s (attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(wait)
                else:
                    raise

    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        if not self.client:
            raise ValueError("Gemini Client is not initialized with an API key")

        config = types.GenerateContentConfig(temperature=0.0)
        if system_prompt:
            config.system_instruction = system_prompt

        try:
            response = await self._generate_with_retry(
                model=self.model,
                contents=[
                    types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
                ],
                config=config
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return f"An error occurred while generating the response from the LLM. Error details have been logged."

    async def extract_query_parameters(self, query: str, allowed_intents: list[str]) -> dict:
        if not self.client:
            return {"intent": "unsupported_intent", "search_terms": [], "primary_person": None}

        system_prompt = (
            "You are an information extraction engine for the AegisGraph Graph-RAG pipeline.\n"
            "Analyze the user's query and extract the following structured data:\n"
            "1. 'intent': Must be EXACTLY one of the following:\n"
            f"{allowed_intents}\n"
            "2. 'primary_person': The full name of the primary person the user is asking about (if any).\n"
            "3. 'search_terms': A list of possible name fragments or identifiers for the person to help search the database.\n"
            "Respond ONLY with a valid JSON object in this exact format:\n"
            '{"intent": "<value>", "primary_person": "<name>", "search_terms": ["<name>"]}\n'
            "If no person is identified, primary_person should be null and search_terms empty.\n"
            "Do not include any other text, explanation, or markdown formatting."
        )

        try:
            response = await self._generate_with_retry(
                model=self.model,
                contents=[
                    types.Content(role="user", parts=[types.Part.from_text(text=query)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    temperature=0.0
                )
            )
            content = response.text.strip()
            result = json.loads(content)

            intent_val = result.get("intent", "unsupported_intent")
            if intent_val not in allowed_intents:
                logger.warning(f"Gemini returned invalid intent: {intent_val}")
                result["intent"] = "unsupported_intent"

            if not isinstance(result.get("search_terms"), list):
                result["search_terms"] = []

            return result
        except Exception as e:
            logger.error(f"Gemini extraction error: {e}")
            return {"intent": "unsupported_intent", "search_terms": [], "primary_person": None}

    async def check_health(self) -> bool:
        if not self.client:
            return False
        try:
            await self._generate_with_retry(
                model=self.model,
                contents="ping",
                config=types.GenerateContentConfig(max_output_tokens=1)
            )
            return True
        except Exception:
            return False
