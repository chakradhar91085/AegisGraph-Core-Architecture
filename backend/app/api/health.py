from fastapi import APIRouter, HTTPException
from app.db.neo4j import neo4j_client
from app.llm.provider_factory import get_llm_provider

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Basic health check endpoint for FastAPI backend.
    """
    return {"status": "healthy", "service": "fastapi"}

@router.get("/health/neo4j")
async def neo4j_health_check():
    """
    Health check for Neo4j connection.
    """
    is_healthy = await neo4j_client.check_health()
    if is_healthy:
        return {"status": "healthy", "service": "neo4j"}
    else:
        raise HTTPException(status_code=503, detail="Neo4j service is unreachable or unhealthy")

@router.get("/health/llm")
async def llm_health_check(provider: str = None):
    """
    Health check for the selected LLM provider.
    Accepts ?provider=ollama.
    """
    llm = get_llm_provider(provider)
    is_healthy = await llm.check_health()
    if is_healthy:
        return {"status": "healthy", "service": llm.provider_name}
    else:
        raise HTTPException(
            status_code=503,
            detail=f"{llm.provider_name} LLM service is unreachable or unhealthy"
        )
