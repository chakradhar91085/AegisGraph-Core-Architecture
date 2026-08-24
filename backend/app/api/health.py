from fastapi import APIRouter, HTTPException
from app.db.neo4j import neo4j_client
from app.llm.ollama_client import ollama_client
import asyncio

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
    is_healthy = neo4j_client.check_health()
    if is_healthy:
        return {"status": "healthy", "service": "neo4j"}
    else:
        raise HTTPException(status_code=503, detail="Neo4j service is unreachable or unhealthy")

@router.get("/health/ollama")
async def ollama_health_check():
    """
    Health check for Ollama service.
    """
    is_healthy = await ollama_client.check_health()
    if is_healthy:
        return {"status": "healthy", "service": "ollama"}
    else:
        raise HTTPException(status_code=503, detail="Ollama service is unreachable or unhealthy")
