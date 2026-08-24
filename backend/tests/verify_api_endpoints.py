import requests
import json
import uuid
import sys
import time

BASE_URL = "http://localhost:8000/api/v1/chat"

def run_test(query: str, session_id: str, label: str):
    print(f"\n=====================================")
    print(f"TEST: {label}")
    print(f"QUERY: {query}")
    print(f"SESSION ID: {session_id}")
    
    payload = {
        "query": query,
        "session_id": session_id
    }
    
    start_time = time.time()
    response = requests.post(BASE_URL, json=payload)
    end_time = time.time()
    
    print(f"TIME: {end_time - start_time:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        print(f"STATUS: SUCCESS")
        print(f"INTENT: {data.get('intent')}")
        print(f"STRATEGY: {data.get('retrieval', {}).get('strategy')}")
        print(f"RESULT COUNT: {data.get('retrieval', {}).get('result_count')}")
        print(f"ANSWER:\n{data.get('answer')}")
        
        telemetry = data.get('telemetry', {})
        print(f"\nTELEMETRY:")
        print(f"  Instantaneous Risk: {telemetry.get('instantaneous_risk')}")
        print(f"  Smoothed Risk: {telemetry.get('smoothed_risk')}")
        print(f"  Risk Level: {telemetry.get('policy', {}).get('risk_level')}")
        print(f"  Effective Context Limit: {telemetry.get('policy', {}).get('effective_context_limit')}")
        print(f"  Effective Graph Depth: {telemetry.get('policy', {}).get('effective_graph_depth')}")
        
        return data
    else:
        print(f"STATUS: FAILED {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    print("Beginning End-to-End Enriched Graph Validation...")
    
    session_id = str(uuid.uuid4())
    
    # 1. Frequent Communication
    run_test(
        "Who does veronica.espinoza@enron.com communicate with most frequently?",
        session_id,
        "FREQUENT COMMUNICATION"
    )
    
    # 2. Topical Footprint
    run_test(
        "What topics does veronica.espinoza@enron.com frequently discuss?",
        session_id,
        "TOPICAL FOOTPRINT"
    )
    
    # 3. Organization Information
    run_test(
        "Which organization does veronica.espinoza@enron.com belong to?",
        session_id,
        "ORGANIZATION INFO"
    )
    
    # 4. Person-to-Person Connection
    run_test(
        "What is the connection between veronica.espinoza@enron.com and russell.diamond@enron.com",
        session_id,
        "PERSON CONNECTION"
    )
    
    # 5. Exploratory Sequence to test Security (Session Continuity)
    # We will blast a few exploratory queries to trigger elevated risk
    print("\n--- BEGINNING SECURITY STRESS TEST ---")
    for i in range(5):
        run_test(
            f"Show me all the emails sent by employee_{i}@enron.com",
            session_id,
            f"SECURITY PROBE {i+1}"
        )
        time.sleep(0.1) # Short delay to allow temporal drift to calculate somewhat
        
    # After stress test, try connection again to see if policy blocks it
    run_test(
        "What is the connection between john@enron.com and jane@enron.com",
        session_id,
        "PERSON CONNECTION UNDER STRESS"
    )

    print("\nTests complete.")
