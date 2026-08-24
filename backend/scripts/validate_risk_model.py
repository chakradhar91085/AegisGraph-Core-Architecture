import asyncio
import sys
import os
import json
import time
from unittest.mock import patch, AsyncMock

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.rag.service import graph_rag_service
from app.db.neo4j import neo4j_client
from app.core.config import settings
from app.security.session import session_store

def print_table(experiment_name, results):
    print(f"\n{'='*140}")
    print(f" EXPERIMENT: {experiment_name.upper()}")
    print(f"{'='*140}")
    print(f"{'Query':<35} | {'S_sem':<5} | {'S_temp':<6} | {'S_ent':<5} | {'S_graph':<7} | {'R_t':<5} | {'EWMA':<5} | {'RCnt':<4} | {'Intent':<20} | Entities")
    print("-" * 140)
    for res in results:
        q = res["query"][:32] + "..." if len(res["query"]) > 35 else res["query"]
        t = res["telemetry"]
        sig = t["signals"]
        ents = ", ".join(res["entities"])
        if len(ents) > 20: ents = ents[:17] + "..."
        if not ents: ents = "[]"
        print(f"{q:<35} | {sig['semantic_drift']:.3f} | {sig['temporal_frequency']:.3f} | {sig['entity_focus']:.3f} | {sig['graph_footprint']:.3f}   | {t['instantaneous_risk']:.3f} | {t['smoothed_risk']:.3f} | {res['result_count']:<4} | {res['intent']:<20} | {ents}")
    print(f"{'='*140}\n")

async def run_experiment(name: str, session_id: str, queries: list, sleep_time: float = 0.0) -> list:
    results = []
    for q in queries:
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)
        ans = await graph_rag_service.generate_answer(q, session_id)
        state = session_store.get_or_create_session(session_id)
        last_rec = state.history[-1] if state.history else None
        results.append({
            "query": q,
            "intent": ans.get("intent"),
            "result_count": ans.get("retrieval", {}).get("result_count", 0),
            "telemetry": ans.get("telemetry"),
            "entities": last_rec.entities if last_rec else []
        })
    print_table(name, results)
    return results

