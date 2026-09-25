import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import logging

from app.core.config import settings
from app.db.postgres import AsyncSessionLocal
from app.rag.service import graph_rag_service
from app.security.auth import User, current_user
from app.security.db_models import AuditSession
from app.security.session import session_store
from app.security.tickets import issue_ticket, verify_ticket
from sqlalchemy.future import select
import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    session_token: Optional[str] = None
    llm_provider: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    session_token: str
    intent: str
    retrieval: Dict[str, Any]
    status: str
    telemetry: Optional[Dict[str, Any]] = None
    graph_data: Optional[Dict[str, Any]] = None
    llm_provider: Optional[str] = None

@router.get("/me")
async def me(user: User = Depends(current_user)):
    return {"user_id": user.user_id, "role": user.role}

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, user: User = Depends(current_user)):
    """
    Secure Graph-RAG chat endpoint.

    Identity and role come from the verified login token, never from the
    request body. The session ticket only groups a user's messages for the
    audit trail; the user's remembered risk is keyed by user id, so dropping
    the ticket does not reset it.
    """
    session_id = (verify_ticket(request.session_token, user.user_id) if request.session_token else None) or str(uuid.uuid4())

    logger.info(f"Chat request: user={user.user_id} session={session_id} role={user.role}")

    try:
        rag_result = await graph_rag_service.generate_answer(
            request.query,
            session_id=session_id,
            role=user.role,
            llm_provider=request.llm_provider,
            user_id=user.user_id,
        )

        token, session_id = issue_ticket(user.user_id, session_id=session_id)

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


class SessionRef(BaseModel):
    session_token: str

@router.post("/session/end")
async def end_own_session(ref: SessionRef, user: User = Depends(current_user)):
    """Mark the caller's own audit session as completed (proved by its ticket)."""
    session_id = verify_ticket(ref.session_token, user.user_id)
    if not session_id:
        raise HTTPException(status_code=404, detail="Session not found")
    async with AsyncSessionLocal() as db:
        session = (await db.execute(select(AuditSession).where(AuditSession.id == session_id))).scalar_one_or_none()
        if session and session.status != "COMPLETED":
            session.status = "COMPLETED"
            session.ended_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            await db.commit()
    return {"status": "success"}

@router.post("/session/reset")
async def reset_risk(user: User = Depends(current_user)):
    """Demo convenience: forget the caller's remembered risk. Off unless DEMO_ALLOW_RISK_RESET=true."""
    if not settings.DEMO_ALLOW_RISK_RESET:
        raise HTTPException(status_code=403, detail="Risk reset is disabled")
    session_store.reset(user.user_id)
    return {"status": "reset"}
