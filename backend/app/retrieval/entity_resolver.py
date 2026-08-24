"""
AegisGraph Phase 2 — Deterministic entity resolution.

Resolves user-provided names/emails to actual graph nodes.
Returns confidence/status: found, ambiguous, or not_found.
Never silently picks between ambiguous matches.
"""
import re
from typing import Optional
from app.retrieval.schemas import ResolvedEntity, ResolutionStatus
from app.retrieval.strategies import retrieval_strategies
import logging

logger = logging.getLogger(__name__)

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


class EntityResolver:
    """
    Deterministic entity resolution for the retrieval pipeline.

    Resolution priority:
    1. Exact email match (Employee)
    2. Name search (Employee)
    3. Entity name search (Entity)

    This component is designed to be replaceable with a more sophisticated
    resolver (e.g., fuzzy matching, LLM-assisted) in a future phase.
    """

    def __init__(self):
        self.strategies = retrieval_strategies

    def extract_email(self, text: str) -> Optional[str]:
        """Extract the first email address from text, if present."""
        match = EMAIL_PATTERN.search(text)
        return match.group(0).lower() if match else None

    async def resolve_employee(self, query: str) -> ResolvedEntity:
        """
        Attempt to resolve a user query to an Employee node.

        Strategy:
        1. If query contains an email address, try exact email match.
        2. Otherwise, search by name.
        """
        email = self.extract_email(query)

        if email:
            results = await self.strategies.lookup_employee_by_email(email)
            if len(results) == 1:
                return ResolvedEntity(
                    type="employee",
                    query_value=email,
                    status=ResolutionStatus.FOUND,
                    matches=results,
                )
            elif len(results) > 1:
                return ResolvedEntity(
                    type="employee",
                    query_value=email,
                    status=ResolutionStatus.AMBIGUOUS,
                    matches=results,
                )
            # Email not found — fall through to name search using the local part
            name_hint = email.split("@")[0].replace(".", " ")
        else:
            # Clean intent stop words to extract the name
            name_hint = query.lower()
            name_hint = re.sub(r"[^\w\s@.]", "", name_hint) # Remove punctuation except @ and .
            stopwords = [
                "what", "emails", "did", "send", "receive", "who", "is",
                "find", "employee", "sent", "by", "received", "from",
                "look", "up", "search", "for", "the", "about", "tell", "me"
            ]
            for word in stopwords:
                name_hint = re.sub(rf"\b{word}\b", "", name_hint)
            name_hint = re.sub(r"\s+", " ", name_hint).strip()
            # If nothing left (e.g. "find employee"), fallback to original
            if not name_hint:
                name_hint = query.strip()

        # Try name-based search
        results = await self.strategies.lookup_employee_by_name(name_hint, limit=5)

        if len(results) == 1:
            return ResolvedEntity(
                type="employee",
                query_value=name_hint,
                status=ResolutionStatus.FOUND,
                matches=results,
            )
        elif len(results) > 1:
            return ResolvedEntity(
                type="employee",
                query_value=name_hint,
                status=ResolutionStatus.AMBIGUOUS,
                matches=results,
            )
        else:
            return ResolvedEntity(
                type="employee",
                query_value=email or name_hint,
                status=ResolutionStatus.NOT_FOUND,
                matches=[],
            )

    async def resolve_entity(self, name: str) -> ResolvedEntity:
        """
        Attempt to resolve a user-provided name to an Entity node.
        Uses case-insensitive name search on the Entity label.
        """
        clean_name = name.lower()
        clean_name = re.sub(r"[^\w\s@.]", "", clean_name)
        stopwords = [
            "what", "entities", "are", "related", "to", "connected",
            "mentioned", "in", "chunk", "find", "search", "look", "for", "the"
        ]
        for word in stopwords:
            clean_name = re.sub(rf"\b{word}\b", "", clean_name)
        clean_name = re.sub(r"\s+", " ", clean_name).strip()
        if not clean_name:
            clean_name = name.strip()
            
        query = """
        MATCH (ent:Entity)
        WHERE toLower(ent.name) CONTAINS toLower($name)
        RETURN ent.entity_id AS entity_id, ent.name AS entity_name,
               ent.entity_type AS entity_type
        LIMIT 5
        """
        results = await self.strategies.db.execute_read(query, {"name": clean_name})

        if len(results) == 1:
            return ResolvedEntity(
                type="entity",
                query_value=name,
                status=ResolutionStatus.FOUND,
                matches=results,
            )
        elif len(results) > 1:
            return ResolvedEntity(
                type="entity",
                query_value=name,
                status=ResolutionStatus.AMBIGUOUS,
                matches=results,
            )
        else:
            return ResolvedEntity(
                type="entity",
                query_value=name,
                status=ResolutionStatus.NOT_FOUND,
                matches=[],
            )


# Module-level singleton
entity_resolver = EntityResolver()
