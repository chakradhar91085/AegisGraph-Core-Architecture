"""
AegisGraph Phase 2 — Retrieval service orchestrator.

Pipeline: Query -> Intent Classification -> Entity Resolution -> Strategy Execution -> Results

This is the single chokepoint through which all retrieval requests flow.
A future AegisGraph behavioral security layer can intercept at this level
to enforce risk policies before and after graph access.
"""
from typing import Dict, Any
from app.retrieval.schemas import (
    RetrievalRequest,
    RetrievalResponse,
    RetrievalIntent,
    ResolutionStatus,
)
from app.retrieval.intent_classifier import classify_intent
from app.retrieval.entity_resolver import entity_resolver
from app.retrieval.strategies import retrieval_strategies
import logging

logger = logging.getLogger(__name__)
from app.core.config import settings

INTENT_DEPTH_MAP = {
    # prototype policy interpretation: d_eff=0 permits non-expansive base lookups
    RetrievalIntent.EMPLOYEE_LOOKUP: 0, 
    RetrievalIntent.SENT_EMAILS: 2,
    RetrievalIntent.RECEIVED_EMAILS: 2,
    RetrievalIntent.EMAIL_CHUNKS: 3,
    RetrievalIntent.CHUNK_ENTITIES: 4,
    RetrievalIntent.ENTITY_RELATIONSHIPS: 5,
    RetrievalIntent.ALL_EMPLOYEES: 1,
    RetrievalIntent.GRAPH_DISCOVERY: 0,
    RetrievalIntent.FREQUENT_COMMUNICATION: 1,
    RetrievalIntent.TOPICAL_FOOTPRINT: 1,
    RetrievalIntent.ORGANIZATION_INFO: 1,
    RetrievalIntent.PERSON_CONNECTION: 1,
    RetrievalIntent.UNSUPPORTED: 0
}


def _serialize_results(results: list) -> list:
    """Convert Neo4j result dicts to JSON-safe dicts (handle DateTime etc.)."""
    serialized = []
    for record in results:
        row = {}
        for key, value in record.items():
            # Neo4j DateTime objects need string conversion
            if hasattr(value, "isoformat"):
                row[key] = value.isoformat()
            else:
                row[key] = value
        serialized.append(row)
    return serialized


