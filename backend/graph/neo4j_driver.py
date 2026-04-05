"""
UHAKIX Neo4j Driver — Graph Database Connection
"""

from neo4j import AsyncGraphDatabase
from neo4j.asyncio import AsyncDriver
from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class Neo4jDriver:
    """Async Neo4j driver with connection pooling."""

    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[AsyncDriver] = None

    async def connect(self):
        """Initialize the Neo4j driver."""
        self.driver = AsyncGraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password),
            max_connection_lifetime=3600,
            max_connection_pool_size=50,
            connection_acquisition_timeout=30,
        )
        # Test connection
        async with self.driver.session() as session:
            result = await session.run("RETURN 1 AS test")
            record = await result.single()
            if record and record["test"] == 1:
                logger.info("neo4j_connected", uri=self.uri)

    async def close(self):
        """Close Neo4j connections."""
        if self.driver:
            await self.driver.close()
            logger.info("neo4j_disconnected")

    async def execute_query(self, query: str, parameters: Dict = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results."""
        if not self.driver:
            raise RuntimeError("Neo4j driver not connected")

        params = parameters or {}
        results = []
        async with self.driver.session() as session:
            result = await session.run(query, params)
            async for record in result:
                results.append(dict(record))
        return results

    async def execute_write(self, query: str, parameters: Dict = None) -> Dict[str, Any]:
        """Execute a write query."""
        if not self.driver:
            raise RuntimeError("Neo4j driver not connected")

        params = parameters or {}
        async with self.driver.session() as session:
            result = await session.run(query, params)
            summary = await result.consume()
            return {
                "counters": summary.counters.__dict__,
            }

    async def create_node(self, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new node."""
        props = ", ".join(f"{k}: ${k}" for k in properties.keys())
        query = f"CREATE (n:{label} {{{props}}}) RETURN n"
        return await self.execute_write(query, properties)

    async def create_relationship(
        self,
        from_label: str,
        from_id: str,
        from_key: str,
        to_label: str,
        to_id: str,
        to_key: str,
        rel_type: str,
        properties: Dict = None,
    ) -> Dict[str, Any]:
        """Create a relationship between two nodes."""
        props = ", ".join(f"{k}: ${k}" for k in (properties or {}).keys())
        rel_clause = f"[r:{rel_type} {{{props}}}]" if props else f"[r:{rel_type}]"

        query = f"""
        MATCH (a:{from_label} {{{from_key}: $from_value}})
        MATCH (b:{to_label} {{{to_key}: $to_value}})
        MERGE (a)-{rel_clause}->(b)
        RETURN a, b, r
        """

        params = {"from_value": from_id, "to_value": to_id, **(properties or {})}
        return await self.execute_write(query, params)

    async def search_nodes(self, label: str, search_term: str, limit: int = 20) -> List[Dict]:
        """Search nodes by name (full-text search)."""
        query = f"""
        MATCH (n:{label})
        WHERE n.name CONTAINS $search
        RETURN n LIMIT $limit
        """
        return await self.execute_query(query, {"search": search_term, "limit": limit})
