import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from app.rag.service import graph_rag_service
from app.security.tickets import issue_ticket, verify_ticket
from app.security.policy import ROLE_POLICIES

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    session_token: Optional[str] = None
    role: str = "Standard"
    llm_provider: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    session_token: str
    intent: str
    retrieval: Dict[str, Any]
    status: str
    telemetry: Optional[Dict[str, Any]] = None
    # Keep older fields for backwards compatibility if needed, but make optional
    retrieved_context: Optional[list] = None
    retrieval_metadata: Optional[dict] = None
    graph_data: Optional[Dict[str, Any]] = None
    llm_provider: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Secure Graph-RAG chat endpoint.

    Session identity and role are never trusted from freeform client fields
    once a session exists: the first message of a session may pick a role,
    but every message after that must present the signed `session_token`
    returned in the previous response, and the session id + role are read
    from that verified token — not from anything the client can edit.
    """
    verified = verify_ticket(request.session_token) if request.session_token else None

    if verified:
        session_id, role = verified
    else:
        # No valid ticket -> this is a brand-new session (fresh risk state),
        # generated server-side so a client can never dictate or replay a
        # session identity. Role is only ever taken from the client on this
        # first message of a session.
        session_id = str(uuid.uuid4())
        role = request.role if request.role in ROLE_POLICIES else "Standard"

    logger.info(f"Starting chat request for session: {session_id}, role: {role}, provider: {request.llm_provider or 'default'}")

    try:
        # Delegate to the GraphRAG service orchestrator
        rag_result = await graph_rag_service.generate_answer(
            request.query,
            session_id=session_id,
            role=role,
            llm_provider=request.llm_provider,
        )

        # Renew the ticket on every response so the session can continue.
        token, session_id = issue_ticket(role, session_id=session_id)

        return ChatResponse(
            answer=rag_result["answer"],
            session_id=session_id,
            session_token=token,
            intent=rag_result.get("intent", "unknown"),
            retrieval=rag_result.get("retrieval", {}),
            telemetry=rag_result.get("telemetry", None),
            graph_data=rag_result.get("graph_data", None),
            llm_provider=rag_result.get("llm_provider", None),
            status="success"
        )
    except Exception as e:
        logger.error(f"Error during chat generation for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during chat processing")
