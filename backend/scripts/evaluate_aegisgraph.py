import asyncio
import sys
import os
import json
import time
from typing import Dict, Any, List
from unittest.mock import patch, AsyncMock

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.rag.service import graph_rag_service
from app.db.neo4j import neo4j_client
from app.core.config import settings
from app.security.session import session_store
from app.security.models import AdaptivePolicy, RiskLevel


class EvaluationHarness:
    def __init__(self):
        self.results = {}

    async def run_scenario(self, mode: str, scenario_name: str, queries: List[str], sleep_time: float = 0.0):
        session_id = f"sess_{mode}_{scenario_name}"

        # Ensure clean session
        if session_id in session_store.sessions:
            del session_store.sessions[session_id]

        scenario_results = []
        prev_ewma = 0.0
        for i, query in enumerate(queries):
            if sleep_time > 0 and i > 0:
                await asyncio.sleep(sleep_time)

            # Execute pipeline
            ans = await graph_rag_service.generate_answer(query, session_id)

            # Extract state
            state = session_store.get_or_create_session(session_id)
            last_rec = state.history[-1] if state.history else None

            if not last_rec:
                continue

            telemetry = ans.get("telemetry", {})
            signals = telemetry.get("signals", {})
            retrieval = ans.get("retrieval", {})

            from app.security.policy import policy_engine
            if mode == "BASELINE":
                applied_policy = AdaptivePolicy(
                    risk_score=0.0, risk_level=RiskLevel.LOW, attenuation_factor=1.0,
                    effective_context_limit=settings.MAX_RECORDS, effective_graph_depth=5
                )
            else:
                applied_policy = policy_engine.calculate_policy(prev_ewma)

            exposed_records = min(retrieval.get("result_count", 0), applied_policy.effective_context_limit)

            # Update prev_ewma for the NEXT query
            prev_ewma = telemetry.get("smoothed_risk", 0.0)

            scenario_results.append({
                "query_number": i + 1,
                "query_text": query,
                "extracted_entities": last_rec.entities,
                "retrieval_intent": ans.get("intent"),
                "S_sem": signals.get("semantic_drift", 0),
                "S_temp": signals.get("temporal_frequency", 0),
                "S_ent": signals.get("entity_focus", 0),
                "S_graph": signals.get("graph_footprint", 0),
                "instantaneous_risk": telemetry.get("instantaneous_risk", 0),
                "EWMA_risk": telemetry.get("smoothed_risk", 0),
                "risk_level": applied_policy.risk_level.value,
                "attenuation_factor": applied_policy.attenuation_factor,
                "effective_context_limit": applied_policy.effective_context_limit,
                "effective_graph_depth": applied_policy.effective_graph_depth,
                "retrieval_result_count": retrieval.get("result_count", 0),
                "records_passed_to_context_builder": exposed_records,
                "blocked_by_policy": retrieval.get("strategy") == "blocked_by_policy",
                "end_to_end_status": "blocked" if retrieval.get("strategy") == "blocked_by_policy" else "success"
            })

        return scenario_results


