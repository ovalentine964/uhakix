"""
UHAKIX Graph Queries — Entity, Relationship, and Analysis Queries
All Neo4j Cypher queries for the knowledge graph.
"""

from typing import Dict, List, Any, Optional
from graph.neo4j_driver import Neo4jDriver
import structlog

logger = structlog.get_logger()


class GraphQueries:
    """Cypher query builders and executors for the UHAKIX knowledge graph."""

    def __init__(self, driver: Neo4jDriver):
        self.driver = driver

    async def initialize_schema(self):
        """Create all constraints and indexes."""
        from graph.neo4j_driver import CREATE_SCHEMA_QUERIES
        for query in CREATE_SCHEMA_QUERIES:
            try:
                await self.driver.execute_write(query)
            except Exception as e:
                logger.warning("schema_init_warning", query=query[:80], error=str(e))
        logger.info("graph_schema_initialized")

    # ── Entity Queries ─────────────────────────────────────────────

    async def create_politician(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or merge a Politician node."""
        query = """
        MERGE (p:Politician {id: $id})
        SET p.name = $name,
            p.position = $position,
            p.party = $party,
            p.constituency = $constituency,
            p.county = $county,
            p.phone = $phone,
            p.email = $email,
            p.status = $status,
            p.updated_at = datetime()
        RETURN p {.*} AS politician
        """
        result = await self.driver.execute_write(query, {
            "id": data.get("id", f"pol_{data.get('name', '').replace(' ', '_').lower()}"),
            "name": data.get("name", ""),
            "position": data.get("position", ""),
            "party": data.get("party", ""),
            "constituency": data.get("constituency", ""),
            "county": data.get("county", ""),
            "phone": data.get("phone", ""),
            "email": data.get("email", ""),
            "status": data.get("status", "active"),
        })
        return result[0]["politician"] if result else {}

    async def create_company(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or merge a Company node."""
        query = """
        MERGE (c:Company {id: $id})
        SET c.name = $name,
            c.registration_number = $reg_number,
            c.reg_date = $reg_date,
            c.status = $status,
            c.address = $address,
            c.county = $county,
            c.updated_at = datetime()
        RETURN c {.*} AS company
        """
        result = await self.driver.execute_write(query, {
            "id": data.get("id", f"co_{data.get('name', '').replace(' ', '_').lower()}"),
            "name": data.get("name", ""),
            "reg_number": data.get("registration_number", ""),
            "reg_date": data.get("registration_date", ""),
            "status": data.get("status", "active"),
            "address": data.get("address", ""),
            "county": data.get("county", ""),
        })
        return result[0]["company"] if result else {}

    async def create_tender(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or merge a Tender node."""
        query = """
        MERGE (t:Tender {id: $id})
        SET t.title = $title,
            t.ministry = $ministry,
            t.estimated_cost_kes = $estimated_cost,
            t.awarded_amount_kes = $awarded_amount,
            t.status = $status,
            t.published_date = $published_date,
            t.closing_date = $closing_date,
            t.source = $source,
            t.updated_at = datetime()
        RETURN t {.*} AS tender
        """
        result = await self.driver.execute_write(query, {
            "id": data.get("id", f"tender_{data.get('title', '').replace(' ', '_').lower()[:50]}"),
            "title": data.get("title", ""),
            "ministry": data.get("ministry", data.get("entity", "")),
            "estimated_cost": data.get("estimated_cost_kes", 0),
            "awarded_amount": data.get("awarded_amount_kes", 0),
            "status": data.get("status", "unknown"),
            "published_date": data.get("published_date", ""),
            "closing_date": data.get("closing_date", ""),
            "source": data.get("source", ""),
        })
        return result[0]["tender"] if result else {}

    async def create_transaction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or merge a Transaction node."""
        query = """
        MERGE (t:Transaction {id: $id})
        SET t.amount_kes = $amount,
            t.date = $date,
            t.ministry = $ministry,
            t.purpose = $purpose,
            t.vendor = $vendor,
            t.ifmis_code = $ifmis_code,
            t.source = $source,
            t.updated_at = datetime()
        RETURN t {.*} AS transaction
        """
        result = await self.driver.execute_write(query, {
            "id": data.get("id", f"txn_{data.get('ifmis_code', '') or data.get('title', '')}"),
            "amount": data.get("amount_kes", 0),
            "date": data.get("date", ""),
            "ministry": data.get("ministry", ""),
            "purpose": data.get("purpose", ""),
            "vendor": data.get("vendor", ""),
            "ifmis_code": data.get("ifmis_code", ""),
            "source": data.get("source", ""),
        })
        return result[0]["transaction"] if result else {}

    async def create_county(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or merge a County node."""
        query = """
        MERGE (c:County {id: $id})
        SET c.name = $name,
            c.code = coalesce(c.code, $code),
            c.governor = $governor,
            c.updated_at = datetime()
        RETURN c {.*} AS county
        """
        result = await self.driver.execute_write(query, {
            "id": data.get("id", f"county_{data.get('name', 'unknown').lower()}"),
            "name": data.get("name", ""),
            "code": data.get("code", ""),
            "governor": data.get("governor", ""),
        })
        return result[0]["county"] if result else {}

    # ── Relationship Queries ───────────────────────────────────────

    async def create_relationship(
        self,
        source_id: str,
        source_type: str,
        target_id: str,
        target_type: str,
        rel_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a relationship between two nodes."""
        query = f"""
        MATCH (a:{source_type} {{id: $source_id}})
        MATCH (b:{target_type} {{id: $target_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r.created_at = datetime(),
            r.sources = coalesce(r.sources, []) + $sources,
            r.strength = coalesce(r.strength, 0) + 1
        RETURN type(r) AS relationship, count(a) AS edges
        """
        props = properties or {}
        result = await self.driver.execute_write(query, {
            "source_id": source_id,
            "target_id": target_id,
            "sources": [props.get("source", "system")],
        })
        return result[0] if result else {}

    async def link_tender_to_contractor(self, tender_id: str, company_id: str, amount: float, source: str):
        """Link a tender to its awarded contractor."""
        return await self.create_relationship(
            source_id=tender_id,
            source_type="Tender",
            target_id=company_id,
            target_type="Company",
            rel_type="AWARDED_TO",
            properties={"amount": amount, "source": source},
        )

    async def link_tender_to_ministry(self, tender_id: str, ministry_id: str, source: str):
        """Link a tender to its procuring ministry."""
        return await self.create_relationship(
            source_id=tender_id,
            source_type="Tender",
            target_id=ministry_id,
            target_type="Politician",
            rel_type="PROCURED_BY",
            properties={"source": source},
        )

    async def link_director_to_company(self, person_id: str, company_id: str, source: str):
        """Link a person as a director of a company."""
        return await self.create_relationship(
            source_id=person_id,
            source_type="Politician",
            target_id=company_id,
            target_type="Company",
            rel_type="DIRECTOR_OF",
            properties={"source": source},
        )

    # ── Search Queries ─────────────────────────────────────────────

    async def search_entities(
        self,
        query: str,
        entity_type: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search entities by name across all node types."""
        search_query = "CALL db.index.fulltext.queryNodes('entityName', $query) YIELD node, score"

        params: Dict[str, Any] = {"query": query, "limit": limit}
        type_filter = ""
        if entity_type:
            type_filter = f"AND label(node) = '{entity_type}'"

        full_query = f"""
        {search_query}
        WHERE score > 0.1 {type_filter}
        RETURN node {{.*, `type`: label(node)}} AS entity, score
        ORDER BY score DESC
        LIMIT $limit
        """
        return await self.driver.execute_read(full_query, params)

    async def get_entity_by_id(self, entity_id: str, entity_type: str) -> Optional[Dict[str, Any]]:
        """Get a specific entity by ID."""
        query = f"""
        MATCH (n:{entity_type} {{id: $entity_id}})
        RETURN n {{.*}} AS entity
        """
        result = await self.driver.execute_read(query, {"entity_id": entity_id})
        return result[0]["entity"] if result else None

    async def get_entity_connections(
        self,
        entity_id: str,
        entity_type: str,
        depth: int = 2,
    ) -> Dict[str, Any]:
        """
        Get all connections for an entity, traversing up to `depth` hops.
        Returns the entity, its connections, and relationship paths.
        """
        query = f"""
        MATCH (n:{entity_type} {{id: $entity_id}})
        OPTIONAL MATCH path = (n)-[r*1..{depth}]-(connected)
        WHERE connected.id IS NOT NULL
        RETURN 
            n {{.*, `type`: label(n)}} AS entity,
            collect(DISTINCT connected {{.*, `type`: label(connected)}}) AS connections,
            [rel in relationships(path) | 
                {{type: type(rel), 
                 source: startNode(rel).id, 
                 target: endNode(rel).id,
                 strength: rel.strength}}
            ] AS relationship_paths
        """
        result = await self.driver.execute_read(query, {"entity_id": entity_id})
        if result:
            row = result[0]
            return {
                "entity": row["entity"],
                "connections": row["connections"],
                "relationships": row["relationship_paths"],
            }
        return {"entity": None, "connections": [], "relationships": []}

    async def find_path_between(
        self,
        source_id: str,
        source_type: str,
        target_id: str,
        target_type: str,
        max_depth: int = 4,
    ) -> List[Dict[str, Any]]:
        """Find shortest path between two entities."""
        query = f"""
        MATCH (a:{source_type} {{id: $source_id}}), (b:{target_type} {{id: $target_id}})
        MATCH path = shortestPath((a)-[*..{max_depth}]-(b))
        RETURN path
        """
        result = await self.driver.execute_read(query, {
            "source_id": source_id,
            "target_id": target_id,
        })
        return result

    async def get_tender_history_for_company(self, company_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all tenders awarded to a specific company."""
        query = """
        MATCH (c:Company {id: $company_id})<-[:AWARDED_TO]-(t:Tender)
        RETURN t {.*} AS tender
        ORDER BY t.published_date DESC
        LIMIT $limit
        """
        result = await self.driver.execute_read(query, {"company_id": company_id, "limit": limit})
        return [r["tender"] for r in result]

    async def get_spending_by_county(
        self,
        county_id: str,
        year: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get total spending for a county."""
        query = """
        MATCH (c:County {id: $county_id})<-[:IN_COUNTY]-(t:Transaction)
        WHERE t.date CONTAINS $year OR $year IS NULL
        RETURN 
            c.name AS county,
            count(t) AS transaction_count,
            sum(t.amount_kes) AS total_spent,
            avg(t.amount_kes) AS avg_amount
        """
        result = await self.driver.execute_read(query, {"county_id": county_id, "year": year})
        return [r for r in result]

    async def get_top_contractors(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Find companies with the most government money."""
        query = f"""
        MATCH (c:Company)<-[r:AWARDED_TO]-(t:Tender)
        RETURN 
            c.name AS company,
            c.registration_number AS reg_number,
            count(t) AS tender_count,
            COALESCE(sum(t.awarded_amount_kes), 0) AS total_value,
            COALESCE(min(t.awarded_amount_kes), 0) AS smallest_tender,
            COALESCE(max(t.awarded_amount_kes), 0) AS largest_tender,
            collect(DISTINCT t.ministry) AS ministries
        ORDER BY total_value DESC
        LIMIT $limit
        """
        result = await self.driver.execute_read(query, {"limit": limit})
        return [r for r in result]
