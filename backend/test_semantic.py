import asyncio
import httpx

async def test_semantic():
    url = "http://localhost:8000/api/v1/chat"
    
    # Query designed to trigger SEMANTIC_SEARCH intent
    payload = {
        "query": "Find emails discussing the California energy crisis",
        "role": "Analyst",
        "llm_provider": "ollama"  # Or Gemini if configured
    }
    
    async with httpx.AsyncClient() as client:
        print(f"Sending query: '{payload['query']}'")
        resp = await client.post(url, json=payload, timeout=60.0)
        
        if resp.status_code == 200:
            data = resp.json()
            print("--- Success ---")
            print(f"Intent classified as: {data.get('intent')}")
            print(f"Strategy used: {data.get('retrieval', {}).get('strategy')}")
            print(f"Results found: {data.get('retrieval', {}).get('result_count')}")
            print("Answer:")
            print(data.get('answer'))
        else:
            print(f"Failed with {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_semantic())
