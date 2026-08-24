"""
AegisGraph — Neo4j Graph Verification Script (READ-ONLY)
Runs 10 diagnostic Cypher queries and prints a structured report.
"""
import asyncio
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db.neo4j import Neo4jClient
from app.core.config import settings


async def run_query(client, title, query):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    try:
        result = await client.execute_read(query)
        for row in result:
            print(f"  {row}")
        return result
    except Exception as e:
        print(f"  ERROR: {e}")
        return []


async def main():
    client = Neo4jClient()
    await client.connect()

    # 1. Node counts by label
    await run_query(client, "CHECK 1: Node counts grouped by label",
        "MATCH (n) RETURN labels(n)[0] AS Label, count(n) AS Count ORDER BY Count DESC")

    # 2. Relationship counts by type
    await run_query(client, "CHECK 2: Relationship counts grouped by type",
        "MATCH ()-[r]->() RETURN type(r) AS RelType, count(r) AS Count ORDER BY Count DESC")

    # 3. Representative properties per node label
    for label in ["Employee", "Email", "Chunk", "Entity"]:
        await run_query(client, f"CHECK 3: Sample properties for :{label}",
            f"MATCH (n:{label}) RETURN properties(n) AS props LIMIT 2")

    # 4. Source→Relationship→Target patterns
    await run_query(client, "CHECK 4: Relationship patterns (source -> rel -> target)",
        "MATCH (a)-[r]->(b) RETURN DISTINCT labels(a)[0] AS SourceLabel, type(r) AS RelType, labels(b)[0] AS TargetLabel, count(*) AS Count ORDER BY Count DESC")

    # 5. Orphan nodes (no relationships at all)
    await run_query(client, "CHECK 5: Orphan nodes (nodes with zero relationships)",
        "MATCH (n) WHERE NOT (n)--() RETURN labels(n)[0] AS Label, count(n) AS OrphanCount ORDER BY OrphanCount DESC")

    # 6. Referential integrity — do relationships connect to valid nodes?
    print(f"\n{'='*70}")
    print(f"  CHECK 6: Referential integrity spot-checks")
    print(f"{'='*70}")

    await run_query(client, "  6a: SENT edges where Employee or Email is missing",
        "MATCH (e:Employee)-[:SENT]->(m) WHERE NOT m:Email RETURN count(*) AS bad_sent_targets UNION ALL MATCH (x)-[:SENT]->(m:Email) WHERE NOT x:Employee RETURN count(*) AS bad_sent_sources")

    await run_query(client, "  6b: RECEIVED_BY edges where Email or Employee is missing",
        "MATCH (m:Email)-[:RECEIVED_BY]->(x) WHERE NOT x:Employee RETURN count(*) AS bad_recv_targets LIMIT 5")

    await run_query(client, "  6c: CONTAINS edges where Email or Chunk is missing",
        "MATCH (m:Email)-[:CONTAINS]->(x) WHERE NOT x:Chunk RETURN count(*) AS bad_contains_targets LIMIT 5")

    await run_query(client, "  6d: MENTIONS edges where Chunk or Entity is missing",
        "MATCH (c:Chunk)-[:MENTIONS]->(x) WHERE NOT x:Entity RETURN count(*) AS bad_mentions_targets LIMIT 5")

    await run_query(client, "  6e: RELATED_TO edges where either side is not Entity",
        "MATCH (a)-[:RELATED_TO]->(b) WHERE NOT a:Entity OR NOT b:Entity RETURN count(*) AS bad_related LIMIT 5")

    # 7. Duplicate nodes by primary key
    print(f"\n{'='*70}")
    print(f"  CHECK 7: Duplicate nodes by primary key")
    print(f"{'='*70}")

    await run_query(client, "  7a: Duplicate employee_id",
        "MATCH (e:Employee) WITH e.employee_id AS eid, count(*) AS cnt WHERE cnt > 1 RETURN eid, cnt LIMIT 10")

    await run_query(client, "  7b: Duplicate email_id",
        "MATCH (m:Email) WITH m.email_id AS mid, count(*) AS cnt WHERE cnt > 1 RETURN mid, cnt LIMIT 10")

    await run_query(client, "  7c: Duplicate chunk_id",
        "MATCH (c:Chunk) WITH c.chunk_id AS cid, count(*) AS cnt WHERE cnt > 1 RETURN cid, cnt LIMIT 10")

    await run_query(client, "  7d: Duplicate entity_id",
        "MATCH (ent:Entity) WITH ent.entity_id AS entid, count(*) AS cnt WHERE cnt > 1 RETURN entid, cnt LIMIT 10")

    # 8. RELATED_TO ordering check — are these the first 100k rows or random?
    await run_query(client, "CHECK 8: RELATED_TO — sample entity_ids to check ordering",
        """MATCH (a:Entity)-[r:RELATED_TO]->(b:Entity)
           RETURN a.entity_id AS src, b.entity_id AS tgt, r.co_occurrence_count AS cooccur
           ORDER BY src, tgt
           LIMIT 5""")

    await run_query(client, "CHECK 8b: RELATED_TO — last few by entity_id ordering",
        """MATCH (a:Entity)-[r:RELATED_TO]->(b:Entity)
           RETURN a.entity_id AS src, b.entity_id AS tgt, r.co_occurrence_count AS cooccur
           ORDER BY src DESC, tgt DESC
           LIMIT 5""")

    # 9. Confirm schema — list all constraints and indexes
    await run_query(client, "CHECK 9: Active constraints",
        "SHOW CONSTRAINTS")

    await run_query(client, "CHECK 9b: Active indexes",
        "SHOW INDEXES YIELD name, type, labelsOrTypes, properties WHERE type <> 'LOOKUP' RETURN name, type, labelsOrTypes, properties")

    # 10. Data-quality spot-checks
    await run_query(client, "CHECK 10a: Emails with empty/null subjects",
        "MATCH (m:Email) WHERE m.subject IS NULL OR m.subject = '' RETURN count(m) AS empty_subjects")

    await run_query(client, "CHECK 10b: Chunks with empty/null text",
        "MATCH (c:Chunk) WHERE c.text IS NULL OR c.text = '' RETURN count(c) AS empty_chunks")

    await run_query(client, "CHECK 10c: Employees with empty email addresses",
        "MATCH (e:Employee) WHERE e.email IS NULL OR e.email = '' RETURN count(e) AS empty_email_employees")

    await run_query(client, "CHECK 10d: Entities with empty names",
        "MATCH (ent:Entity) WHERE ent.name IS NULL OR ent.name = '' RETURN count(ent) AS empty_name_entities")

    await run_query(client, "CHECK 10e: Entity type distribution",
        "MATCH (ent:Entity) RETURN ent.entity_type AS EntityType, count(ent) AS Count ORDER BY Count DESC")

    await run_query(client, "CHECK 10f: Employee domain distribution (top 10)",
        "MATCH (e:Employee) RETURN e.domain AS Domain, count(e) AS Count ORDER BY Count DESC LIMIT 10")

    await run_query(client, "CHECK 10g: Timestamp range of emails",
        "MATCH (m:Email) RETURN min(m.timestamp) AS Earliest, max(m.timestamp) AS Latest")

    await client.close()
    print(f"\n{'='*70}")
    print("  VERIFICATION COMPLETE")
    print(f"{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())
