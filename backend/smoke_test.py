import asyncio
import time
from fastapi.testclient import TestClient
from app.main import app

def run_smoke_test():
    client = TestClient(app)
    
    query = "What emails did Christopher Calger send?"
    
    print("--- LIVE SMOKE TEST ---")
    print(f"Endpoint: POST /api/v1/chat")
    print(f"Query: {query}")
    
    start_time = time.time()
    
    try:
        response = client.post("/api/v1/chat", json={"query": query})
        end_time = time.time()
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Intent: {data.get('intent')}")
            print(f"Neo4j Results Retrieved: {data.get('retrieval', {}).get('result_count')}")
            
            # Print the actual answer returned by Ollama
            print("\n--- Generated Answer ---")
            print(data.get("answer"))
            print("------------------------\n")
            print(f"Total Request Latency: {end_time - start_time:.2f} seconds")
        else:
            print("Response error:", response.text)
            
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    run_smoke_test()
