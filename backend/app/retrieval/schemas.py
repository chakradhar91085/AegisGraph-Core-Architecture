"""
AegisGraph Phase 2 — Pydantic schemas for the retrieval API.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class RetrievalIntent(str, Enum):
    EMPLOYEE_LOOKUP = "employee_lookup"
    SENT_EMAILS = "sent_emails"
    RECEIVED_EMAILS = "received_emails"
    EMAIL_CHUNKS = "email_chunks"
    CHUNK_ENTITIES = "chunk_entities"
    ENTITY_RELATIONSHIPS = "entity_relationships"
    GRAPH_DISCOVERY = "graph_discovery"
    ALL_EMPLOYEES = "all_employees"
    FREQUENT_COMMUNICATION = "frequent_communication"
    TOPICAL_FOOTPRINT = "topical_footprint"
    ORGANIZATION_INFO = "organization_info"
    PERSON_CONNECTION = "person_connection"
    UNSUPPORTED = "unsupported_intent"


class ResolutionStatus(str, Enum):
    FOUND = "found"
    AMBIGUOUS = "ambiguous"
    NOT_FOUND = "not_found"


class ResolvedEntity(BaseModel):
    """Result of resolving a user-provided name/email to a graph node."""
    type: str  # "employee" or "entity"
    query_value: str  # what the user provided
    status: ResolutionStatus
    matches: List[Dict[str, Any]] = Field(default_factory=list)


class RetrievalRequest(BaseModel):
    """Incoming retrieval query from the client."""
    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(default=10, ge=1, le=50)
    max_depth: int = Field(..., ge=0)
    response_mode: str = "ALLOW"


class RetrievalResponse(BaseModel):
    """Structured retrieval result returned to the client."""
    query: str
    intent: str
    resolved_entities: List[ResolvedEntity] = Field(default_factory=list)
    results: List[Dict[str, Any]] = Field(default_factory=list)
    result_count: int = 0
    strategy: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
