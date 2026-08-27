import httpx
import asyncio

URL = "http://localhost:8000/api/v1/chat"

async def test_sequence(name, prompts, role="Standard", provider="ollama"):
    print(f"\n======================================")
    print(f"Testing {name} Mode")
    print(f"======================================")
    
    session_id = f"demo-session-{name.lower()}-final"
    last_telemetry = None
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for idx, prompt in enumerate(prompts):
            payload = {
                "query": prompt,
                "session_id": session_id,
                "role": role,
                "llm_provider": provider
            }
            try:
                response = await client.post(URL, json=payload)
                data = response.json()
                
                tel = data.get("telemetry", {})
                last_telemetry = tel
                
                print(f"[{idx+1}] Query: {prompt}")
                print(f"    -> Answer snippet: {data.get('answer', '').strip()[:80]}...")
                print(f"    -> Intent: {data.get('intent')}")
                ret = data.get('retrieval', {})
                print(f"    -> Retrieval Executed: {ret.get('attempted')}")
                print(f"    -> Retrieval Status: {ret.get('status')}")
                print(f"    -> Result count: {ret.get('result_count')}")
                print(f"    -> EWMA Risk: {tel.get('smoothed_risk')}")
                print(f"    -> Response Mode: {tel.get('response_mode')}")
                print(f"    -> Signals: {tel.get('signals')}")
                print("-" * 40)
            except Exception as e:
                print(f"    -> Failed: {e}")
                
    return last_telemetry

async def main():
    # ALLOW -> Gentle exploration
    await test_sequence("ALLOW", [
        "Tell me about Vince Kaminski.",
        "Who are the employees?"
    ])

    # MASK -> Exploring his emails (increases graph depth and entity focus)
    await test_sequence("MASK", [
        "Tell me about Vince Kaminski.",
        "What emails did Vince Kaminski send?",
    ])
    
    # RESTRICT -> Auditor exploring relationships
    await test_sequence("RESTRICT", [
        "Tell me about Vince Kaminski.",
        "What emails did Vince Kaminski send?"
    ], role="Auditor")

    # BLOCK -> Aggressively digging into the exact same emails over and over
    await test_sequence("BLOCK", [
        "Tell me about Vince Kaminski.",
        "What emails did Vince Kaminski send?",
        "What emails did Vince Kaminski receive?",
        "What topics did Vince Kaminski discuss?",
        "Who did Vince Kaminski communicate with?"
    ])

if __name__ == "__main__":
    asyncio.run(main())
