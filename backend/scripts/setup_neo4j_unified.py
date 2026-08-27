import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "aegisgraph")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "aegisgraph")

CONSTRAINTS = [
    "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE",
    "CREATE CONSTRAINT session_id_unique IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE",
    "CREATE CONSTRAINT query_id_unique IF NOT EXISTS FOR (q:QueryEvent) REQUIRE q.query_id IS UNIQUE",
    "CREATE CONSTRAINT person_email_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.email IS UNIQUE",
    "CREATE CONSTRAINT email_id_unique IF NOT EXISTS FOR (e:Email) REQUIRE e.email_id IS UNIQUE",
    "CREATE CONSTRAINT topic_name_unique IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE"
]

INDEXES = [
    "CREATE INDEX email_sent_at_idx IF NOT EXISTS FOR (e:Email) ON (e.sent_at)",
    "CREATE INDEX email_subject_idx IF NOT EXISTS FOR (e:Email) ON (e.subject)",
    "CREATE INDEX person_name_idx IF NOT EXISTS FOR (p:Person) ON (p.name)"
]

def setup_db():
    print(f"Connecting to {NEO4J_URI}...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    with driver.session(database=NEO4J_DATABASE) as session:
        print("Applying Constraints...")
        for query in CONSTRAINTS:
            try:
                session.run(query)
                print(f"Success: {query}")
            except Exception as e:
                print(f"Failed: {query}\nReason: {e}")
                
        print("\nApplying Indexes...")
        for query in INDEXES:
            try:
                session.run(query)
                print(f"Success: {query}")
            except Exception as e:
                print(f"Failed: {query}\nReason: {e}")

    driver.close()
    print("Database setup complete.")

if __name__ == "__main__":
    setup_db()
