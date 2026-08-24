"""
AegisGraph Phase 4A — Behavioral Security Tests
"""
import asyncio
import sys
import os
import time
from unittest.mock import AsyncMock, patch

# Ensure backend is importable
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.security.signals import signals_calculator
from app.security.models import QueryRecord, SignalValues
from app.security.risk import risk_engine
from app.security.session import session_store
from app.rag.service import graph_rag_service
from app.db.neo4j import neo4j_client
from app.core.config import settings

PASS = 0
FAIL = 0

def report(name: str, passed: bool, detail: str = ""):
    global PASS, FAIL
    status = "PASS" if passed else "FAIL"
    if passed:
        PASS += 1
    else:
        FAIL += 1
    detail_str = f" -- {detail}" if detail else ""
    print(f"  [{status}] {name}{detail_str}")

def _test_semantic_drift():
    print("\n--- Test: Semantic Drift ---")
    
    # Identical
    d1 = signals_calculator.calculate_semantic_drift([1.0, 0.0], [1.0, 0.0])
    report("Identical queries have 0 drift", d1 == 0.0, f"Got: {d1}")
    
    # Orthogonal
    d2 = signals_calculator.calculate_semantic_drift([1.0, 0.0], [0.0, 1.0])
    report("Orthogonal queries have 1.0 drift", abs(d2 - 1.0) < 0.01, f"Got: {d2}")
    
    # Opposite
    d3 = signals_calculator.calculate_semantic_drift([1.0, 0.0], [-1.0, 0.0])
    report("Opposite queries have 1.0 drift", abs(d3 - 1.0) < 0.01, f"Got: {d3}")
    
    # Missing embedding
    d4 = signals_calculator.calculate_semantic_drift([], [1.0, 0.0])
    report("Missing embedding yields 0.0 drift", d4 == 0.0)

def _test_temporal_frequency():
    print("\n--- Test: Temporal Frequency ---")
    import math
    
    # A. First query
    tf_first = signals_calculator.calculate_temporal_frequency([], 100.0)
    report("First query gives 0.0", tf_first == 0.0)
    
    # B. Two queries 0 seconds apart
    hist_b = [QueryRecord(timestamp=100.0, query="")]
    tf_0 = signals_calculator.calculate_temporal_frequency(hist_b, 100.0)
    report("0 seconds apart gives 1.0", tf_0 == 1.0)
    
    # C. 1 second apart
    hist_c = [QueryRecord(timestamp=100.0, query="")]
    tf_1 = signals_calculator.calculate_temporal_frequency(hist_c, 101.0)
    expected_1 = math.exp(-0.1 * 1.0)
    report(f"1 second apart gives {expected_1:.3f}", abs(tf_1 - expected_1) < 0.01)
    
    # D. 5 seconds apart
    hist_d = [QueryRecord(timestamp=100.0, query="")]
    tf_5 = signals_calculator.calculate_temporal_frequency(hist_d, 105.0)
    expected_5 = math.exp(-0.1 * 5.0)
    report(f"5 seconds apart gives {expected_5:.3f}", abs(tf_5 - expected_5) < 0.01)
    
    # E. 60 seconds apart
    hist_e = [QueryRecord(timestamp=100.0, query="")]
    tf_60 = signals_calculator.calculate_temporal_frequency(hist_e, 160.0)
    expected_60 = math.exp(-0.1 * 60.0)
    report(f"60 seconds apart gives {expected_60:.3f} (very low)", abs(tf_60 - expected_60) < 0.01 and tf_60 < 0.01)
    
    # F. Query count does not affect S_temp
    hist_f_multiple = [
        QueryRecord(timestamp=80.0, query=""),
        QueryRecord(timestamp=90.0, query=""),
        QueryRecord(timestamp=100.0, query="")
    ]
    tf_f = signals_calculator.calculate_temporal_frequency(hist_f_multiple, 105.0)
    report("Query count does not affect S_temp (only latest delta matters)", abs(tf_f - tf_5) < 0.001)

def _test_entity_focus():
    print("\n--- Test: Entity Focus ---")
    
    # 0 entities
    ef1 = signals_calculator.calculate_entity_focus([])
    report("No entities gives 0.0 focus", ef1 == 0.0)
    
    # 1 entity (insufficient history)
    hist0 = [QueryRecord(timestamp=0, query="", entities=["Enron"])]
    ef1_half = signals_calculator.calculate_entity_focus(hist0)
    report("Insufficient history gives 0.0 focus", ef1_half == 0.0)
    
    # 1 entity repeated
    hist1 = [QueryRecord(timestamp=0, query="", entities=["Enron"])] * 3
    ef2 = signals_calculator.calculate_entity_focus(hist1)
    report("Repeated single entity gives 1.0 focus", ef2 == 1.0)
    
    # Diverse entities
    hist2 = [
        QueryRecord(timestamp=0, query="", entities=["E1"]),
        QueryRecord(timestamp=0, query="", entities=["E2"]),
        QueryRecord(timestamp=0, query="", entities=["E3"]),
        QueryRecord(timestamp=0, query="", entities=["E4"]),
    ]
    ef3 = signals_calculator.calculate_entity_focus(hist2)
    report("Diverse entities gives lower focus", ef3 < 0.5, f"Got: {ef3}")
    