class RetrievalService:
    """
    Orchestrates the controlled retrieval pipeline.

    Execution flow:
    1. Classify intent
    2. Resolve entities (if needed)
    3. Execute the matching parameterized Cypher strategy
    4. Return structured results

    Security guarantees:
    - Only predefined strategies are executed
    - All Cypher is parameterized
    - Result limits are enforced
    - No arbitrary Cypher exposure
    """

    def __init__(self):
        self.strategies = retrieval_strategies
        self.resolver = entity_resolver

    async def execute(self, request: RetrievalRequest) -> RetrievalResponse:
        """
        Main entry point for all retrieval requests.

        This method is the interception point for the future
        AegisGraph behavioral security layer.
        """
        # --- Phase: Intent Classification ---
        intent = await classify_intent(request.query)
        logger.info(f"Classified intent: {intent.value} for query: {request.query!r}")

        if intent == RetrievalIntent.UNSUPPORTED:
            return RetrievalResponse(
                query=request.query,
                intent=intent.value,
                results=[],
                result_count=0,
                strategy="none",
                metadata={"reason": "Query intent could not be determined."},
            )

        # --- Phase: Security Enforcement ---
        required_depth = INTENT_DEPTH_MAP.get(intent, 5)
        if required_depth > request.max_depth:
            logger.warning(f"Security block: required depth {required_depth} > max depth {request.max_depth}")
            return RetrievalResponse(
                query=request.query,
                intent=intent.value,
                results=[],
                result_count=0,
                strategy="blocked_by_policy",
                metadata={"reason": "Query exceeds permitted graph depth due to security policy."},
            )

        # --- Phase: Entity Resolution + Strategy Execution ---
        if intent == RetrievalIntent.EMPLOYEE_LOOKUP:
            return await self._handle_employee_lookup(request, intent)

        elif intent == RetrievalIntent.ALL_EMPLOYEES:
            return await self._handle_all_employees(request, intent)

        elif intent == RetrievalIntent.GRAPH_DISCOVERY:
            return await self._handle_graph_discovery(request, intent)

        elif intent == RetrievalIntent.SENT_EMAILS:
            return await self._handle_employee_emails(request, intent, "sent")

        elif intent == RetrievalIntent.RECEIVED_EMAILS:
            return await self._handle_employee_emails(request, intent, "received")

        elif intent == RetrievalIntent.EMAIL_CHUNKS:
            return await self._handle_email_chunks(request, intent)

        elif intent == RetrievalIntent.CHUNK_ENTITIES:
            return await self._handle_chunk_entities(request, intent)

        elif intent == RetrievalIntent.ENTITY_RELATIONSHIPS:
            return await self._handle_entity_relationships(request, intent)

        elif intent == RetrievalIntent.FREQUENT_COMMUNICATION:
            return await self._handle_frequent_communication(request, intent)

        elif intent == RetrievalIntent.TOPICAL_FOOTPRINT:
            return await self._handle_topical_footprint(request, intent)

        elif intent == RetrievalIntent.ORGANIZATION_INFO:
            return await self._handle_organization_info(request, intent)

        elif intent == RetrievalIntent.PERSON_CONNECTION:
            return await self._handle_person_connection(request, intent)

        # Should not reach here
        return RetrievalResponse(
            query=request.query,
            intent=intent.value,
            results=[],
            result_count=0,
            strategy="none",
            metadata={"reason": "Unhandled intent."},
        )

    # ------------------------------------------------------------------
    # Intent handlers
    # ------------------------------------------------------------------

    async def _handle_employee_lookup(
        self, request: RetrievalRequest, intent: RetrievalIntent
    ) -> RetrievalResponse:
        """Handle employee_lookup intent."""
        resolved = await self.resolver.resolve_employee(request.query)
        results = _serialize_results(resolved.matches)

        return RetrievalResponse(
            query=request.query,
            intent=intent.value,
            resolved_entities=[resolved],
            results=results,
            result_count=len(results),
            strategy="employee_lookup",
            metadata={"resolution_status": resolved.status.value},
        )

    async def _handle_all_employees(
        self, request: RetrievalRequest, intent: RetrievalIntent
    ) -> RetrievalResponse:
        """Handle all_employees intent by searching broadly."""
        # Empty string with the standard lookup returns the top N employees
        raw_results = await self.strategies.lookup_employee_by_name("", limit=request.limit)
        results = _serialize_results(raw_results)

        return RetrievalResponse(
            query=request.query,
            intent=intent.value,
            results=results,
            result_count=len(results),
            strategy="all_employees",
        )

    async def _handle_graph_discovery(
        self, request: RetrievalRequest, intent: RetrievalIntent
    ) -> RetrievalResponse:
        """Handle graph_discovery intent (help/discovery queries)."""
        return RetrievalResponse(
            query=request.query,
            intent=intent.value,
            results=[{
                "AegisGraph_Help": "AegisGraph is a secure Graph-RAG system over the Enron email dataset.",
                "Schema": "It contains Employees, Emails, text Chunks, and named Entities.",
                "Capabilities": "Users can explore employees, their sent/received emails, email chunks, entities mentioned in chunks, and entity co-occurrence relationships."
            }],
            result_count=1,
            strategy="graph_discovery",
            metadata={"reason": "User requested graph discovery or help."},
        )

    async def _handle_employee_emails(
        self, request: RetrievalRequest, intent: RetrievalIntent, direction: str
    ) -> RetrievalResponse:
        """Handle sent_emails or received_emails intent."""
        resolved = await self.resolver.resolve_employee(request.query)

        if resolved.status == ResolutionStatus.NOT_FOUND:
            return RetrievalResponse(
                query=request.query,
                intent=intent.value,
                resolved_entities=[resolved],
                results=[],
                result_count=0,
                strategy=f"{direction}_emails",
                metadata={
                    "resolution_status": resolved.status.value,
                    "reason": f"No employee found matching the query.",
                },
            )

        if resolved.status == ResolutionStatus.AMBIGUOUS:
            return RetrievalResponse(
                query=request.query,
                intent=intent.value,
                resolved_entities=[resolved],
                results=[],
                result_count=0,
                strategy=f"{direction}_emails",
                metadata={
                    "resolution_status": resolved.status.value,
                    "reason": "Multiple employees matched. Please be more specific.",
                    "candidates": _serialize_results(resolved.matches),
                },
            )

        # Exactly one match
        employee_id = resolved.matches[0]["employee_id"]
        if direction == "sent":
            raw_results = await self.strategies.get_sent_emails(
                employee_id, limit=request.limit
            )
        else:
            raw_results = await self.strategies.get_received_emails(
                employee_id, limit=request.limit
            )

        results = _serialize_results(raw_results)

        return RetrievalResponse(
            query=request.query,
            intent=intent.value,
            resolved_entities=[resolved],
            results=results,
            result_count=len(results),
            strategy=f"{direction}_emails",
            metadata={
                "resolution_status": resolved.status.value,
                "employee_id": employee_id,
                "limit_applied": request.limit,
            },
        )

    async def _handle_email_chunks(
        self, request: RetrievalRequest, intent: RetrievalIntent
    ) -> RetrievalResponse:
        """Handle email_chunks intent. Expects an email_id in the query."""
        # Extract something that looks like an email_id (enron_...)
        import re

        email_id_match = re.search(r"(enron_[a-f0-9]+)", request.query, re.IGNORECASE)
        if not email_id_match:
            return RetrievalResponse(
                query=request.query,
                intent=intent.value,
                results=[],
                result_count=0,
                strategy="email_chunks",
                metadata={
                    "reason": "No email_id found in query. Please provide an email_id like 'enron_abc123'."
                },
            )

        email_id = email_id_match.group(1)
        raw_results = await self.strategies.get_email_chunks(
            email_id, limit=request.limit
        )
        results = _serialize_results(raw_results)

        return RetrievalResponse(
            query=request.query,
            intent=intent.value,
            results=results,
            result_count=len(results),
            strategy="email_chunks",
            metadata={"email_id": email_id, "limit_applied": request.limit},
        )

    async def _handle_chunk_entities(
        self, request: RetrievalRequest, intent: RetrievalIntent
    ) -> RetrievalResponse:
        """Handle chunk_entities intent. Expects a chunk_id in the query."""
        import re

        chunk_id_match = re.search(
            r"(chk_enron_[a-f0-9]+_\d+)", request.query, re.IGNORECASE
        )
        if not chunk_id_match:
            return RetrievalResponse(
                query=request.query,
                intent=intent.value,
                results=[],
                result_count=0,
                strategy="chunk_entities",
                metadata={
                    "reason": "No chunk_id found in query. Please provide a chunk_id like 'chk_enron_abc123_0'."
                },
            )

        chunk_id = chunk_id_match.group(1)
        raw_results = await self.strategies.get_chunk_entities(
            chunk_id, limit=request.limit
        )
        results = _serialize_results(raw_results)

        return RetrievalResponse(
            query=request.query,
            intent=intent.value,
            results=results,
            result_count=len(results),
            strategy="chunk_entities",
            metadata={"chunk_id": chunk_id, "limit_applied": request.limit},
        )

    async def _handle_entity_relationships(
        self, request: RetrievalRequest, intent: RetrievalIntent
    ) -> RetrievalResponse:
        """Handle entity_relationships intent."""
        import re

        # Try to find an entity_id directly
        entity_id_match = re.search(
            r"(ent_[a-z]+_[a-f0-9]+)", request.query, re.IGNORECASE
        )

        if entity_id_match:
            entity_id = entity_id_match.group(1)
            raw_results = await self.strategies.get_entity_relationships(
                entity_id, limit=request.limit
            )
            results = _serialize_results(raw_results)
            return RetrievalResponse(
                query=request.query,
                intent=intent.value,
                results=results,
                result_count=len(results),
                strategy="entity_relationships",
                metadata={"entity_id": entity_id, "limit_applied": request.limit},
            )

        # Otherwise try to resolve an entity by name
        # Extract the entity name from patterns like "entities related to X"
        name_match = re.search(
            r"(?:related|connected|linked)\s+to\s+(.+)", request.query, re.IGNORECASE
        )
        entity_name = name_match.group(1).strip() if name_match else request.query

        resolved = await self.resolver.resolve_entity(entity_name)

        if resolved.status == ResolutionStatus.NOT_FOUND:
            return RetrievalResponse(
                query=request.query,
                intent=intent.value,
                resolved_entities=[resolved],
                results=[],
                result_count=0,
                strategy="entity_relationships",
                metadata={
                    "resolution_status": resolved.status.value,
                    "reason": f"No entity found matching '{entity_name}'.",
                },
            )

        if resolved.status == ResolutionStatus.AMBIGUOUS:
            return RetrievalResponse(
                query=request.query,
                intent=intent.value,
                resolved_entities=[resolved],
                results=[],
                result_count=0,
                strategy="entity_relationships",
                metadata={
                    "resolution_status": resolved.status.value,
                    "reason": "Multiple entities matched. Please be more specific.",
                    "candidates": _serialize_results(resolved.matches),
                },
            )

        # Exactly one match
        entity_id = resolved.matches[0]["entity_id"]
        raw_results = await self.strategies.get_entity_relationships(
            entity_id, limit=request.limit
        )
        results = _serialize_results(raw_results)

        return RetrievalResponse(
            query=request.query,
            intent=intent.value,
            resolved_entities=[resolved],
            results=results,
            result_count=len(results),
            strategy="entity_relationships",
            metadata={
                "resolution_status": resolved.status.value,
                "entity_id": entity_id,
                "limit_applied": request.limit,
            },
        )

    async def _handle_frequent_communication(
        self, request: RetrievalRequest, intent: RetrievalIntent
    ) -> RetrievalResponse:
        resolved = await self.resolver.resolve_employee(request.query)
        if resolved.status != ResolutionStatus.FOUND:
            return RetrievalResponse(
                query=request.query,
                intent=intent.value,
                resolved_entities=[resolved],
                results=[],
                result_count=0,
                strategy="frequent_communication",
                metadata={"reason": "Could not uniquely resolve employee."}
            )
        employee_id = resolved.matches[0]["employee_id"]
        raw_results = await self.strategies.get_frequent_communication(employee_id, limit=request.limit)
        results = _serialize_results(raw_results)
        return RetrievalResponse(
            query=request.query,
            intent=intent.value,
            resolved_entities=[resolved],
            results=results,
            result_count=len(results),
            strategy="frequent_communication"
        )

    async def _handle_topical_footprint(
        self, request: RetrievalRequest, intent: RetrievalIntent
    ) -> RetrievalResponse:
        resolved = await self.resolver.resolve_employee(request.query)
        if resolved.status != ResolutionStatus.FOUND:
            return RetrievalResponse(
                query=request.query,
                intent=intent.value,
                resolved_entities=[resolved],
                results=[],
                result_count=0,
                strategy="topical_footprint",
                metadata={"reason": "Could not uniquely resolve employee."}
            )
        employee_id = resolved.matches[0]["employee_id"]
        raw_results = await self.strategies.get_topical_footprint(employee_id, limit=request.limit)
        results = _serialize_results(raw_results)
        return RetrievalResponse(
            query=request.query,
            intent=intent.value,
            resolved_entities=[resolved],
            results=results,
            result_count=len(results),
            strategy="topical_footprint"
        )

    async def _handle_organization_info(
        self, request: RetrievalRequest, intent: RetrievalIntent
    ) -> RetrievalResponse:
        resolved = await self.resolver.resolve_employee(request.query)
        if resolved.status != ResolutionStatus.FOUND:
            return RetrievalResponse(
                query=request.query,
                intent=intent.value,
                resolved_entities=[resolved],
                results=[],
                result_count=0,
                strategy="organization_info",
                metadata={"reason": "Could not uniquely resolve employee."}
            )
        employee_id = resolved.matches[0]["employee_id"]
        raw_results = await self.strategies.get_organization(employee_id, limit=request.limit)
        results = _serialize_results(raw_results)
        return RetrievalResponse(
            query=request.query,
            intent=intent.value,
            resolved_entities=[resolved],
            results=results,
            result_count=len(results),
            strategy="organization_info"
        )

    async def _handle_person_connection(
        self, request: RetrievalRequest, intent: RetrievalIntent
    ) -> RetrievalResponse:
        import re
        # Attempt to find two names. Use a simple split on ' and ' or ' with '
        match = re.search(r"(?:between|connect(?:ion|ed)\s+(?:to|between))\s+(.*?)\s+(?:and|with)\s+(.*)", request.query, re.IGNORECASE)
        
        if not match:
             return RetrievalResponse(
                query=request.query,
                intent=intent.value,
                results=[],
                result_count=0,
                strategy="person_connection",
                metadata={"reason": "Could not identify two distinct names in query."}
            )
            
        name1 = match.group(1).strip()
        name2 = match.group(2).strip()
        
        resolved1 = await self.resolver.resolve_employee(name1)
        resolved2 = await self.resolver.resolve_employee(name2)
        
        if resolved1.status != ResolutionStatus.FOUND or resolved2.status != ResolutionStatus.FOUND:
             return RetrievalResponse(
                query=request.query,
                intent=intent.value,
                resolved_entities=[resolved1, resolved2],
                results=[],
                result_count=0,
                strategy="person_connection",
                metadata={"reason": "Could not uniquely resolve both employees."}
            )
            
        emp_id1 = resolved1.matches[0]["employee_id"]
        emp_id2 = resolved2.matches[0]["employee_id"]
        
        # Determine strict bounded limit based on effective graph depth. We bound it aggressively to min(request.max_depth, 3) 
        # so even a permissive policy doesn't result in massive arbitrary traversals.
        safe_depth = min(request.max_depth, 3)
        if safe_depth < 1:
             return RetrievalResponse(
                query=request.query,
                intent=intent.value,
                resolved_entities=[resolved1, resolved2],
                results=[],
                result_count=0,
                strategy="person_connection",
                metadata={"reason": "Graph depth limit prevents path traversal."}
            )
        
        raw_results = await self.strategies.get_person_connection(emp_id1, emp_id2, safe_depth)
        results = _serialize_results(raw_results)
        return RetrievalResponse(
            query=request.query,
            intent=intent.value,
            resolved_entities=[resolved1, resolved2],
            results=results,
            result_count=len(results),
            strategy="person_connection"
        )


# Module-level singleton
retrieval_service = RetrievalService()
