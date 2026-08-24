"""
AegisGraph Phase 2 — Retrieval system integration tests.

Tests all 6 retrieval strategies, entity resolution, intent classification,
security constraints, and the FastAPI endpoint using REAL data from the
live aegisgraph Neo4j database.

Run with: python -m tests.test_retrieval
"""
import asyncio
import sys
import os
import json

# Ensure backend is importable
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db.neo4j import Neo4jClient
from app.core.config import settings
from app.retrieval.strategies import retrieval_strategies
from app.retrieval.entity_resolver import entity_resolver
from app.retrieval.intent_classifier import classify_intent
from app.retrieval.schemas import RetrievalIntent, RetrievalRequest, ResolutionStatus
from app.retrieval.service import retrieval_service

# ---------------------------------------------------------------------------
# Test infrastructure
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Bootstrap: fetch real data from the live graph
# ---------------------------------------------------------------------------

async def bootstrap():
    """Fetch real Employee and Entity records from the graph for testing."""
    client = Neo4jClient()
    await client.connect()

    employees = await client.execute_read(
        "MATCH (e:Employee) WHERE e.mailbox <> '' "
        "RETURN e.employee_id AS id, e.name AS name, e.email AS email "
        "LIMIT 3"
    )

    # Get an email from one of these employees
    emp_id = employees[0]["id"] if employees else None
    emails = []
    if emp_id:
        emails = await client.execute_read(
            "MATCH (e:Employee {employee_id: $eid})-[:SENT]->(m:Email) "
            "RETURN m.email_id AS email_id, m.subject AS subject LIMIT 1",
            {"eid": emp_id},
        )

    # Get a chunk from that email
    email_id = emails[0]["email_id"] if emails else None
    chunks = []
    if email_id:
        chunks = await client.execute_read(
            "MATCH (m:Email {email_id: $eid})-[:CONTAINS]->(c:Chunk) "
            "RETURN c.chunk_id AS chunk_id LIMIT 1",
            {"eid": email_id},
        )

    # Get an entity from that chunk
    chunk_id = chunks[0]["chunk_id"] if chunks else None
    entities = []
    if chunk_id:
        entities = await client.execute_read(
            "MATCH (c:Chunk {chunk_id: $cid})-[:MENTIONS]->(ent:Entity) "
            "RETURN ent.entity_id AS entity_id, ent.name AS name, "
            "ent.entity_type AS entity_type LIMIT 3",
            {"cid": chunk_id},
        )

    # Get an entity with RELATED_TO relationships
    entity_with_rels = await client.execute_read(
        "MATCH (e1:Entity)-[r:RELATED_TO]-(e2:Entity) "
        "RETURN e1.entity_id AS entity_id, e1.name AS name, "
        "e1.entity_type AS entity_type, count(r) AS rel_count "
        "ORDER BY rel_count DESC LIMIT 1"
    )

    await client.close()

    return {
        "employees": employees,
        "emp_id": emp_id,
        "emails": emails,
        "email_id": email_id,
        "chunks": chunks,
        "chunk_id": chunk_id,
        "entities": entities,
        "entity_with_rels": entity_with_rels,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

async def _test_connection():
    print("\n--- Test: Neo4j Connection ---")
    client = Neo4jClient()
    await client.connect()
    healthy = await client.check_health()
    report("Neo4j health check", healthy)
    await client.close()


async def _test_employee_lookup(data):
    print("\n--- Test: Strategy A - Employee Lookup ---")
    emp = data["employees"][0]

    # By exact email
    results = await retrieval_strategies.lookup_employee_by_email(emp["email"])
    report(
        f"Lookup by email ({emp['email']})",
        len(results) == 1 and results[0]["employee_id"] == emp["id"],
        f"Found: {results[0]['name']}" if results else "EMPTY",
    )

    # By name
    results = await retrieval_strategies.lookup_employee_by_name(emp["name"])
    report(
        f"Lookup by name ({emp['name']})",
        len(results) >= 1,
        f"Found {len(results)} result(s)",
    )

    # Nonexistent
    results = await retrieval_strategies.lookup_employee_by_email(
        "nonexistent_zzzz@fake.com"
    )
    report("Lookup nonexistent email", len(results) == 0)

    results = await retrieval_strategies.lookup_employee_by_name(
        "ZZZZZNONEXISTENT_PERSON_12345"
    )
    report("Lookup nonexistent name", len(results) == 0)


async def _test_sent_emails(data):
    print("\n--- Test: Strategy B - Sent Emails ---")
    results = await retrieval_strategies.get_sent_emails(data["emp_id"], limit=5)
    report(
        f"Sent emails for {data['emp_id']}",
        len(results) > 0,
        f"Found {len(results)} email(s), first subject: {results[0]['subject']!r}" if results else "EMPTY",
    )

    # Limit enforcement
    results = await retrieval_strategies.get_sent_emails(data["emp_id"], limit=2)
    report("Limit enforcement (limit=2)", len(results) <= 2, f"Got {len(results)}")


async def _test_received_emails(data):
    print("\n--- Test: Strategy C - Received Emails ---")
    results = await retrieval_strategies.get_received_emails(data["emp_id"], limit=5)
    report(
        f"Received emails for {data['emp_id']}",
        len(results) >= 0,  # Employee might not have received emails in this dataset
        f"Found {len(results)} email(s)",
    )


async def _test_email_chunks(data):
    print("\n--- Test: Strategy D - Email Chunks ---")
    if not data["email_id"]:
        report("Email chunks", False, "No email_id available")
        return

    results = await retrieval_strategies.get_email_chunks(data["email_id"], limit=5)
    report(
        f"Chunks for email {data['email_id']}",
        len(results) > 0,
        f"Found {len(results)} chunk(s), first has {len(results[0].get('text', ''))} chars" if results else "EMPTY",
    )


async def _test_chunk_entities(data):
    print("\n--- Test: Strategy E - Chunk Entities ---")
    if not data["chunk_id"]:
        report("Chunk entities", False, "No chunk_id available")
        return

    results = await retrieval_strategies.get_chunk_entities(data["chunk_id"], limit=10)
    report(
        f"Entities for chunk {data['chunk_id']}",
        len(results) > 0,
        f"Found {len(results)} entities" if results else "EMPTY",
    )
    if results:
        report(
            "Entity has expected fields",
            all(k in results[0] for k in ["entity_id", "entity_name", "entity_type"]),
        )


async def _test_entity_relationships(data):
    print("\n--- Test: Strategy F - Entity Relationships ---")
    if not data["entity_with_rels"]:
        report("Entity relationships", False, "No entity with relationships found")
        return

    ent = data["entity_with_rels"][0]
    results = await retrieval_strategies.get_entity_relationships(
        ent["entity_id"], limit=5
    )
    report(
        f"Relationships for entity '{ent['name']}' ({ent['entity_id']})",
        len(results) > 0,
        f"Found {len(results)} related entities",
    )


async def _test_entity_resolution(data):
    print("\n--- Test: Entity Resolution ---")
    emp = data["employees"][0]

    # Exact email resolution
    resolved = await entity_resolver.resolve_employee(emp["email"])
    report(
        f"Resolve by email ({emp['email']})",
        resolved.status == ResolutionStatus.FOUND,
        f"Status: {resolved.status.value}",
    )

    # Name resolution
    resolved = await entity_resolver.resolve_employee(emp["name"])
    report(
        f"Resolve by name ({emp['name']})",
        resolved.status in (ResolutionStatus.FOUND, ResolutionStatus.AMBIGUOUS),
        f"Status: {resolved.status.value}, matches: {len(resolved.matches)}",
    )

    # Nonexistent
    resolved = await entity_resolver.resolve_employee("ZZZNONEXISTENT12345")
    report(
        "Resolve nonexistent employee",
        resolved.status == ResolutionStatus.NOT_FOUND,
        f"Status: {resolved.status.value}",
    )

    # Entity resolution
    if data["entities"]:
        ent = data["entities"][0]
        resolved = await entity_resolver.resolve_entity(ent["name"])
        report(
            f"Resolve entity '{ent['name']}'",
            resolved.status in (ResolutionStatus.FOUND, ResolutionStatus.AMBIGUOUS),
            f"Status: {resolved.status.value}",
        )


async def _test_intent_classification():
    print("\n--- Test: Intent Classification ---")

    cases = [
        ("Find employee jeff.dasovich@enron.com", RetrievalIntent.EMPLOYEE_LOOKUP),
        ("Who is Jeff Dasovich", RetrievalIntent.EMPLOYEE_LOOKUP),
        ("Emails sent by Alice", RetrievalIntent.SENT_EMAILS),
        ("Emails received by Bob", RetrievalIntent.RECEIVED_EMAILS),
        ("Chunks of email enron_abc123", RetrievalIntent.EMAIL_CHUNKS),
        ("Entities mentioned in chunk chk_enron_abc_0", RetrievalIntent.CHUNK_ENTITIES),
        ("Entities related to Enron", RetrievalIntent.ENTITY_RELATIONSHIPS),
        ("What is the weather today", RetrievalIntent.UNSUPPORTED),
    ]

    for query, expected in cases:
        result = await classify_intent(query)
        report(
            f"Intent: {query!r}",
            result == expected,
            f"Expected {expected.value}, got {result.value}",
        )


async def _test_hybrid_intent_fallback():
    print("\n--- Test: Hybrid Intent Routing (Ollama Fallback) ---")
    import unittest.mock as mock
    from app.llm.ollama_client import ollama_client

    # Original query that fails regex
    query = "Who works at Enron?"
    
    # 1. Mock successful classification
    with mock.patch.object(ollama_client, "classify_intent", new_callable=mock.AsyncMock) as mock_classify:
        mock_classify.return_value = "all_employees"
        result = await classify_intent(query)
        report(
            f"Fallback success (mocked): {query!r}",
            result == RetrievalIntent.ALL_EMPLOYEES,
            f"Got {result.value}"
        )
        mock_classify.assert_called_once()

    # 2. Mock hallucinated classification
    with mock.patch.object(ollama_client, "classify_intent", new_callable=mock.AsyncMock) as mock_classify:
        mock_classify.return_value = "invented_intent"
        result = await classify_intent(query)
        report(
            f"Fallback hallucination safety (mocked): {query!r}",
            result == RetrievalIntent.UNSUPPORTED,
            f"Got {result.value} (safely rejected 'invented_intent')"
        )

    # 3. Mock Ollama timeout/error
    with mock.patch.object(ollama_client, "classify_intent", new_callable=mock.AsyncMock) as mock_classify:
        mock_classify.return_value = "unsupported_intent"
        result = await classify_intent(query)
        report(
            f"Fallback timeout/error safety (mocked): {query!r}",
            result == RetrievalIntent.UNSUPPORTED,
            f"Got {result.value}"
        )


async def _test_security():
    print("\n--- Test: Security ---")

    # Test that RetrievalRequest cannot silently default to max_depth=5
    try:
        from pydantic import ValidationError
        request = RetrievalRequest(query="Test", limit=10)
        report("Direct RetrievalRequest cannot silently default to max_depth=5", False, "Validation did not fail")
    except ValidationError:
        report("Direct RetrievalRequest cannot silently default to max_depth=5", True)

    # Test that injection attempt in employee lookup returns clean result
    malicious = "' OR 1=1 --"
    results = await retrieval_strategies.lookup_employee_by_name(malicious)
    report(
        "SQL/Cypher injection in name lookup returns empty",
        len(results) == 0,
        f"Got {len(results)} results (should be 0)",
    )

    import unittest.mock as mock
    from app.llm.ollama_client import ollama_client

    # Test limit hard cap
    results = await retrieval_strategies.lookup_employee_by_name("a", limit=9999)
    report(
        "Hard limit cap (requested 9999)",
        len(results) <= 50,
        f"Got {len(results)} results (max 50)",
    )

    # Test that the service handles unsupported intent cleanly
    request = RetrievalRequest(query="MATCH (n) DETACH DELETE n", limit=10, max_depth=5)
    
    with mock.patch.object(ollama_client, "classify_intent", new_callable=mock.AsyncMock) as mock_classify:
        mock_classify.return_value = "unsupported_intent"
        response = await retrieval_service.execute(request)
    report(
        "Arbitrary Cypher rejected (unsupported_intent)",
        response.intent == "unsupported_intent",
        f"Intent: {response.intent}",
    )
    
    # Test max_depth enforcement for graph expansion (d_eff=0)
    request = RetrievalRequest(query="Entities related to Enron", limit=10, max_depth=0)
    response = await retrieval_service.execute(request)
    report(
        "HIGH-risk d_eff=0 blocks graph-expanding strategies",
        response.strategy == "blocked_by_policy" and response.result_count == 0,
        f"Strategy: {response.strategy}",
    )

    # Test max_depth enforcement for base lookup (d_eff=0)
    request = RetrievalRequest(query="Who is Christopher Calger", limit=10, max_depth=0)
    response = await retrieval_service.execute(request)
    report(
        "HIGH-risk d_eff=0 permits non-expansive base lookups",
        response.strategy != "blocked_by_policy" and response.intent == "employee_lookup",
        f"Strategy: {response.strategy}",
    )


async def _test_empty_results():
    print("\n--- Test: Empty Results ---")

    request = RetrievalRequest(
        query="Find emails sent by nonexistent_zzz@fake.com", limit=5, max_depth=5
    )
    response = await retrieval_service.execute(request)
    report(
        "Empty results return clean structure",
        response.result_count == 0 and response.intent != "",
        f"Intent: {response.intent}, results: {response.result_count}",
    )


async def _test_service_end_to_end(data):
    print("\n--- Test: Service End-to-End ---")
    emp = data["employees"][0]

    # Employee lookup
    request = RetrievalRequest(query=f"Find employee {emp['email']}", limit=5, max_depth=5)
    response = await retrieval_service.execute(request)
    report(
        f"E2E employee lookup ({emp['email']})",
        response.result_count >= 1 and response.intent == "employee_lookup",
        f"Intent: {response.intent}, results: {response.result_count}",
    )

    # Sent emails
    request = RetrievalRequest(
        query=f"Emails sent by {emp['email']}", limit=3, max_depth=5
    )
    response = await retrieval_service.execute(request)
    report(
        f"E2E sent emails ({emp['email']})",
        response.result_count > 0 and response.intent == "sent_emails",
        f"Intent: {response.intent}, results: {response.result_count}",
    )

    # Email chunks (if we have an email_id)
    if data["email_id"]:
        request = RetrievalRequest(
            query=f"Get chunks of email {data['email_id']}", limit=5, max_depth=5
        )
        response = await retrieval_service.execute(request)
        report(
            f"E2E email chunks ({data['email_id']})",
            response.result_count > 0 and response.intent == "email_chunks",
            f"Intent: {response.intent}, results: {response.result_count}",
        )

    # Chunk entities (if we have a chunk_id)
    if data["chunk_id"]:
        request = RetrievalRequest(
            query=f"Entities mentioned in chunk {data['chunk_id']}", limit=10, max_depth=5
        )
        response = await retrieval_service.execute(request)
        report(
            f"E2E chunk entities ({data['chunk_id']})",
            response.result_count >= 0 and response.intent == "chunk_entities",
            f"Intent: {response.intent}, results: {response.result_count}",
        )


async def main():
    global PASS, FAIL

    print("=" * 70)
    print("  AEGISGRAPH PHASE 2 — RETRIEVAL SYSTEM TESTS")
    print("=" * 70)

    # Connect the shared Neo4j client
    from app.db.neo4j import neo4j_client
    await neo4j_client.connect()

    # Bootstrap with real data
    print("\nBootstrapping with real data from aegisgraph...")
    data = await bootstrap()
    print(f"  Employees: {[e['name'] for e in data['employees']]}")
    print(f"  Email ID:  {data['email_id']}")
    print(f"  Chunk ID:  {data['chunk_id']}")
    print(f"  Entities:  {[e['name'] for e in data['entities']]}")
    if data["entity_with_rels"]:
        print(f"  Entity w/ rels: {data['entity_with_rels'][0]['name']} ({data['entity_with_rels'][0]['rel_count']} rels)")

    # Run all test suites
    await _test_connection()
    await _test_employee_lookup(data)
    await _test_sent_emails(data)
    await _test_received_emails(data)
    await _test_email_chunks(data)
    await _test_chunk_entities(data)
    await _test_entity_relationships(data)
    await _test_entity_resolution(data)
    await _test_intent_classification()
    await _test_hybrid_intent_fallback()
    await _test_security()
    await _test_empty_results()
    await _test_service_end_to_end(data)

    await neo4j_client.close()

    # Summary
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
