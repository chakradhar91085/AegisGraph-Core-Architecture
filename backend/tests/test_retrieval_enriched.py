"""
AegisGraph Phase 10A — Enriched Retrieval system integration tests.
Run with: python -m tests.test_retrieval_enriched
"""
import asyncio
import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.retrieval.schemas import RetrievalRequest, RetrievalIntent
from app.retrieval.service import retrieval_service

async def test_frequent_communication_intent():
    print("Running test_frequent_communication_intent...")
    req = RetrievalRequest(
        query="Who does veronica.espinoza@enron.com communicate with most frequently?",
        limit=5,
        max_depth=5
    )
    resp = await retrieval_service.execute(req)
    assert resp.intent == RetrievalIntent.FREQUENT_COMMUNICATION.value
    assert resp.strategy == "frequent_communication"
    assert resp.result_count > 0
    assert "weight" in resp.results[0]
    assert "name" in resp.results[0]
    print("PASS: test_frequent_communication_intent")

async def test_topical_footprint_intent():
    print("Running test_topical_footprint_intent...")
    req = RetrievalRequest(
        query="What topics does veronica.espinoza@enron.com frequently talk about?",
        limit=5,
        max_depth=5
    )
    resp = await retrieval_service.execute(req)
    assert resp.intent == RetrievalIntent.TOPICAL_FOOTPRINT.value
    assert resp.strategy == "topical_footprint"
    assert resp.result_count > 0
    assert "entity_name" in resp.results[0]
    assert "count" in resp.results[0]
    print("PASS: test_topical_footprint_intent")

async def test_organization_info_intent():
    print("Running test_organization_info_intent...")
    req = RetrievalRequest(
        query="Which organization is veronica.espinoza@enron.com associated with?",
        limit=1,
        max_depth=5
    )
    resp = await retrieval_service.execute(req)
    assert resp.intent == RetrievalIntent.ORGANIZATION_INFO.value
    assert resp.strategy == "organization_info"
    assert resp.result_count == 1
    assert "organization_name" in resp.results[0]
    assert resp.results[0]["organization_name"] == "enron.com"
    print("PASS: test_organization_info_intent")

async def test_person_connection_intent():
    print("Running test_person_connection_intent...")
    req = RetrievalRequest(
        query="What is the connection between veronica.espinoza@enron.com and russell.diamond@enron.com",
        limit=5,
        max_depth=3
    )
    resp = await retrieval_service.execute(req)
    assert resp.intent == RetrievalIntent.PERSON_CONNECTION.value
    assert resp.strategy == "person_connection"
    assert resp.result_count > 0
    assert "path_names" in resp.results[0]
    assert "path_weights" in resp.results[0]
    print("PASS: test_person_connection_intent")

async def test_person_connection_blocked_by_depth():
    print("Running test_person_connection_blocked_by_depth...")
    # max_depth = 0 should block path traversal inside the handler
    req = RetrievalRequest(
        query="What is the connection between veronica.espinoza@enron.com and russell.diamond@enron.com",
        limit=5,
        max_depth=0
    )
    resp = await retrieval_service.execute(req)
    assert resp.intent == RetrievalIntent.PERSON_CONNECTION.value
    assert resp.strategy == "blocked_by_policy"
    assert resp.result_count == 0
    print("PASS: test_person_connection_blocked_by_depth")

async def main():
    await test_frequent_communication_intent()
    await test_topical_footprint_intent()
    await test_organization_info_intent()
    await test_person_connection_intent()
    await test_person_connection_blocked_by_depth()
    print("ALL ENRICHED RETRIEVAL TESTS PASSED.")

if __name__ == "__main__":
    asyncio.run(main())
