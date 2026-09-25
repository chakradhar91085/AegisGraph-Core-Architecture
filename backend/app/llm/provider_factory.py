"""
AegisGraph — LLM Provider Factory.

Returns the correct provider singleton by name.
Providers are instantiated lazily on first request and cached.
"""
import logging
from app.llm.base_provider import BaseLLMProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

# Lazy singletons
_providers: dict[str, BaseLLMProvider] = {}


def get_llm_provider(provider_name: str | None = None) -> BaseLLMProvider:
    """
    Return the LLM provider. Since Gemini was removed, this always returns Ollama.

    Args:
        provider_name: Ignored. Maintained for signature compatibility.

    Returns:
        A BaseLLMProvider instance.
    """
    name = "ollama"

    if name not in _providers:
        from app.llm.ollama_provider import OllamaProvider
        _providers[name] = OllamaProvider()
        logger.info(f"Initialized OllamaProvider ({settings.OLLAMA_MODEL})")

    return _providers[name]
