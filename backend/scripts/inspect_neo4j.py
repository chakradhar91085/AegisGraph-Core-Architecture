from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "aegisgraph")

def main():
    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            with driver.session(database="aegisgraph") as session:
                print("--- Node Labels ---")
                labels = session.run("CALL db.labels()")
                for r in labels:
                    print(f"- {r[0]}")
                    
                print("\n--- Relationship Types ---")
                rels = session.run("CALL db.relationshipTypes()")
                for r in rels:
                    print(f"- {r[0]}")

                print("\n--- Employee Data Richness ---")
                rich_employees = session.run("""
                    MATCH (e:Employee)
                    OPTIONAL MATCH (e)-[:SENT]->(sent:Email)
                    OPTIONAL MATCH (e)<-[:RECEIVED_BY]-(received:Email)
                    OPTIONAL MATCH (e)-[:COMMUNICATES_WITH]-(other:Employee)
                    RETURN e.name as name, e.email as email, count(DISTINCT sent) as sent_emails, count(DISTINCT received) as received_emails, count(DISTINCT other) as connections
                    ORDER BY (sent_emails + received_emails) DESC
                    LIMIT 15
                """)
                for r in rich_employees:
                    print(f"{r['name']} ({r['email']}): {r['sent_emails']} sent, {r['received_emails']} received, {r['connections']} connections")

                print("\n--- Email Data Structure ---")
                email_sample = session.run("""
                    MATCH (em:Email)
                    RETURN keys(em) as props
                    LIMIT 1
                """)
                for r in email_sample:
                    print(f"Email properties: {r['props']}")
                    
                chunk_check = session.run("""
                    MATCH (c:Chunk)
                    RETURN count(c) as total_chunks
                """)
                print(f"Total Chunks: {chunk_check.single()[0]}")
                
                print("\n--- Checking Calger's Emails ---")
                calger_emails = session.run("""
                    MATCH (e:Employee {name: "Christopher Calger"})-[:SENT]->(em:Email)
                    RETURN em.subject, em.body LIMIT 3
                """)
                for r in calger_emails:
                    print(f"Subject: {r['em.subject']}, Body present: {r.get('em.body') is not None}")

    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    main()
