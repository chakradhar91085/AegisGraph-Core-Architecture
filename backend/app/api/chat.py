import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, Literal
import logging

from app.rag.service import graph_rag_service

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    role: str = "Standard"
    llm_provider: Optional[Literal["gemini", "ollama"]] = None

class ChatResponse(BaseModel):
    answer: str
    session_id: str
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
    Phase 6B Chat Endpoint: Secure Graph-RAG flow with selectable LLM provider.
    """
    session_id = request.session_id if request.session_id else str(uuid.uuid4())
    logger.info(f"Starting chat request for session: {session_id}, provider: {request.llm_provider or 'default'}")
    
    try:
        # Delegate to the GraphRAG service orchestrator
        rag_result = await graph_rag_service.generate_answer(
            request.query,
            session_id=session_id,
            role=request.role,
            llm_provider=request.llm_provider,
        )
        
        return ChatResponse(
            answer=rag_result["answer"],
            session_id=session_id,
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