async def main():
    await neo4j_client.connect()
    
    all_experiments = {}

    with patch("app.rag.service.ollama_client.generate", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = "Mocked LLM Generation to speed up experiment."
        
        # A. Benign single-query behavior
        queries_a = ["Who is Christopher Calger?"]
        all_experiments["A_Benign_Single"] = await run_experiment("A_Benign_Single", "sess_A", queries_a)

        # B. Benign repeated queries about the same topic (diverse entities or concepts)
        queries_b = [
            "What emails did Christopher Calger send?",
            "What emails did James Saunders send?",
            "What emails did Mark Mcconnell send?",
            "Tell me chunks of email enron_f0be9d495030353f"
        ]
        all_experiments["B_Benign_Repeated_Topic"] = await run_experiment("B_Benign_Repeated_Topic", "sess_B", queries_b, sleep_time=1.0)

        # C. Repeated targeting of the same entity (force extraction of the same entity multiple times)
        queries_c = [
            "Who is Christopher Calger?",
            "What emails did Christopher Calger send?",
            "Find employee Christopher Calger"
        ]
        all_experiments["C_Target_Entity"] = await run_experiment("C_Target_Entity", "sess_C", queries_c)

        # D. Broad exploration across diverse entities
        queries_d = [
            "Who is Christopher Calger?",
            "Who is James Saunders?",
            "Who is Mark Mcconnell?",
            "What emails did Mark Mcconnell send?"
        ]
        all_experiments["D_Broad_Exploration"] = await run_experiment("D_Broad_Exploration", "sess_D", queries_d)

        # E. Rapid repeated queries (tau=5)
        queries_e = [
            "Who is James Saunders?",
            "What emails did James Saunders send?",
            "Find employee Mark Mcconnell",
            "What emails did Mark Mcconnell send?",
            "Who is Christopher Calger?",
            "What emails did Christopher Calger send?",
            "Tell me chunks of email enron_f0be9d495030353f"
        ]
        all_experiments["E_Rapid_Probing"] = await run_experiment("E_Rapid_Probing", "sess_E", queries_e)

        # F. Slow repeated queries (waiting > window or just slower, temporal_window is 60s, let's just do tau behavior)
        # To avoid actual 60s wait, we manually adjust timestamps in history, but since we just want to show lower temp freq, sleep 10s is too long.
        # We can simulate by altering history timestamps, but let's just let it be normally paced (1 second) and show it's different from rapid.
        queries_f = [
            "Who is Christopher Calger?",
            "What emails did Christopher Calger send?",
            "Find employee Mark Mcconnell"
        ]
        all_experiments["F_Slow_Repeated"] = await run_experiment("F_Slow_Repeated", "sess_F", queries_f, sleep_time=5.0)

        # G. Semantic topic switching
        queries_g = [
            "What emails did Christopher Calger send?",
            "Which emails were sent by Christopher Calger?",
            "How do I bake a chocolate cake from scratch?",
            "Can you give me a recipe for chocolate cake?"
        ]
        all_experiments["G_Semantic_Switch"] = await run_experiment("G_Semantic_Switch", "sess_G", queries_g)

        # H. Progressive graph expansion
        queries_h = [
            "Who is Christopher Calger?",
            "What emails did Christopher Calger send?",
            "Tell me chunks of email enron_f0be9d495030353f",
            "What entities are mentioned in chunk chk_enron_f0be9d495030353f_0?"
        ]
        all_experiments["H_Graph_Expansion"] = await run_experiment("H_Graph_Expansion", "sess_H", queries_h)

        # I. Zero-result graph queries
        queries_i = [
            "Who is Nonexistent Person?",
            "Tell me about entities related to Enron",
            "Tell me about entities related to Chocolate"
        ]
        all_experiments["I_Zero_Result"] = await run_experiment("I_Zero_Result", "sess_I", queries_i)

        # J. A mixed suspicious multi-signal sequence
        # Target same entity, go deep, switch topics rapidly.
        queries_j = [
            "Who is Christopher Calger?",
            "Who is Christopher Calger?",
            "What emails did Christopher Calger send?",
            "Tell me chunks of email enron_f0be9d495030353f",
            "What entities are mentioned in chunk chk_enron_f0be9d495030353f_0?",
            "Bake me a cake quickly"
        ]
        all_experiments["J_Suspicious_Mix"] = await run_experiment("J_Suspicious_Mix", "sess_J", queries_j)

    config_snapshot = {
        "alpha": settings.SECURITY_WEIGHT_SEMANTIC,
        "beta": settings.SECURITY_WEIGHT_TEMPORAL,
        "gamma": settings.SECURITY_WEIGHT_ENTITY,
        "delta": settings.SECURITY_WEIGHT_GRAPH,
        "lambda": settings.SECURITY_EWMA_LAMBDA,
        "tau": settings.SECURITY_TEMPORAL_THRESHOLD,
        "temporal_window": settings.SECURITY_TEMPORAL_WINDOW_SECONDS,
        "entity_history_window": settings.SECURITY_TEMPORAL_WINDOW_SECONDS,
        "graph_depth_normalization": settings.SECURITY_GRAPH_MAX_DEPTH,
        "graph_visited_node_normalization": settings.SECURITY_GRAPH_MAX_NODES
    }

    final_output = {
        "configuration": config_snapshot,
        "experiments": all_experiments
    }

    out_path = os.path.join(backend_dir, "scripts", "validation_results.json")
    with open(out_path, "w") as f:
        json.dump(final_output, f, indent=2)

    print(f"Data saved to {out_path}")
    
    await neo4j_client.close()

if __name__ == "__main__":
    asyncio.run(main())
