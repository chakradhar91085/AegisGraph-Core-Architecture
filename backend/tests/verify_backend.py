import asyncio
import httpx
from typing import Dict, Any

# We use the existing clients for direct DB/LLM tests
from app.db.neo4j import neo4j_client
from app.llm.provider_factory import get_llm_provider

API_URL = "http://127.0.0.1:8000/api/v1"

async def test_fastapi_health() -> bool:
    print("--- Test A: FastAPI health ---")
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{API_URL}/health")
            r.raise_for_status()
            print("FastAPI Health:", r.json())
            return True
        except Exception as e:
            print("FastAPI Health Failed:", e)
            return False

async def test_neo4j_connectivity() -> bool:
    print("--- Test B: Neo4j connectivity ---")
    try:
        healthy = await neo4j_client.check_health()
        print("Neo4j Connectivity:", healthy)
        return healthy
    except Exception as e:
        print("Neo4j Connectivity Failed:", e)
        return False

async def test_ollama_connectivity() -> bool:
    print("--- Test C: Ollama connectivity ---")
    try:
        provider = get_llm_provider("ollama")
        healthy = await provider.check_health()
        print("Ollama Connectivity:", healthy)
        return healthy
    except Exception as e:
        print("Ollama Connectivity Failed:", e)
        return False

async def test_neo4j_read_query():
    print("--- Test D: Real Neo4j read query (Schema Inspection) ---")
    try:
        # Get Node Labels
        labels = await neo4j_client.execute_read("CALL db.labels() YIELD label RETURN label")
        print("Node Labels:", [l['label'] for l in labels])
        
        # Get Relationship Types
        rels = await neo4j_client.execute_read("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
        print("Relationship Types:", [r['relationshipType'] for r in rels])
        
        # Get counts (using apoc.meta.stats if available or a simple count)
        # We will do a generic count for each label discovered
        print("Node Counts by Label:")
        for l in labels:
            label = l['label']
            count = await neo4j_client.execute_read(f"MATCH (n:`{label}`) RETURN count(n) as count")
            print(f"  {label}: {count[0]['count']}")
            
        return True
    except Exception as e:
        print("Neo4j Read Query Failed:", e)
        return False

async def test_real_chat():
    print("--- Test E: Real /chat request ---")
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            payload = {"query": "Find employee skilling"}
            r = await client.post(f"{API_URL}/chat", json=payload)
            r.raise_for_status()
            print("Chat Response:", r.json())
            return True
        except Exception as e:
            print("Chat Request Failed:", e)
            return False

async def test_malformed_request():
    print("--- Test F: Malformed request ---")
    async with httpx.AsyncClient() as client:
        try:
            payload = {"wrong_key": "Find employee skilling"}
            r = await client.post(f"{API_URL}/chat", json=payload)
            print("Expected failure status:", r.status_code)
            return r.status_code == 422
        except Exception as e:
            print("Malformed request check errored:", e)
            return False

async def test_health_endpoints():
    print("--- Test G/H: Health endpoints (Neo4j & Ollama API routes) ---")
    async with httpx.AsyncClient() as client:
        try:
            r1 = await client.get(f"{API_URL}/health/neo4j")
            print("Neo4j endpoint:", r1.json() if r1.status_code == 200 else r1.status_code)
            
            r2 = await client.get(f"{API_URL}/health/ollama")
            print("Ollama endpoint:", r2.json() if r2.status_code == 200 else r2.status_code)
            return True
        except Exception as e:
            print("Health endpoints test failed:", e)
            return False

async def run_all():
    await neo4j_client.connect()
    
    await test_fastapi_health()
    await test_neo4j_connectivity()
    await test_ollama_connectivity()
    await test_neo4j_read_query()
    await test_health_endpoints()
    await test_malformed_request()
    await test_real_chat()

    await neo4j_client.close()

if __name__ == "__main__":
    asyncio.run(run_all())