def _test_graph_footprint():
    print("\n--- Test: Graph Footprint ---")
    
    # Zero results
    gf0 = signals_calculator.calculate_graph_footprint("entity_relationships", 0)
    report("Zero results gives 0.0 footprint", gf0 == 0.0)
    
    # Employee lookup: depth=1, nodes=1. v_max=50, d_max=5
    gf1 = signals_calculator.calculate_graph_footprint("employee_lookup", 1)
    # (1/5) + 0.5 * (1/50) = 0.2 + 0.01 = 0.21
    report("Employee lookup gives 0.21", abs(gf1 - 0.21) < 0.01)
    
    # Deep intent: entity_relationships: depth=5, nodes=50
    gf2 = signals_calculator.calculate_graph_footprint("entity_relationships", 50)
    # (5/5) + 0.5 * (50/50) = 1.5 -> clamped to 1.0
    report("Deep maxed traversal gives 1.0", gf2 == 1.0)

def _test_risk_fusion():
    print("\n--- Test: Risk Fusion & EWMA ---")
    
    s = SignalValues(semantic_drift=0.5, temporal_frequency=0.5, entity_focus=0.5, graph_footprint=0.5)
    r = risk_engine.calculate_instantaneous_risk(s)
    report("All 0.5 signals gives 0.5 risk", abs(r - 0.5) < 0.01)
    
    # EWMA
    # lam = 0.3, instantaneous = 1.0, prev = 0.0 -> 0.3 * 1 + 0.7 * 0 = 0.3
    ewma1 = risk_engine.calculate_ewma(1.0, 0.0)
    report("EWMA correctly steps to 0.3", abs(ewma1 - 0.3) < 0.01)
    
    # Next step: instant = 1.0, prev = 0.3 -> 0.3*1 + 0.7*0.3 = 0.3 + 0.21 = 0.51
    ewma2 = risk_engine.calculate_ewma(1.0, ewma1)
    report("EWMA correctly steps to 0.51", abs(ewma2 - 0.51) < 0.01)

def _test_session_isolation():
    print("\n--- Test: Session Isolation ---")
    session_store.sessions.clear()
    
    # Update sess1
    session_store.update_smoothed_risk("sess1", 0.5)
    
    # Read sess2
    state2 = session_store.get_or_create_session("sess2")
    report("Session 2 isolated from Session 1", state2.last_smoothed_risk == 0.0)

async def _test_real_embeddings():
    print("\n--- Test: Real Embedding Model (all-MiniLM-L6-v2) ---")
    
    from app.security.embeddings import embedding_provider
    from app.security.signals import signals_calculator
    
    # Force load
    if embedding_provider._model is None:
        embedding_provider._load_model()
        
    report("Model loads successfully", embedding_provider._model is not None)
    
    dim = embedding_provider._model.get_embedding_dimension()
    report(f"Embedding dimension is exactly 384 (Got: {dim})", dim == 384)
    
    # Identical queries
    q1_emb = await embedding_provider.get_embedding("Enron energy trading")
    q2_emb = await embedding_provider.get_embedding("Enron energy trading")
    
    drift_identical = signals_calculator.calculate_semantic_drift(q1_emb, q2_emb)
    report("Identical queries have near-zero drift", drift_identical < 0.001)
    
    # Similar queries
    q3_emb = await embedding_provider.get_embedding("Enron energy business")
    drift_similar = signals_calculator.calculate_semantic_drift(q1_emb, q3_emb)
    report("Similar queries have small drift", 0.0 < drift_similar < 0.2)
    
    # Different queries
    q4_emb = await embedding_provider.get_embedding("Baking a chocolate cake")
    drift_different = signals_calculator.calculate_semantic_drift(q1_emb, q4_emb)
    report("Different queries have high drift", drift_different > 0.6)
    
    # Failure handling
    # We simulate a failure by temporarily replacing the model with a broken one
    original_model = embedding_provider._model
    embedding_provider._model = None
    
    # Patch the _load_model to raise an exception
    with patch.object(embedding_provider, "_load_model", side_effect=Exception("Simulated failure")):
        failed_emb = await embedding_provider.get_embedding("Test")
        report("Embedding failure handled gracefully (returns None)", failed_emb is None)
        
        # Verify drift defaults to 0.0 on failure
        drift_failed = signals_calculator.calculate_semantic_drift(failed_emb, q1_emb)
        report("Semantic drift handles missing embeddings safely (0.0)", drift_failed == 0.0)
        
    # Restore
    embedding_provider._model = original_model

