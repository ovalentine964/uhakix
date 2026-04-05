"""
UHAKIX Neo4j Driver — Connection Pool and Query Executor
Production-grade async Neo4j integration with connection pooling,
automatic retries, and typed query results.
"""

from typing import Any, Dict, List, Optional, Tuple
from contextlib import asynccontextmanager
import neo4j
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import ServiceUnavailable, TransientError, Neo4jError
from core.config import settings
import structlog

logger = structlog.get_logger()


class Neo4jDriver:
    """
    Async Neo4j driver with connection pooling.
    
    Manages:
    - Connection lifecycle (connect/close)
    - Session management with context managers
    - Query execution with retries
    - Graph schema enforcement
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: str = "neo4j",
        max_pool_size: int = 50,
        max_retry_time: int = 30,
    ):
        self.uri = uri or settings.neo4j_uri
        self.user = user or settings.neo4j_user
        self.password = password or settings.neo4j_password
        self.database = database
        self.max_pool_size = max_pool_size
        self.max_retry_time = max_retry_time

        self._driver: Optional[AsyncDriver] = None
        self._connected = False

    async def connect(self) -> None:
        """Initialize Neo4j driver and verify connection."""
        try:
            self._driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_pool_size=self.max_pool_size,
                max_transaction_retry_time=self.max_retry_time,
                encrypted=False,  # Set to True for production with SSL certs
            )
            await self._driver.verify_connectivity()
            self._connected = True
            logger.info("neo4j_connected", uri=self.uri)
        except Exception as e:
            logger.error("neo4j_connection_failed", error=str(e), uri=self.uri)
            self._connected = False
            raise

    async def close(self) -> None:
        """Close the Neo4j driver."""
        if self._driver:
            await self._driver.close()
            self._connected = False
            logger.info("neo4j_disconnected")

    @property
    def is_connected(self) -> bool:
        return self._connected and self._driver is not None

    @asynccontextmanager
    async def session(self, database: Optional[str] = None):
        """Get an async session with automatic cleanup."""
        if not self.is_connected:
            raise RuntimeError("Neo4j not connected. Call connect() first.")

        session = self._driver.session(
            database=database or self.database,
            default_access_mode=neo4j.WRITE_ACCESS,
        )
        try:
            yield session
        finally:
            await session.close()

    async def execute_write(self, query: str, parameters: Optional[Dict] = None) -> Any:
        """Execute a write query with retry logic."""
        parameters = parameters or {}

        async def _run_tx(tx):
            result = await tx.run(query, **parameters)
            return await result.data()

        try:
            async with self.session() as session:
                return await session.execute_write(_run_tx)
        except (ServiceUnavailable, TransientError) as e:
            logger.error("neo4j_write_failed", query=query[:100], error=str(e))
            raise

    async def execute_read(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        """Execute a read query."""
        parameters = parameters or {}

        async def _run_tx(tx):
            result = await tx.run(query, **parameters)
            return await result.data()

        try:
            async with self.session() as session:
                return await session.execute_read(_run_tx)
        except (ServiceUnavailable, TransientError) as e:
            logger.error("neo4j_read_failed", query=query[:100], error=str(e))
            raise

    async def execute_cypher(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        """Execute any Cypher query (read or write)."""
        return await self.execute_read(query, parameters)


# ── Entity Schema Definitions ──────────────────────────────────

# Cypher queries for creating the graph schema
CREATE_SCHEMA_QUERIES = [
    # Entity Node Constraints
    """
    CREATE CONSTRAINT politician_id IF NOT EXISTS
    FOR (p:Politician) REQUIRE p.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT company_id IF NOT EXISTS
    FOR (c:Company) REQUIRE c.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT tender_id IF NOT EXISTS
    FOR (t:Tender) REQUIRE t.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT county_id IF NOT EXISTS
    FOR (c:County) REQUIRE c.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT project_id IF NOT EXISTS
    FOR (p:Project) REQUIRE p.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT transaction_id IF NOT EXISTS
    FOR (t:Transaction) REQUIRE t.id IS UNIQUE
    """,

    # Node Properties Indexes (for fast lookups)
    """
    CREATE INDEX politician_name_idx IF NOT EXISTS
    FOR (p:Politician) ON (p.name, p.constituency)
    """,
    """
    CREATE INDEX company_name_idx IF NOT EXISTS
    FOR (c:Company) ON (c.name)
    """,
    """
    CREATE INDEX tender_ministry_idx IF NOT EXISTS
    FOR (t:Tender) ON (t.ministry, t.status)
    """,
    """
    CREATE INDEX county_name_idx IF NOT EXISTS
    FOR (c:County) ON (c.name)
    """,
    """
    CREATE INDEX transaction_date_idx IF NOT EXISTS
    FOR (t:Transaction) ON (t.date)
    """,
    """
    CREATE INDEX transaction_amount_idx IF NOT EXISTS
    FOR (t:Transaction) ON (t.amount_kes)
    """,
]
