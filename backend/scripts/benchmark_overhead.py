import asyncio
import time
import json
import os
import sys
import statistics
import logging

# Ensure backend is importable
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.security.service import aegis_security
from app.security.session import session_store
from app.retrieval.service import retrieval_service
from app.retrieval.schemas import RetrievalRequest, RetrievalResponse
from app.db.neo4j import neo4j_client

# Suppress verbose logging
logging.getLogger("app.db.neo4j").setLevel(logging.WARNING)
logging.getLogger("app.retrieval").setLevel(logging.WARNING)

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

async def warmup_neo4j():
    try:
        await neo4j_client.execute_read("RETURN 1")
    except Exception as e:
        pass

async def benchmark_security_computation(iterations: int = 100):
    print(f"\n--- Benchmarking Security Computation ({iterations} iterations) ---")
    
    # Warmup sentence-transformers by running it once
    await aegis_security.observe_query("warmup_session", "Hello world")
    
    latencies = []
    
    # Pre-construct a mock retrieval response
    mock_response = RetrievalResponse(
        query="Who is Christopher Calger?",
        intent="employee_lookup",
        strategy="employee_lookup",
        result_count=1,
        results=[{"name": "Christopher Calger"}]
    )
    
    for i in range(iterations):
        session_id = f"bench_sec_session_{i}"
        
        # 1. First query in session
        start = time.perf_counter()
        ctx1 = await aegis_security.observe_query(session_id, "Who is Christopher Calger?")
        await aegis_security.calculate_risk(ctx1, mock_response)
        
        # 2. Second query in session (triggers all signals: drift, temporal, entity history, EWMA update)
        ctx2 = await aegis_security.observe_query(session_id, "What emails did Christopher Calger send?")
        mock_response_2 = RetrievalResponse(
            query="What emails did Christopher Calger send?",
            intent="sent_emails",
            strategy="sent_emails",
            result_count=5,
            results=[]
        )
        await aegis_security.calculate_risk(ctx2, mock_response_2)
        end = time.perf_counter()
        
        # Time for a full 2-query progression (average per query)
        latency_ms = ((end - start) / 2) * 1000
        latencies.append(latency_ms)
        
    return latencies

async def benchmark_protected_retrieval(iterations: int = 50):
    print(f"\n--- Benchmarking Protected Retrieval ({iterations} iterations) ---")
    latencies = []
    
    # We will use "Who is Christopher Calger?"
    query = "Who is Christopher Calger?"
    
    for i in range(iterations):
        session_id = f"bench_prot_session_{i}"
        
        start = time.perf_counter()
        
        # Security Pre-Retrieval
        ctx = await aegis_security.observe_query(session_id, query)
        policy = ctx["policy"]
        
        # Retrieval
        req = RetrievalRequest(query=query, limit=policy.effective_context_limit, max_depth=policy.effective_graph_depth)
        resp = await retrieval_service.execute(req)
        
        # Security Post-Retrieval
        await aegis_security.calculate_risk(ctx, resp)
        
        end = time.perf_counter()
        
        latency_ms = (end - start) * 1000
        latencies.append(latency_ms)
        
    return latencies

async def benchmark_baseline_retrieval(iterations: int = 50):
    print(f"\n--- Benchmarking Baseline Retrieval ({iterations} iterations) ---")
    latencies = []
    
    query = "Who is Christopher Calger?"
    
    for i in range(iterations):
        start = time.perf_counter()
        
        # Direct Retrieval (No security interception)
        req = RetrievalRequest(query=query, limit=20, max_depth=5)
        resp = await retrieval_service.execute(req)
        
        end = time.perf_counter()
        
        latency_ms = (end - start) * 1000
        latencies.append(latency_ms)
        
    return latencies

def calculate_stats(latencies):
    if not latencies:
        return {}
    return {
        "mean_ms": round(statistics.mean(latencies), 2),
        "median_ms": round(statistics.median(latencies), 2),
        "min_ms": round(min(latencies), 2),
        "max_ms": round(max(latencies), 2),
        "stdev_ms": round(statistics.stdev(latencies) if len(latencies) > 1 else 0.0, 2)
    }

async def main():
    print("=" * 60)
    print("  AEGISGRAPH PHASE 5C — PERFORMANCE OVERHEAD")
    print("=" * 60)
    
    # Warmup
    print("Warming up database connection and ML models...")
    await warmup_neo4j()
    
    sec_iters = 100
    ret_iters = 50
    
    sec_latencies = await benchmark_security_computation(sec_iters)
    sec_stats = calculate_stats(sec_latencies)
    print(f"Security Computation Mean: {sec_stats['mean_ms']} ms")
    
    base_latencies = await benchmark_baseline_retrieval(ret_iters)
    base_stats = calculate_stats(base_latencies)
    print(f"Baseline Retrieval Mean: {base_stats['mean_ms']} ms")
    
    prot_latencies = await benchmark_protected_retrieval(ret_iters)
    prot_stats = calculate_stats(prot_latencies)
    print(f"Protected Retrieval Mean: {prot_stats['mean_ms']} ms")
    
    overhead_ms = prot_stats["mean_ms"] - base_stats["mean_ms"]
    overhead_pct = (overhead_ms / base_stats["mean_ms"] * 100) if base_stats["mean_ms"] > 0 else 0
    
    print("\n" + "=" * 60)
    print(f"  Security Computation Only : {sec_stats['mean_ms']} ms per query")
    print(f"  Baseline Retrieval        : {base_stats['mean_ms']} ms per query")
    print(f"  Protected Retrieval       : {prot_stats['mean_ms']} ms per query")
    print(f"  Empirical Overhead        : {overhead_ms:.2f} ms ({overhead_pct:.1f}%)")
    print("=" * 60)
    
    # Close Neo4j cleanly
    await neo4j_client.close()
    
    # Save structured output
    output = {
        "metadata": {
            "title": "Phase 5C Performance Overhead Evaluation",
            "iterations": {
                "security_computation": sec_iters,
                "retrieval": ret_iters
            },
            "environment_notes": "Local development environment. Neo4j network/database variability may impact retrieval latency."
        },
        "security_computation_statistics": sec_stats,
        "baseline_retrieval_statistics": base_stats,
        "protected_retrieval_statistics": prot_stats,
        "calculated_overhead": {
            "absolute_ms": round(overhead_ms, 2),
            "percentage": round(overhead_pct, 2)
        }
    }
    
    ensure_dir("scripts")
    with open("scripts/phase5c_performance.json", "w") as f:
        json.dump(output, f, indent=2)
        
    print("Saved results to scripts/phase5c_performance.json")

if __name__ == "__main__":
    asyncio.run(main())
