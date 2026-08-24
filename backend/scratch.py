import asyncio
from app.rag.service import graph_rag_service
from app.db.neo4j import neo4j_client

async def main():
    await neo4j_client.connect()
    r = await graph_rag_service.generate_answer('What emails did Christopher Calger send?')
    print(r)
    await neo4j_client.close()

asyncio.run(main())
