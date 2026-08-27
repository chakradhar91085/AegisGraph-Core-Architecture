from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "aegisgraph")

def main():
    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            with driver.session(database="aegisgraph") as session:
                print("\n--- Top Senders ---")
                top_senders = session.run("""
                    MATCH (n)-[:SENT]->(em:Email)
                    RETURN labels(n) as labels, n.name as name, n.email as email, count(DISTINCT em) as sent_emails
                    ORDER BY sent_emails DESC
                    LIMIT 15
                """)
                for r in top_senders:
                    print(f"{r['name']} ({r['email']}, {r['labels']}): {r['sent_emails']} sent")

                print("\n--- Are there any Chunks at all? ---")
                chunk_check = session.run("""
                    MATCH (c:Chunk)
                    RETURN count(c) as total_chunks
                """)
                print(f"Total Chunks: {chunk_check.single()[0]}")
                
                print("\n--- Does Christopher Calger exist? ---")
                calger = session.run("""
                    MATCH (n)
                    WHERE toLower(n.name) CONTAINS "calger" OR toLower(n.email) CONTAINS "calger"
                    RETURN labels(n) as labels, n.name, n.email
                """)
                for r in calger:
                    print(f"Found: {r['n.name']} ({r['n.email']}) - Labels: {r['labels']}")

    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    main()
