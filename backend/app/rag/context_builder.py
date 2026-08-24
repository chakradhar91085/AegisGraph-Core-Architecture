"""
AegisGraph Phase 3A — Context Builder

Converts structured retrieval results (from Phase 2) into a compact,
deterministic text context for the LLM. Enforces size limits.
"""
from typing import List, Dict, Any
from app.retrieval.schemas import RetrievalResponse, ResolutionStatus
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ContextBuilder:
    def __init__(self):
        self.max_records = settings.MAX_RECORDS
        self.max_chunk_chars = settings.MAX_CHUNK_CHARS
        self.max_context_chars = settings.MAX_CONTEXT_CHARS

    def build_context(self, response: RetrievalResponse, effective_limit: int = None) -> str:
        """
        Takes a RetrievalResponse and formats it into a deterministic text block.
        Truncates according to limits and dynamic effective_limit.
        """
        if not response.results or response.result_count == 0:
            return "No relevant context found."

        # Determine active record limit
        limit = min(effective_limit, self.max_records) if effective_limit is not None else self.max_records
        
        # Truncate number of records
        results_to_process = response.results[:limit]
        
        context_parts = []
        strategy = response.strategy

        if strategy == "employee_lookup":
            context_parts.extend(self._format_employee(response, results_to_process))
        elif strategy in ("sent_emails", "received_emails"):
            context_parts.extend(self._format_emails(response, results_to_process))
        elif strategy == "email_chunks":
            context_parts.extend(self._format_chunks(response, results_to_process))
        elif strategy == "chunk_entities":
            context_parts.extend(self._format_entities(response, results_to_process))
        elif strategy == "entity_relationships":
            context_parts.extend(self._format_entity_relationships(response, results_to_process))
        elif strategy == "frequent_communication":
            context_parts.extend(self._format_frequent_communication(response, results_to_process))
        elif strategy == "topical_footprint":
            context_parts.extend(self._format_topical_footprint(response, results_to_process))
        elif strategy == "organization_info":
            context_parts.extend(self._format_organization_info(response, results_to_process))
        elif strategy == "person_connection":
            context_parts.extend(self._format_person_connection(response, results_to_process))
        else:
            # Fallback formatting
            context_parts.extend(self._format_generic(response, results_to_process))
            
        # Join and truncate total context length
        full_context = "\n\n".join(context_parts)
        
        if len(full_context) > self.max_context_chars:
            logger.warning(
                f"Context length ({len(full_context)}) exceeds MAX_CONTEXT_CHARS "
                f"({self.max_context_chars}). Truncating."
            )
            full_context = full_context[:self.max_context_chars] + "\n\n...[TRUNCATED due to length limits]"
            
        return full_context

    def _get_subject_header(self, response: RetrievalResponse) -> str:
        """Helper to extract subject info securely from resolved entities."""
        if not response.resolved_entities:
            return ""
        parts = []
        for i, entity in enumerate(response.resolved_entities):
            if entity.status == ResolutionStatus.FOUND and entity.matches:
                match = entity.matches[0]
                name = match.get("name") or match.get("entity_name") or entity.query_value
                typ = "Employee" if entity.type == "employee" else "Entity"
                if len(response.resolved_entities) > 1:
                    parts.append(f"SUBJECT {i+1}: {name} ({typ})")
                else:
                    parts.append(f"SUBJECT: {name} ({typ})")
        if parts:
            return "\n".join(parts) + "\n"
        return ""

    def _format_employee(self, response: RetrievalResponse, results: List[Dict[str, Any]]) -> List[str]:
        parts = []
        for row in results:
            part = (
                "RETRIEVED RECORD TYPE: Employee Profile\n"
                f"Name: {row.get('name', '')}\n"
                f"Email: {row.get('email', '')}\n"
                f"Domain: {row.get('domain', '')}\n"
                f"Mailbox: {row.get('mailbox', '')}"
            )
            parts.append(part)
        return parts

    def _format_emails(self, response: RetrievalResponse, results: List[Dict[str, Any]]) -> List[str]:
        header = self._get_subject_header(response)
        parts = [f"{header}RETRIEVED RECORD TYPE: Email Metadata\nINTENT: {response.intent.upper()}"]
        for row in results:
            part = (
                f"- Email ID: {row.get('email_id', '')} | "
                f"Subject: {row.get('subject', '')} | "
                f"Timestamp: {row.get('timestamp', '')} | "
                f"Folder: {row.get('source_folder', '')}"
            )
            parts.append(part)
        return ["\n".join(parts)]

    def _format_chunks(self, response: RetrievalResponse, results: List[Dict[str, Any]]) -> List[str]:
        parts = [f"RETRIEVED RECORD TYPE: Email Content Chunk\nINTENT: {response.intent.upper()}"]
        for row in results:
            text = str(row.get('text', ''))
            if len(text) > self.max_chunk_chars:
                text = text[:self.max_chunk_chars] + "... [TRUNCATED]"
            part = (
                f"Chunk ID: {row.get('chunk_id', '')} | Index: {row.get('chunk_index', '')}\n"
                f"Text:\n{text}"
            )
            parts.append(part)
        return parts

    def _format_entities(self, response: RetrievalResponse, results: List[Dict[str, Any]]) -> List[str]:
        parts = [f"RETRIEVED RECORD TYPE: Entities Mentioned in Chunk\nINTENT: {response.intent.upper()}"]
        for row in results:
            parts.append(
                f"- {row.get('entity_name', '')} (Type: {row.get('entity_type', '')}, Mentions: {row.get('mention_count', '')})"
            )
        return ["\n".join(parts)]

    def _format_entity_relationships(self, response: RetrievalResponse, results: List[Dict[str, Any]]) -> List[str]:
        header = self._get_subject_header(response)
        parts = [f"{header}RETRIEVED RECORD TYPE: Entity Co-occurrences\nINTENT: {response.intent.upper()}"]
        for row in results:
            parts.append(
                f"- {row.get('entity_name', '')} (Type: {row.get('entity_type', '')}, Co-occurrences: {row.get('co_occurrence_count', '')})"
            )
        return ["\n".join(parts)]

    def _format_generic(self, response: RetrievalResponse, results: List[Dict[str, Any]]) -> List[str]:
        header = self._get_subject_header(response)
        parts = [f"{header}RETRIEVED RECORD TYPE: Generic Records\nINTENT: {response.intent.upper()}"]
        for row in results:
            prop_str = ", ".join(f"{k}: {v}" for k, v in row.items())
            parts.append(f"- {prop_str}")
        return ["\n".join(parts)]

    def _format_frequent_communication(self, response: RetrievalResponse, results: List[Dict[str, Any]]) -> List[str]:
        header = self._get_subject_header(response)
        parts = [f"{header}RETRIEVED RECORD TYPE: Frequent Communication Network\nINTENT: {response.intent.upper()}"]
        for row in results:
            parts.append(
                f"- {row.get('name', '')} — communication interactions: {row.get('weight', '')}"
            )
        return ["\n".join(parts)]

    def _format_topical_footprint(self, response: RetrievalResponse, results: List[Dict[str, Any]]) -> List[str]:
        header = self._get_subject_header(response)
        parts = [f"{header}RETRIEVED RECORD TYPE: Frequently Discussed Topics\nINTENT: {response.intent.upper()}"]
        for row in results:
            parts.append(
                f"- {row.get('entity_name', '')} ({row.get('entity_type', '')}) — observed {row.get('count', '')} times"
            )
        return ["\n".join(parts)]

    def _format_organization_info(self, response: RetrievalResponse, results: List[Dict[str, Any]]) -> List[str]:
        header = self._get_subject_header(response)
        parts = [f"{header}RETRIEVED RECORD TYPE: Organization Membership\nINTENT: {response.intent.upper()}"]
        for row in results:
            parts.append(
                f"- Organization: {row.get('organization_name', '')}"
            )
        return ["\n".join(parts)]

    def _format_person_connection(self, response: RetrievalResponse, results: List[Dict[str, Any]]) -> List[str]:
        header = self._get_subject_header(response)
        parts = [f"{header}RETRIEVED RECORD TYPE: Observed Communication Path\nINTENT: {response.intent.upper()}"]
        for row in results:
            names = " -> ".join(row.get('path_names', []))
            weights = ", ".join(str(w) for w in row.get('path_weights', []))
            parts.append(f"- Path: {names}")
            parts.append(f"  Observed email interactions along path: {weights}")
        return ["\n".join(parts)]


# Module-level singleton
context_builder = ContextBuilder()
