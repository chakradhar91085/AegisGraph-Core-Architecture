from fastapi import APIRouter, HTTPException
import logging
from sqlalchemy.future import select
from app.db.postgres import AsyncSessionLocal
from app.security.db_models import AuditSession, AuditQuery
import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/audit/sessions")
async def get_audit_sessions(limit: int = 50):
    """
    Retrieve the most recent audit sessions.
    """
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(AuditSession).order_by(AuditSession.started_at.desc()).limit(limit)
            result = await db.execute(stmt)
            sessions = result.scalars().all()
            
            # Serialize for JSON
            return {
                "sessions": [
                    {
                        "session_id": s.id,
                        "role": s.role,
                        "started_at": s.started_at.isoformat() + "Z" if s.started_at else None,
                        "ended_at": s.ended_at.isoformat() + "Z" if s.ended_at else None,
                        "status": s.status,
                        "query_count": s.query_count,
                        "final_risk_score": s.final_risk_score,
                        "peak_risk_score": s.peak_risk_score,
                        "final_behavioral_mode": s.final_behavioral_mode,
                        "highest_behavioral_mode": s.highest_behavioral_mode
                    }
                    for s in sessions
                ]
            }
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit/sessions/{session_id}/queries")
async def get_session_queries(session_id: str):
    """
    Retrieve all queries for a specific session.
    """
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(AuditQuery).where(AuditQuery.session_id == session_id).order_by(AuditQuery.timestamp.asc())
            result = await db.execute(stmt)
            queries = result.scalars().all()
            
            return {
                "queries": [
                    {
                        "id": q.id,
                        "timestamp": q.timestamp.isoformat() + "Z" if q.timestamp else None,
                        "query": q.query,
                        "intent": q.intent,
                        "risk_score": q.risk_score,
                        "behavioral_mode": q.behavioral_mode,
                        "retrieval_outcome": q.retrieval_outcome,
                        "masked": q.masked,
                        "attenuated": q.attenuated,
                        "blocked": q.blocked,
                        "result_count": q.result_count,
                        "role": q.role,
                        "llm_provider": q.llm_provider
                    }
                    for q in queries
                ]
            }
    except Exception as e:
        logger.error(f"Error fetching queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audit/sessions/{session_id}/end")
async def end_session(session_id: str):
    """
    Mark a session as completed.
    """
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(AuditSession).where(AuditSession.id == session_id)
            result = await db.execute(stmt)
            session = result.scalar_one_or_none()
            
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
                
            if session.status != "COMPLETED":
                session.status = "COMPLETED"
                session.ended_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                await db.commit()
                
            return {"status": "success", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit")
async def get_audit_logs(limit: int = 100):
    """Legacy endpoint for backward compatibility during transition if needed"""
    return {"logs": []}
