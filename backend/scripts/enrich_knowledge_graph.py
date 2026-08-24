#!/usr/env/bin python3
import os
import time
from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "aegisgraph")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "aegisgraph")

def run_enrichment():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    print("========================================")
    print("AEGISGRAPH - KNOWLEDGE GRAPH ENRICHMENT")
    print("========================================")
    
    with driver.session(database=NEO4J_DATABASE) as session:
        # 1. Organization & BELONGS_TO
        print("\n1. Enriching Organizations...")
        t0 = time.time()
        org_query = """
        MATCH (e:Employee)
        WHERE e.domain IS NOT NULL AND trim(e.domain) <> ''
        WITH DISTINCT e.domain AS domain
        MERGE (o:Organization {name: domain})
        """
        session.run(org_query)
        
        belongs_query = """
        MATCH (e:Employee)
        WHERE e.domain IS NOT NULL AND trim(e.domain) <> ''
        MATCH (o:Organization {name: e.domain})
        MERGE (e)-[:BELONGS_TO]->(o)
        """
        res_org = session.run(belongs_query)
        print(f"Created Organizations and BELONGS_TO edges in {time.time() - t0:.2f}s")
        
        # 2. COMMUNICATES_FREQUENTLY_WITH
        print("\n2. Enriching Social Graph (COMMUNICATES_FREQUENTLY_WITH >= 5)...")
        t0 = time.time()
        comm_query = """
        MATCH (p1:Employee)-[:SENT]->(:Email)-[:RECEIVED_BY]->(p2:Employee)
        WHERE p1 <> p2
        WITH p1, p2, count(*) as weight
        WHERE weight >= 5
        MERGE (p1)-[r:COMMUNICATES_FREQUENTLY_WITH]->(p2)
        SET r.weight = weight
        """
        session.run(comm_query)
        print(f"Created COMMUNICATES_FREQUENTLY_WITH edges in {time.time() - t0:.2f}s")

        # 3. FREQUENTLY_MENTIONS
        print("\n3. Enriching Topical Footprint (FREQUENTLY_MENTIONS >= 10)...")
        t0 = time.time()
        mentions_query = """
        MATCH (p:Employee)-[:SENT]->(:Email)-[:CONTAINS]->(:Chunk)-[:MENTIONS]->(ent:Entity)
        WITH p, ent, sum(1) as total_mentions
        WHERE total_mentions >= 10
        MERGE (p)-[r:FREQUENTLY_MENTIONS]->(ent)
        SET r.count = total_mentions
        """
        session.run(mentions_query)
        print(f"Created FREQUENTLY_MENTIONS edges in {time.time() - t0:.2f}s")

        print("\n--- FINAL GRAPH STATISTICS ---")
        stats_query = """
        CALL db.labels() YIELD label 
        MATCH (n) WHERE label IN labels(n) 
        RETURN label, count(n) AS count 
        ORDER BY label
        """
        for record in session.run(stats_query):
            print(f"Node {record['label']}: {record['count']}")
            
        rel_stats = """
        MATCH ()-[r]->() 
        RETURN type(r) AS type, count(r) AS count 
        ORDER BY count DESC
        """
        for record in session.run(rel_stats):
            print(f"Relationship {record['type']}: {record['count']}")

    driver.close()
    print("\nEnrichment complete.")

if __name__ == "__main__":
    run_enrichment()
