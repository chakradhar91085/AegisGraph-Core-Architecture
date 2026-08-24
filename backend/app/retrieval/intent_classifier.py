"""
AegisGraph Phase 2 — Rule-based intent classifier.

Classifies natural-language queries into predefined retrieval intents.
Designed to be replaceable with an LLM-based classifier in a future phase.

Returns unsupported_intent for anything it cannot confidently classify.
"""
import re
from app.retrieval.schemas import RetrievalIntent
import logging

logger = logging.getLogger(__name__)

# Each rule is a tuple of (compiled regex pattern, intent)
# Rules are evaluated top-to-bottom; first match wins.
INTENT_RULES = [
    # All employees
    (re.compile(
        r"(who\s+are\s+the\s+employees)"
        r"|(list\s+(all\s+)?employees)"
        r"|(show\s+employees)",
        re.IGNORECASE,
    ), RetrievalIntent.ALL_EMPLOYEES),

    # Graph discovery
    (re.compile(
        r"(what\s+can\s+(i|you)\s+(do|explore|search))"
        r"|(how\s+does\s+aegisgraph\s+work)"
        r"|(what\s+(is|information\s+is)\s+(in|available))"
        r"|(help)"
        r"|(hello|hi\b|greetings)",
        re.IGNORECASE,
    ), RetrievalIntent.GRAPH_DISCOVERY),

    # Entity relationship lookups
    (re.compile(
        r"(entities?\s+(related|connected|linked)\s+to)"
        r"|(related\s+entities)"
        r"|(entity\s+relationship)",
        re.IGNORECASE,
    ), RetrievalIntent.ENTITY_RELATIONSHIPS),

    # Chunk entity lookups
    (re.compile(
        r"(entities?\s+(in|from|mentioned\s+in)\s+(chunk|text))"
        r"|(chunk\s+entit)"
        r"|(mentioned\s+in\s+chunk)",
        re.IGNORECASE,
    ), RetrievalIntent.CHUNK_ENTITIES),

    # Email chunk lookups
    (re.compile(
        r"(chunks?\s+(of|from|in)\s+email)"
        r"|(email\s+(text|content|body|chunks?))"
        r"|(content\s+of\s+email)",
        re.IGNORECASE,
    ), RetrievalIntent.EMAIL_CHUNKS),

    # Sent emails
    (re.compile(
        r"(emails?\s+(sent|from|written)\s+by)"
        r"|(sent\s+(by|emails?|mail))"
        r"|(emails?\s+from\b)"
        r"|(emails?.*send)"
        r"|(outbox)",
        re.IGNORECASE,
    ), RetrievalIntent.SENT_EMAILS),

    # Received emails
    (re.compile(
        r"(emails?\s+(received|to)\s+by)"
        r"|(received\s+(by|emails?|mail))"
        r"|(emails?\s+to\b)"
        r"|(emails?.*receive)"
        r"|(inbox)",
        re.IGNORECASE,
    ), RetrievalIntent.RECEIVED_EMAILS),

    # Organization info
    (re.compile(
        r"(organization.*associated\s+with)"
        r"|(domain.*belong\s+to)"
        r"|(which\s+organization)"
        r"|(what\s+organization)",
        re.IGNORECASE,
    ), RetrievalIntent.ORGANIZATION_INFO),

    # Person-to-person connection
    (re.compile(
        r"(connected\s+to)"
        r"|(connection\s+between)",
        re.IGNORECASE,
    ), RetrievalIntent.PERSON_CONNECTION),

    # Frequent communication
    (re.compile(
        r"(communicate(s)?\s+with)"
        r"|(email(s)?\s+most\s+often)"
        r"|(strongest\s+connections)",
        re.IGNORECASE,
    ), RetrievalIntent.FREQUENT_COMMUNICATION),

    # Topical footprint
    (re.compile(
        r"(frequently\s+talks\s+about)"
        r"|(frequently\s+mentions)"
        r"|(topics.*associated\s+with)"
        r"|(what.*talk\s+about)",
        re.IGNORECASE,
    ), RetrievalIntent.TOPICAL_FOOTPRINT),

    # Employee lookup (broadest — must come last among specific intents)
    (re.compile(
        r"(find\s+(employee|person|user|worker))"
        r"|(who\s+is)"
        r"|(look\s*up\s+(employee|person))"
        r"|(employee\s+info)"
        r"|(search\s+(for\s+)?(employee|person))",
        re.IGNORECASE,
    ), RetrievalIntent.EMPLOYEE_LOOKUP),
]

# If query contains an @ sign and no other intent matched, assume employee lookup
EMAIL_FALLBACK_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


from app.llm.ollama_client import ollama_client

async def classify_intent(query: str) -> RetrievalIntent:
    """
    Classify a natural-language query into a retrieval intent.

    Rules are evaluated top-to-bottom. First match wins.
    If deterministic regex fails, falls back to a strictly constrained LLM classification.
    """
    query = query.strip()
    if not query:
        return RetrievalIntent.UNSUPPORTED

    # 1. Fast Path: Deterministic Regex
    for pattern, intent in INTENT_RULES:
        if pattern.search(query):
            logger.debug(f"Intent classified as {intent.value} for query: {query!r}")
            return intent

    # Fallback: if query contains an email address, treat as employee lookup
    if EMAIL_FALLBACK_PATTERN.search(query):
        logger.debug(f"Email detected, defaulting to employee_lookup: {query!r}")
        return RetrievalIntent.EMPLOYEE_LOOKUP

    # 2. Slow Path: LLM Intent Classification Fallback
    logger.debug(f"Regex classification failed, falling back to LLM for: {query!r}")
    allowed_intents = [i.value for i in RetrievalIntent]
    
    llm_intent_str = await ollama_client.classify_intent(query, allowed_intents)
    
    try:
        validated_intent = RetrievalIntent(llm_intent_str)
        if validated_intent != RetrievalIntent.UNSUPPORTED:
            logger.debug(f"LLM successfully classified intent as {llm_intent_str}")
        return validated_intent
    except ValueError:
        logger.warning(f"LLM returned invalid intent: {llm_intent_str}. Defaulting to UNSUPPORTED.")
        return RetrievalIntent.UNSUPPORTED
