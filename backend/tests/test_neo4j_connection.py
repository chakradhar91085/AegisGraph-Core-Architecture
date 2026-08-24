import asyncio
import os
import sys

# Add the project root to the sys path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.neo4j import neo4j_client

async def _test_connection():
    print("Initializing Neo4j connection test...")
    try:
        await neo4j_client.connect()
        print("Driver connected successfully.")

        print("Testing basic read (RETURN 1)...")
        result = await neo4j_client.execute_read("RETURN 1 AS connected")
        print("Connected Result:", result)

        print("Testing node count in database 'aegisgraph'...")
        count_result = await neo4j_client.execute_read("MATCH (n) RETURN count(n) AS node_count")
        print("Node Count Result:", count_result)

    except Exception as e:
        print(f"Error during Neo4j connection test: {e}")
    finally:
        await neo4j_client.close()


import unittest
class TestSuite(unittest.IsolatedAsyncioTestCase):
    async def test_all(self):
        try:
            await _test_connection()
        except SystemExit as e:
            self.assertEqual(e.code, 0)

if __name__ == "__main__":
    asyncio.run(test_connection())
