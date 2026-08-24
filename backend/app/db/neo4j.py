from neo4j import AsyncGraphDatabase, AsyncDriver
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self):
        self.driver: AsyncDriver | None = None

    async def connect(self):
        if not self.driver:
            try:
                self.driver = AsyncGraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
                )
                logger.info("Connected to Neo4j successfully.")
            except Exception as e:
                logger.error(f"Failed to connect to Neo4j: {e}")
                raise

    async def close(self):
        if self.driver:
            await self.driver.close()
            self.driver = None
            logger.info("Neo4j connection closed.")

    async def execute_read(self, query: str, parameters: dict = None):
        """Execute a read transaction"""
        if not self.driver:
            await self.connect()
        
        async with self.driver.session(database=settings.NEO4J_DATABASE) as session:
            try:
                result = await session.run(query, parameters or {})
                records = await result.data()
                return records
            except Exception as e:
                logger.error(f"Error executing read query: {e}")
                raise

    async def check_health(self) -> bool:
        """Verify the database connection"""
        try:
            result = await self.execute_read("RETURN 1 AS num")
            return len(result) > 0 and result[0]["num"] == 1
        except Exception:
            return False

# Global instance
neo4j_client = Neo4jClient()
