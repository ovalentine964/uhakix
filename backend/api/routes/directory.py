"""UJUZIO Entity Directory API — Graph-based entity search and connections"""
from typing import Optional, List
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class Entity(BaseModel):
    id: str
    name: str
    entity_type: str  # person, company, ministry, county, director
    description: Optional[str] = None
    registered_date: Optional[str] = None
    status: str = "active"


class EntitySearchResult(BaseModel):
    entities: List[Entity]
    total: int
    page: int
    has_more: bool


class Relationship(BaseModel):
    source: str
    target: str
    relationship_type: str  # director_of, contracted_by, same_address, shared_tender
    strength: float  # 0.0 - 1.0
    sources: List[str]
    first_seen: str
    last_seen: str


@router.get("/search", response_model=EntitySearchResult)
async def search_entities(
    query: str = Query(..., min_length=2, description="Entity name to search"),
    entity_type: Optional[str] = Query(None, description="person, company, ministry, county, director"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    """Search the entity directory. SCOUT agent powers graph traversal."""
    return EntitySearchResult(entities=[], total=0, page=page, has_more=False)


@router.get("/{entity_id}")
async def get_entity(entity_id: str):
    """Get full entity details from Neo4j graph."""
    return {"entity_id": entity_id}


@router.get("/{entity_id}/relationships", response_model=List[Relationship])
async def get_entity_relationships(
    entity_id: str,
    relationship_type: Optional[str] = Query(None),
    min_strength: float = Query(0.0, ge=0.0, le=1.0),
):
    """
    Get all relationships for an entity.
    Returns connection paths found by SCOUT agent.
    """
    return []


@router.get("/{entity_id}/timeline")
async def get_entity_timeline(entity_id: str, year: Optional[str] = None):
    """Timeline of all known activities involving this entity."""
    return {"entity_id": entity_id, "activities": []}
