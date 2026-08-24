"""
AegisGraph Phase 2 — Retrieval API endpoint.

POST /api/v1/retrieval/query

Accepts a natural-language query and returns structured retrieval results.
Does not generate LLM answers. Does not expose arbitrary Cypher.
"""
from fastapi import APIRouter
from app.retrieval.schemas import RetrievalRequest, RetrievalResponse
from app.retrieval.service import retrieval_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/retrieval/query", response_model=RetrievalResponse)
async def retrieval_query(request: RetrievalRequest) -> RetrievalResponse:
    """
    Controlled Graph-RAG retrieval endpoint.

    Accepts a natural-language query, classifies intent, resolves entities,
    executes parameterized Cypher against Neo4j, and returns structured results.

    Security:
    - Only predefined Cypher templates are used.
    - All user input is passed as Neo4j query parameters.
    - Result counts are capped at 50.
    - No raw Cypher execution is exposed.
    """
    logger.info(f"Retrieval request: {request.query!r} (limit={request.limit})")

    response = await retrieval_service.execute(request)

    logger.info(
        f"Retrieval complete: intent={response.intent}, "
        f"results={response.result_count}, strategy={response.strategy}"
    )

    return response
