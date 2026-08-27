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
    Return the LLM provider for the given name.

    Args:
        provider_name: 'gemini' or 'ollama'. Defaults to settings.LLM_PROVIDER.

    Returns:
        A BaseLLMProvider instance.
    """
    name = (provider_name or settings.LLM_PROVIDER).lower().strip()

    if name not in ("gemini", "ollama"):
        logger.warning(f"Unknown LLM provider '{name}', falling back to '{settings.LLM_PROVIDER}'")
        name = settings.LLM_PROVIDER.lower().strip()

    if name not in _providers:
        if name == "gemini":
            from app.llm.gemini_provider import GeminiProvider
            _providers[name] = GeminiProvider()
            logger.info("Initialized GeminiProvider (gemini-flash-latest)")
        elif name == "ollama":
            from app.llm.ollama_provider import OllamaProvider
            _providers[name] = OllamaProvider()
            logger.info(f"Initialized OllamaProvider ({settings.OLLAMA_MODEL})")

    return _providers[name]
