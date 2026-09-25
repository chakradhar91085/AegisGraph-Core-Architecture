"""
AegisGraph — hard security gates.

Pattern checks on a single query that force a minimum risk regardless of the
behavioral history (paper Eq. 13): prompt injection / role impersonation
-> HIGH (0.65), bulk requests for sensitive personal data -> MEDIUM (0.35).
"""
import re

_INJECTION = re.compile(
    r"ignore\s+(all\s+|any\s+|the\s+)?(previous|prior|above|earlier)\s+(instructions|rules|prompts)"
    r"|disregard\s+(all\s+|any\s+|the\s+)?(previous|prior|above|your)\s+(instructions|rules|guidelines|polic)"
    r"|you\s+are\s+now\s+(the\s+|an?\s+)?(system\s+|aegisgraph\s+)?(admin|administrator|root|developer)"
    r"|(with|has|have)\s+(full|unrestricted|admin)\s+(clearance|access|privileges)"
    r"|(reveal|show|print|repeat)\s+(me\s+)?(your\s+|the\s+)?(system|hidden|initial)\s+(prompt|instructions)"
    r"|developer\s+mode|jailbreak"
    r"|(bypass|override)\s+(the\s+)?(security|policy|filters?|restrictions?|access)",
    re.IGNORECASE,
)
_SENSITIVE = re.compile(
    r"\b(social\s+security|ssn|salary|salaries|compensation|home\s+(phone|address)|credit\s+card|passport|passwords?)\b",
    re.IGNORECASE,
)
_BULK = re.compile(r"\b(all|every|each|list|dump|export|enumerate)\b", re.IGNORECASE)


def gate_score(query: str) -> float:
    if _INJECTION.search(query):
        return 0.65
    if _SENSITIVE.search(query) and _BULK.search(query):
        return 0.35
    return 0.0
