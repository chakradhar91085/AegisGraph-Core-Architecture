import asyncio
import httpx

API_URL = "http://127.0.0.1:8000/api/v1/chat"

# To get high risk, we need high temporal frequency, semantic drift, graph footprint, and entity focus.
# - High semantic drift: change topic rapidly (Enron -> Pandas -> Enron)
# - High temporal frequency: send queries rapidly without sleeping
# - High graph footprint: ask complex graph traversal queries ("frequent communication", "topical footprint", etc.)
# - High entity focus: keep asking about the same entity (e.g. "Vince Kaminski") repeatedly

async def send_query(client, session_id, role, query, delay=0):
    if delay > 0:
        await asyncio.sleep(delay)
    payload = {
        "session_id": session_id,
        "query": query,
        "role": role
    }
    response = await client.post(API_URL, json=payload, timeout=120.0)
    data = response.json()
    tel = data.get("telemetry", {})
    return {
        "query": query,
        "mode": tel.get("response_mode", "UNKNOWN"),
        "risk": tel.get("smoothed_risk", 0.0),
        "inst_risk": tel.get("instantaneous_risk", 0.0),
        "status": data.get("retrieval", {}).get("status")
    }

async def generate():
    async with httpx.AsyncClient() as client:
        print("=== GENERATING CHEAT SHEET ===")
        
        # 1. ALLOW (Standard Role, normal pacing)
        print("\n--- ALLOW Mode ---")
        res1 = await send_query(client, "demo-allow", "Standard", "Who is Vince Kaminski?")
        print(f"Q1: {res1['query']} -> Mode: {res1['mode']} | Risk: {res1['risk']:.3f} | Inst: {res1['inst_risk']:.3f}")
        
        # 2. MASK (Standard Role, rapid complex queries)
        print("\n--- MASK Mode ---")
        res2_1 = await send_query(client, "demo-mask", "Standard", "Who did Vince Kaminski communicate with?")
        print(f"Q1: {res2_1['query']} -> Mode: {res2_1['mode']} | Risk: {res2_1['risk']:.3f} | Inst: {res2_1['inst_risk']:.3f}")
        res2_2 = await send_query(client, "demo-mask", "Standard", "What topics did Vince Kaminski discuss?", 0)
        print(f"Q2: {res2_2['query']} -> Mode: {res2_2['mode']} | Risk: {res2_2['risk']:.3f} | Inst: {res2_2['inst_risk']:.3f}")
        res2_3 = await send_query(client, "demo-mask", "Standard", "Who are all the employees?", 0)
        print(f"Q3: {res2_3['query']} -> Mode: {res2_3['mode']} | Risk: {res2_3['risk']:.3f} | Inst: {res2_3['inst_risk']:.3f}")
        res2_4 = await send_query(client, "demo-mask", "Standard", "Tell me about pandas and dataframe.", 0)
        print(f"Q4: {res2_4['query']} -> Mode: {res2_4['mode']} | Risk: {res2_4['risk']:.3f} | Inst: {res2_4['inst_risk']:.3f}")

        # 3. RESTRICT (Auditor Role, moderate risk)
        print("\n--- RESTRICT Mode ---")
        res3_1 = await send_query(client, "demo-restrict", "Auditor", "What emails did Vince Kaminski send?")
        print(f"Q1: {res3_1['query']} -> Mode: {res3_1['mode']} | Risk: {res3_1['risk']:.3f} | Inst: {res3_1['inst_risk']:.3f}")
        res3_2 = await send_query(client, "demo-restrict", "Auditor", "Who did Vince Kaminski communicate with?", 0)
        print(f"Q2: {res3_2['query']} -> Mode: {res3_2['mode']} | Risk: {res3_2['risk']:.3f} | Inst: {res3_2['inst_risk']:.3f} (Status: {res3_2['status']})")
        res3_3 = await send_query(client, "demo-restrict", "Auditor", "Who are all the employees?", 0)
        print(f"Q3: {res3_3['query']} -> Mode: {res3_3['mode']} | Risk: {res3_3['risk']:.3f} | Inst: {res3_3['inst_risk']:.3f} (Status: {res3_3['status']})")

        # 4. BLOCK (Any Role, extreme risk)
        print("\n--- BLOCK Mode ---")
        sid = "demo-block"
        for i, q in enumerate([
            "Who did Vince Kaminski communicate with?",
            "What emails did Vince Kaminski send?",
            "What topics did Vince Kaminski discuss?",
            "Who are all the employees?",
            "Tell me about pandas.",
            "Tell me about numpy.",
            "Who did Vince Kaminski communicate with again?",
            "What is Enron's organization structure?",
            "Tell me about Vince Kaminski.",
            "Who did Vince Kaminski communicate with?"
        ]):
            res4 = await send_query(client, sid, "Standard", q, 0)
            print(f"Q{i+1}: {q} -> Mode: {res4['mode']} | Risk: {res4['risk']:.3f} | Inst: {res4['inst_risk']:.3f} | Status: {res4['status']}")
            if res4['mode'] == 'BLOCK':
                print(">> Hit BLOCK successfully!")
                break

if __name__ == "__main__":
    asyncio.run(generate())