async def _test_synthetic_sequences():
    print("\n--- Test: Synthetic Attack Sequences ---")
    
    # Ensure Ollama LLM is mocked so it runs fast and doesn't hallucinate
    with patch("app.rag.service.ollama_client.generate", new_callable=AsyncMock) as mock_generate, \
         patch("app.security.service.embedding_provider.get_embedding", new_callable=AsyncMock) as mock_embed:
        
        mock_generate.return_value = "Mocked answer"
        mock_embed.return_value = [0.1, 0.2, 0.3] # Dummy embedding
        
        # Sequence A: Benign
        print("\n  [Sequence A - Benign]")
        sid = "seq_a"
        q1 = await graph_rag_service.generate_answer("Who is Christopher Calger?", sid)
        print(f"    Q1 Risk: {q1['telemetry']['smoothed_risk']:.3f} | Intent: {q1['intent']}")
        q2 = await graph_rag_service.generate_answer("What emails did Christopher Calger send?", sid)
        print(f"    Q2 Risk: {q2['telemetry']['smoothed_risk']:.3f} | Intent: {q2['intent']}")
        
        report("Benign sequence runs successfully", True)
        
        # Sequence B: Entity Focused Probing
        print("\n  [Sequence B - Entity Focused Probing]")
        sid2 = "seq_b"
        q1 = await graph_rag_service.generate_answer("Who is Christopher Calger?", sid2)
        q2 = await graph_rag_service.generate_answer("What emails did Christopher Calger send?", sid2)
        q3 = await graph_rag_service.generate_answer("Tell me about the emails sent by Christopher Calger", sid2)
        q4 = await graph_rag_service.generate_answer("Who received emails from Christopher Calger?", sid2)
        print(f"    Final Entity Focus: {q4['telemetry']['signals']['entity_focus']:.3f}")
        print(f"    Final Smoothed Risk: {q4['telemetry']['smoothed_risk']:.3f}")
        
        report("Entity focused sequence runs successfully", True)
        
        # Sequence C: Rapid Probing (High Temporal)
        print("\n  [Sequence C - Rapid Probing]")
        sid3 = "seq_c"
        # Simulate 6 queries instantly
        for i in range(6):
            q = await graph_rag_service.generate_answer("Who is Christopher Calger?", sid3)
            
        print(f"    Final Temporal Freq: {q['telemetry']['signals']['temporal_frequency']:.3f}")
        print(f"    Final Smoothed Risk: {q['telemetry']['smoothed_risk']:.3f}")
        
        report("Rapid probing hits high temporal frequency", q['telemetry']['signals']['temporal_frequency'] > 0.95)
        
        # Sequence D: Graph Expansion
        print("\n  [Sequence D - Graph Expansion]")
        sid4 = "seq_d"
        # We simulate deeper queries
        q1 = await graph_rag_service.generate_answer("Who is Christopher Calger?", sid4)
        print(f"    Depth 1 Risk: {q1['telemetry']['smoothed_risk']:.3f}")
        q2 = await graph_rag_service.generate_answer("What emails did Christopher Calger send?", sid4)
        print(f"    Depth 2 Risk: {q2['telemetry']['smoothed_risk']:.3f}")
        q3 = await graph_rag_service.generate_answer("Tell me chunks of email enron_f0be9d495030353f", sid4)
        print(f"    Depth 3 Risk: {q3['telemetry']['smoothed_risk']:.3f}")
        q4 = await graph_rag_service.generate_answer("What entities are mentioned in chunk chk_enron_f0be9d495030353f_0?", sid4)
        print(f"    Depth 4 Risk: {q4['telemetry']['smoothed_risk']:.3f}")
        q5 = await graph_rag_service.generate_answer("Tell me about entities related to Enron", sid4)
        print(f"    Depth 5 Intent: {q5['intent']}")
        print(f"    Depth 5 Graph Footprint: {q5['telemetry']['signals']['graph_footprint']:.3f}")
        print(f"    Final Smoothed Risk: {q5['telemetry']['smoothed_risk']:.3f}")
        
        report("Graph expansion reaches high graph footprint before 0 results", q4['telemetry']['signals']['graph_footprint'] > 0.5)
        report("Zero results gives 0 graph footprint", q5['telemetry']['signals']['graph_footprint'] == 0.0)

async def main():
    print("=" * 70)
    print("  AEGISGRAPH PHASE 4A — SECURITY TESTS")
    print("=" * 70)

    _test_semantic_drift()
    _test_temporal_frequency()
    _test_entity_focus()
    _test_graph_footprint()
    _test_risk_fusion()
    _test_session_isolation()
    
    await _test_real_embeddings()
    
    await neo4j_client.connect()
    await _test_synthetic_sequences()
    await neo4j_client.close()

    total = PASS + FAIL
    print(f"\n{'=' * 70}")
    print(f"  RESULTS: {PASS}/{total} passed, {FAIL} failed")
    print(f"{'=' * 70}")

    if FAIL > 0:
        sys.exit(1)



import unittest
class TestSuite(unittest.IsolatedAsyncioTestCase):
    async def test_all(self):
        try:
            await main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)

if __name__ == "__main__":
    asyncio.run(main())
