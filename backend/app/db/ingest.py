import asyncio
import csv
import os
import sys
import logging
import time

# Ensure backend directory is in sys.path if run directly
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db.neo4j import Neo4jClient
from app.core.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(backend_dir, "..", "data", "neo4j")
BATCH_SIZE = 5000  # High batch size for faster insertion over localhost

CONSTRAINTS_AND_INDEXES = [
    "CREATE CONSTRAINT unique_employee_id IF NOT EXISTS FOR (e:Employee) REQUIRE e.employee_id IS UNIQUE;",
    "CREATE CONSTRAINT unique_email_id IF NOT EXISTS FOR (m:Email) REQUIRE m.email_id IS UNIQUE;",
    "CREATE CONSTRAINT unique_chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.chunk_id IS UNIQUE;",
    "CREATE CONSTRAINT unique_entity_id IF NOT EXISTS FOR (ent:Entity) REQUIRE ent.entity_id IS UNIQUE;",
    "CREATE INDEX idx_employee_email IF NOT EXISTS FOR (e:Employee) ON (e.email);",
    "CREATE INDEX idx_employee_domain IF NOT EXISTS FOR (e:Employee) ON (e.domain);",
    "CREATE INDEX idx_email_timestamp IF NOT EXISTS FOR (m:Email) ON (m.timestamp);",
    "CREATE INDEX idx_entity_name IF NOT EXISTS FOR (ent:Entity) ON (ent.name);",
    "CREATE INDEX idx_entity_type IF NOT EXISTS FOR (ent:Entity) ON (ent.entity_type);"
]

async def execute_schema():
    logger.info("Applying schema constraints and indexes...")
    client = Neo4jClient()
    await client.connect()
    driver = client.driver
    
    async with driver.session(database=settings.NEO4J_DATABASE) as session:
        for query in CONSTRAINTS_AND_INDEXES:
            try:
                await session.run(query)
                logger.info(f"Executed: {query.split('IF NOT EXISTS ')[0]}")
            except Exception as e:
                logger.error(f"Failed to execute schema query: {e}")
                
async def ingest_csv(filename, query, limit=None):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return

    logger.info(f"Starting ingestion of {filename}...")
    client = Neo4jClient()
    await client.connect()
    driver = client.driver
    
    t0 = time.time()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        batch = []
        total = 0
        
        async with driver.session(database=settings.NEO4J_DATABASE) as session:
            for row in reader:
                batch.append(row)
                
                if len(batch) >= BATCH_SIZE:
                    await session.run(query, {"batch": batch})
                    total += len(batch)
                    batch = []
                    logger.info(f"Ingested {total} rows from {filename}...")
                    
                    if limit and total >= limit:
                        break
                        
            if batch and (not limit or total < limit):
                await session.run(query, {"batch": batch})
                total += len(batch)
                
    elapsed = time.time() - t0
    logger.info(f"Finished {filename}: Ingested {total} rows in {elapsed:.2f}s.")

QUERIES = {
    "employees": """
        UNWIND $batch AS row
        MERGE (e:Employee {employee_id: row.employee_id})
        SET e.email = row.email,
            e.name = row.name,
            e.mailbox = row.mailbox,
            e.domain = row.domain
    """,
    "emails": """
        UNWIND $batch AS row
        MERGE (m:Email {email_id: row.email_id})
        SET m.message_id = row.message_id,
            m.timestamp = datetime(row.timestamp),
            m.subject = row.subject,
            m.content_hash = row.content_hash,
            m.source_folder = row.source_folder
    """,
    "chunks": """
        UNWIND $batch AS row
        MERGE (c:Chunk {chunk_id: row.chunk_id})
        SET c.email_id = row.email_id,
            c.chunk_index = toInteger(row.chunk_index),
            c.text = row.text
    """,
    "entities": """
        UNWIND $batch AS row
        MERGE (ent:Entity {entity_id: row.entity_id})
        SET ent.name = row.name,
            ent.entity_type = row.entity_type
    """,
    "sent": """
        UNWIND $batch AS row
        MATCH (e:Employee {employee_id: row.employee_id})
        MATCH (m:Email {email_id: row.email_id})
        MERGE (e)-[:SENT]->(m)
    """,
    "received": """
        UNWIND $batch AS row
        MATCH (m:Email {email_id: row.email_id})
        MATCH (e:Employee {employee_id: row.employee_id})
        MERGE (m)-[:RECEIVED_BY {recipient_type: row.recipient_type}]->(e)
    """,
    "contains": """
        UNWIND $batch AS row
        MATCH (m:Email {email_id: row.email_id})
        MATCH (c:Chunk {chunk_id: row.chunk_id})
        MERGE (m)-[:CONTAINS]->(c)
    """,
    "mentions": """
        UNWIND $batch AS row
        MATCH (c:Chunk {chunk_id: row.chunk_id})
        MATCH (ent:Entity {entity_id: row.entity_id})
        MERGE (c)-[:MENTIONS {count: toInteger(row.count)}]->(ent)
    """,
    "related": """
        UNWIND $batch AS row
        MATCH (e1:Entity {entity_id: row.source_entity_id})
        MATCH (e2:Entity {entity_id: row.target_entity_id})
        MERGE (e1)-[:RELATED_TO {co_occurrence_count: toInteger(row.co_occurrence_count)}]->(e2)
    """
}

async def run_full_ingestion():
    await execute_schema()
    
    logger.info("=== INGESTING NODES ===")
    await ingest_csv("employees.csv", QUERIES["employees"])
    await ingest_csv("emails.csv", QUERIES["emails"])
    await ingest_csv("chunks.csv", QUERIES["chunks"])
    await ingest_csv("entities.csv", QUERIES["entities"])
    
    logger.info("=== INGESTING EDGES ===")
    await ingest_csv("sent_relationships.csv", QUERIES["sent"])
    await ingest_csv("received_relationships.csv", QUERIES["received"])
    await ingest_csv("contains_relationships.csv", QUERIES["contains"])
    await ingest_csv("mentions_relationships.csv", QUERIES["mentions"])
    
    logger.info("=== INGESTING MASSIVE EDGES (Capped for MVP) ===")
    # 7.5 million is too slow for a synchronous script over Python, cap it to 100k for development.
    await ingest_csv("entity_relationships.csv", QUERIES["related"], limit=100000)

if __name__ == "__main__":
    try:
        asyncio.run(run_full_ingestion())
        logger.info("Ingestion complete!")
    except Exception as e:
        logger.exception("Ingestion failed!")
