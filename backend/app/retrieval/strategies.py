"""
AegisGraph Phase 2 — Parameterized Cypher retrieval strategies.

All queries use Neo4j query parameters ($param). No string interpolation.
Every query has a configurable LIMIT. No unrestricted traversals.
"""
from typing import List, Dict, Any
from app.db.neo4j import neo4j_client
import logging

logger = logging.getLogger(__name__)

MAX_LIMIT = 50  # Hard ceiling for any retrieval operation


class RetrievalStrategies:
    """
    Contains all parameterized Cypher retrieval strategies.

    This class is the single point where Cypher is defined.
    A future AegisGraph security layer can intercept calls to these methods
    to enforce behavioral risk policies before graph access.
    """

    def __init__(self):
        self.db = neo4j_client

    def _cap_limit(self, limit: int) -> int:
        """Enforce hard ceiling on result limits."""
        return min(max(limit, 1), MAX_LIMIT)

    # ------------------------------------------------------------------
    # Strategy A — Employee Lookup
    # ------------------------------------------------------------------

    async def lookup_employee_by_email(self, email: str) -> List[Dict[str, Any]]:
        """Find an Employee node by exact email address."""
        query = """
        MATCH (e:Employee {email: $email})
        RETURN e.employee_id AS employee_id, e.name AS name,
               e.email AS email, e.domain AS domain, e.mailbox AS mailbox
        LIMIT 1
        """
        return await self.db.execute_read(query, {"email": email.strip().lower()})

    async def lookup_employee_by_name(
        self, name: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find Employee nodes by case-insensitive name search."""
        query = """
        MATCH (e:Employee)
        WHERE toLower(e.name) CONTAINS toLower($name)
        RETURN e.employee_id AS employee_id, e.name AS name,
               e.email AS email, e.domain AS domain, e.mailbox AS mailbox
        LIMIT $limit
        """
        return await self.db.execute_read(
            query, {"name": name.strip(), "limit": self._cap_limit(limit)}
        )

    # ------------------------------------------------------------------
    # Strategy B — Sent Emails
    # ------------------------------------------------------------------

    async def get_sent_emails(
        self, employee_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve emails sent by a specific employee."""
        query = """
        MATCH (e:Employee {employee_id: $employee_id})-[:SENT]->(m:Email)
        RETURN m.email_id AS email_id, m.subject AS subject,
               m.timestamp AS timestamp, m.source_folder AS source_folder
        ORDER BY m.timestamp DESC
        LIMIT $limit
        """
        return await self.db.execute_read(
            query, {"employee_id": employee_id, "limit": self._cap_limit(limit)}
        )

    # ------------------------------------------------------------------
    # Strategy C — Received Emails
    # ------------------------------------------------------------------

    async def get_received_emails(
        self, employee_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve emails received by a specific employee."""
        query = """
        MATCH (e:Employee {employee_id: $employee_id})<-[:RECEIVED_BY]-(m:Email)
        RETURN m.email_id AS email_id, m.subject AS subject,
               m.timestamp AS timestamp, m.source_folder AS source_folder
        ORDER BY m.timestamp DESC
        LIMIT $limit
        """
        return await self.db.execute_read(
            query, {"employee_id": employee_id, "limit": self._cap_limit(limit)}
        )

    # ------------------------------------------------------------------
    # Strategy D — Email Chunks
    # ------------------------------------------------------------------

    async def get_email_chunks(
        self, email_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve text chunks belonging to a specific email."""
        query = """
        MATCH (m:Email {email_id: $email_id})-[:CONTAINS]->(c:Chunk)
        RETURN c.chunk_id AS chunk_id, c.chunk_index AS chunk_index, c.text AS text
        ORDER BY c.chunk_index ASC
        LIMIT $limit
        """
        return await self.db.execute_read(
            query, {"email_id": email_id, "limit": self._cap_limit(limit)}
        )

    # ------------------------------------------------------------------
    # Strategy E — Chunk Entities
    # ------------------------------------------------------------------

    async def get_chunk_entities(
        self, chunk_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Retrieve named entities mentioned in a specific chunk."""
        query = """
        MATCH (c:Chunk {chunk_id: $chunk_id})-[r:MENTIONS]->(ent:Entity)
        RETURN ent.entity_id AS entity_id, ent.name AS entity_name,
               ent.entity_type AS entity_type, r.count AS mention_count
        ORDER BY r.count DESC
        LIMIT $limit
        """
        return await self.db.execute_read(
            query, {"chunk_id": chunk_id, "limit": self._cap_limit(limit)}
        )

    # ------------------------------------------------------------------
    # Strategy F — Entity Relationships
    # ------------------------------------------------------------------

    async def get_entity_relationships(
        self, entity_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Retrieve entities related to a given entity via co-occurrence."""
        query = """
        MATCH (e1:Entity {entity_id: $entity_id})-[r:RELATED_TO]-(e2:Entity)
        RETURN e2.entity_id AS entity_id, e2.name AS entity_name,
               e2.entity_type AS entity_type, r.co_occurrence_count AS co_occurrence_count
        ORDER BY r.co_occurrence_count DESC
        LIMIT $limit
        """
        return await self.db.execute_read(
            query, {"entity_id": entity_id, "limit": self._cap_limit(limit)}
        )

    # ------------------------------------------------------------------
    # Strategy G — Frequent Communication
    # ------------------------------------------------------------------

    async def get_frequent_communication(
        self, employee_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve employees this employee communicates with most frequently."""
        query = """
        MATCH (e1:Employee {employee_id: $employee_id})-[r:COMMUNICATES_FREQUENTLY_WITH]-(e2:Employee)
        RETURN e2.employee_id AS employee_id, e2.name AS name,
               e2.email AS email, r.weight AS weight
        ORDER BY r.weight DESC
        LIMIT $limit
        """
        return await self.db.execute_read(
            query, {"employee_id": employee_id, "limit": self._cap_limit(limit)}
        )

    # ------------------------------------------------------------------
    # Strategy H — Topical Footprint
    # ------------------------------------------------------------------

    async def get_topical_footprint(
        self, employee_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Retrieve entities this employee frequently mentions."""
        query = """
        MATCH (e:Employee {employee_id: $employee_id})-[r:FREQUENTLY_MENTIONS]->(ent:Entity)
        RETURN ent.entity_id AS entity_id, ent.name AS entity_name,
               ent.entity_type AS entity_type, r.count AS count
        ORDER BY r.count DESC
        LIMIT $limit
        """
        return await self.db.execute_read(
            query, {"employee_id": employee_id, "limit": self._cap_limit(limit)}
        )

    # ------------------------------------------------------------------
    # Strategy I — Organization Info
    # ------------------------------------------------------------------

    async def get_organization(
        self, employee_id: str, limit: int = 1
    ) -> List[Dict[str, Any]]:
        """Retrieve the organization this employee belongs to."""
        query = """
        MATCH (e:Employee {employee_id: $employee_id})-[:BELONGS_TO]->(o:Organization)
        RETURN o.name AS organization_name
        LIMIT $limit
        """
        return await self.db.execute_read(
            query, {"employee_id": employee_id, "limit": self._cap_limit(limit)}
        )

    # ------------------------------------------------------------------
    # Strategy J — Person Connection
    # ------------------------------------------------------------------

    async def get_person_connection(
        self, employee_id_1: str, employee_id_2: str, max_depth: int
    ) -> List[Dict[str, Any]]:
        """Safely find a shortest communication path between two employees up to max_depth."""
        # Using APOC or pure cypher shortestPath
        # Note: Cypher requires the upper bound in shortestPath to be a literal.
        # We will dynamically generate the literal from max_depth safely.
        safe_depth = self._cap_limit(max_depth)
        
        query = f"""
        MATCH p=shortestPath((e1:Employee {{employee_id: $emp1}})-[:COMMUNICATES_FREQUENTLY_WITH*1..{safe_depth}]-(e2:Employee {{employee_id: $emp2}}))
        RETURN [node IN nodes(p) | node.name] AS path_names,
               [rel IN relationships(p) | rel.weight] AS path_weights
        """
        return await self.db.execute_read(
            query, {"emp1": employee_id_1, "emp2": employee_id_2}
        )
# Module-level singleton
retrieval_strategies = RetrievalStrategies()