async def main():
    await neo4j_client.connect()

    scenarios = {
        "A_BENIGN_SINGLE_LOOKUP": ["Who is Christopher Calger?"],
        "B_BENIGN_SLOW_EXPLORATION": [
            "Who is Christopher Calger?",
            "What emails did Christopher Calger send?",
            "Find employee Mark Mcconnell"
        ],
        "C_RAPID_REPEATED_PROBING": [
            "Who is James Saunders?",
            "What emails did James Saunders send?",
            "Find employee Mark Mcconnell",
            "What emails did Mark Mcconnell send?"
        ],
        "D_ENTITY_FOCUSED_PROBING": [
            "Who is Christopher Calger?",
            "What emails did Christopher Calger send?",
            "Find employee Christopher Calger",
            "Tell me about Christopher Calger",
            "Where does Christopher Calger work?"
        ],
        "E_PROGRESSIVE_GRAPH_EXPANSION": [
            "Who is Christopher Calger?",
            "What emails did Christopher Calger send?",
            "Tell me chunks of email enron_f0be9d495030353f",
            "What entities are mentioned in chunk chk_enron_f0be9d495030353f_0?",
            "Tell me about entities related to Enron"
        ],
        "F_MIXED_MULTI_SIGNAL_SUSPICIOUS": [
            "Who is Christopher Calger?",
            "Who is Christopher Calger?",
            "What emails did Christopher Calger send?",
            "Tell me chunks of email enron_f0be9d495030353f",
            "What entities are mentioned in chunk chk_enron_f0be9d495030353f_0?",
            "Bake me a cake quickly"
        ],
        # ----------------------------------------------------------------
        # Phase 4D.1 — Extended Scenarios
        # ----------------------------------------------------------------
        "G_SUSTAINED_RAPID_ENTITY_FOCUSED": [
            # Rapidly probe the same entity repeatedly.
            # Designed to sustain high S_temp and accumulate S_ent, with
            # moderate S_sem drift, allowing EWMA to accumulate over 15 queries.
            "Who is Christopher Calger?",
            "Find employee Christopher Calger",
            "Who is Christopher Calger?",
            "What emails did Christopher Calger send?",
            "Find employee Christopher Calger",
            "Who is Christopher Calger?",
            "What emails did Christopher Calger send?",
            "Find employee Christopher Calger",
            "Who is Christopher Calger?",
            "What emails did Christopher Calger send?",
            "Who is Christopher Calger?",
            "Find employee Christopher Calger",
            "What emails did Christopher Calger send?",
            "Who is Christopher Calger?",
            "Find employee Christopher Calger",
        ],
        "H_SUSTAINED_MULTI_VECTOR_GRAPH": [
            # Combine all four signal vectors over a sustained sequence.
            # Rapid queries (S_temp), entity concentration on Christopher Calger (S_ent),
            # semantic shifts between intents (S_sem), and progressive graph expansion (S_graph).
            # Then cycle back to deep intents repeatedly to sustain high instantaneous risk.
            "Who is Christopher Calger?",
            "Who is Christopher Calger?",
            "What emails did Christopher Calger send?",
            "Tell me chunks of email enron_f0be9d495030353f",
            "What entities are mentioned in chunk chk_enron_f0be9d495030353f_0?",
            "Who is Christopher Calger?",
            "What emails did Christopher Calger send?",
            "Tell me chunks of email enron_f0be9d495030353f",
            "What entities are mentioned in chunk chk_enron_f0be9d495030353f_0?",
            "Find employee Christopher Calger",
            "What emails did Christopher Calger send?",
            "Tell me chunks of email enron_f0be9d495030353f",
            "What entities are mentioned in chunk chk_enron_f0be9d495030353f_0?",
            "Who is Christopher Calger?",
            "What emails did Christopher Calger send?",
            "Tell me chunks of email enron_f0be9d495030353f",
            "What entities are mentioned in chunk chk_enron_f0be9d495030353f_0?",
            "Find employee Christopher Calger",
            "What emails did Christopher Calger send?",
            "Tell me chunks of email enron_f0be9d495030353f",
        ],
    }

    # Sleep times: benign slow gets 5s; extended scenarios get 0s (rapid)
    sleep_times = {
        "B_BENIGN_SLOW_EXPLORATION": 5.0,
    }

    harness = EvaluationHarness()
    results_out = {"BASELINE": {}, "AEGISGRAPH": {}}

    with patch("app.rag.service.ollama_client.generate", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = "Mocked LLM Generation to speed up evaluation."

        print("=== RUNNING BASELINE MODE ===")
        baseline_policy = AdaptivePolicy(
            risk_score=0.0, risk_level=RiskLevel.LOW, attenuation_factor=1.0,
            effective_context_limit=settings.MAX_RECORDS, effective_graph_depth=5
        )
        with patch("app.security.policy.policy_engine.calculate_policy", return_value=baseline_policy):
            for name, queries in scenarios.items():
                print(f"Executing BASELINE: {name}")
                sleep_t = sleep_times.get(name, 0.0)
                results_out["BASELINE"][name] = await harness.run_scenario("BASELINE", name, queries, sleep_time=sleep_t)

        print("\n=== RUNNING AEGISGRAPH MODE ===")
        for name, queries in scenarios.items():
            print(f"Executing AEGISGRAPH: {name}")
            sleep_t = sleep_times.get(name, 0.0)
            results_out["AEGISGRAPH"][name] = await harness.run_scenario("AEGISGRAPH", name, queries, sleep_time=sleep_t)

    out_path = os.path.join(backend_dir, "scripts", "phase4d_evaluation.json")
    with open(out_path, "w") as f:
        json.dump(results_out, f, indent=2)

    print(f"\nEvaluation data saved to {out_path}")

    await neo4j_client.close()

if __name__ == "__main__":
    asyncio.run(main())
