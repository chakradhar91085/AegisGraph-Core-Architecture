import asyncio
import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.security.embeddings import embedding_provider
from app.security.signals import signals_calculator

async def verify_semantic_drift():
    print("==================================================")
    print(" AEGISGRAPH PHASE 4A — SEMANTIC DRIFT VERIFICATION")
    print("==================================================")
    
    # Force initialization
    embedding_provider._load_model()
    
    model_name = embedding_provider.model_name
    dimension = embedding_provider._model.get_embedding_dimension()
    
    print(f"Embedding Model: {model_name}")
    print(f"Embedding Dimension: {dimension}\n")
    
    # Queries
    query_a = "Can you show me the energy trading strategy?"
    query_b = "Can you show me the energy trading strategy?"
    query_c = "What was the corporate strategy for trading energy?"
    query_d = "How to bake a chocolate chip cookie from scratch?"
    
    # Generate embeddings
    print("Generating embeddings...")
    emb_a = await embedding_provider.get_embedding(query_a)
    emb_b = await embedding_provider.get_embedding(query_b)
    emb_c = await embedding_provider.get_embedding(query_c)
    emb_d = await embedding_provider.get_embedding(query_d)
    
    def cosine_similarity(v1, v2):
        return sum(x * y for x, y in zip(v1, v2))
    
    print("\n--- 1. Identical Queries ---")
    print(f"Q1: {query_a}")
    print(f"Q2: {query_b}")
    sim = cosine_similarity(emb_a, emb_b)
    drift = signals_calculator.calculate_semantic_drift(emb_a, emb_b)
    print(f"Cosine Similarity: {sim:.6f}")
    print(f"Semantic Drift (S_sem): {drift:.6f}")
    
    print("\n--- 2. Semantically Similar Queries ---")
    print(f"Q1: {query_a}")
    print(f"Q2: {query_c}")
    sim_similar = cosine_similarity(emb_a, emb_c)
    drift_similar = signals_calculator.calculate_semantic_drift(emb_a, emb_c)
    print(f"Cosine Similarity: {sim_similar:.6f}")
    print(f"Semantic Drift (S_sem): {drift_similar:.6f}")
    
    print("\n--- 3. Unrelated Queries ---")
    print(f"Q1: {query_a}")
    print(f"Q2: {query_d}")
    sim_unrelated = cosine_similarity(emb_a, emb_d)
    drift_unrelated = signals_calculator.calculate_semantic_drift(emb_a, emb_d)
    print(f"Cosine Similarity: {sim_unrelated:.6f}")
    print(f"Semantic Drift (S_sem): {drift_unrelated:.6f}")
    
    print("\n==================================================")
    print(" VERIFICATION COMPLETE")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(verify_semantic_drift())
