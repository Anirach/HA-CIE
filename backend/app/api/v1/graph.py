"""Graph API endpoints for standards visualization."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.core.security import get_current_user_with_role
from app.services.standards_service import (
    standards_service,
    Part,
    Chapter,
    Criterion,
    CausalRelationship,
    CriterionCategory,
)

router = APIRouter(prefix="/graph", tags=["Graph"])


class GraphNode(BaseModel):
    """Node data for Cytoscape.js."""
    data: Dict[str, Any]


class GraphEdge(BaseModel):
    """Edge data for Cytoscape.js."""
    data: Dict[str, Any]


class GraphData(BaseModel):
    """Complete graph data for visualization."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class PartSummary(BaseModel):
    """Summary of a standard part."""
    number: str
    name: str
    weight: float
    color: str
    chapter_count: int


class ChapterDetail(BaseModel):
    """Detailed chapter information."""
    id: str
    number: str
    name: str
    weight: float
    focus: str
    part_number: str
    part_name: str
    color: str
    criteria: List[Criterion]
    incoming_relationships: List[CausalRelationship]
    outgoing_relationships: List[CausalRelationship]


class RelationshipDetail(BaseModel):
    """Detailed relationship information."""
    source: str
    source_name: str
    target: str
    target_name: str
    strength: float
    relationship_type: str
    mechanism: str


@router.get(
    "/standards",
    response_model=GraphData,
    summary="Get standards graph for visualization"
)
async def get_standards_graph(
    current_user: dict = Depends(get_current_user_with_role)
):
    """
    Get the complete HA Thailand Standards graph data formatted for Cytoscape.js.
    
    Returns nodes (chapters) and edges (causal relationships) with all
    necessary data for interactive visualization.
    """
    graph_data = standards_service.get_graph_data()
    
    return GraphData(
        nodes=[GraphNode(data=n["data"]) for n in graph_data["nodes"]],
        edges=[GraphEdge(data=e["data"]) for e in graph_data["edges"]]
    )


@router.get(
    "/parts",
    response_model=List[PartSummary],
    summary="Get all standard parts"
)
async def get_parts(
    current_user: dict = Depends(get_current_user_with_role)
):
    """Get summary of all standard parts."""
    parts = standards_service.get_parts()
    return [
        PartSummary(
            number=p.number,
            name=p.name,
            weight=p.weight,
            color=p.color,
            chapter_count=len(p.chapters)
        )
        for p in parts
    ]


@router.get(
    "/parts/{part_number}",
    response_model=Part,
    summary="Get a specific part with all chapters"
)
async def get_part(
    part_number: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Get detailed information about a specific part."""
    part = standards_service.get_part(part_number)
    if not part:
        raise HTTPException(status_code=404, detail=f"Part {part_number} not found")
    return part


@router.get(
    "/chapters",
    response_model=List[Chapter],
    summary="Get all chapters"
)
async def get_chapters(
    part: Optional[str] = None,
    current_user: dict = Depends(get_current_user_with_role)
):
    """
    Get all chapters, optionally filtered by part number.
    
    Args:
        part: Optional part number to filter (e.g., "I", "II", "III", "IV")
    """
    if part:
        part_obj = standards_service.get_part(part)
        if not part_obj:
            raise HTTPException(status_code=404, detail=f"Part {part} not found")
        return part_obj.chapters
    return standards_service.get_all_chapters()


@router.get(
    "/chapters/{chapter_id}",
    response_model=ChapterDetail,
    summary="Get detailed chapter information"
)
async def get_chapter_detail(
    chapter_id: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """
    Get detailed information about a specific chapter including its
    criteria and causal relationships.
    """
    chapter = standards_service.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")
    
    # Find the part this chapter belongs to
    part = None
    for p in standards_service.get_parts():
        for c in p.chapters:
            if c.id == chapter_id:
                part = p
                break
        if part:
            break
    
    # Get relationships
    relationships = standards_service.get_relationships_for_chapter(chapter_id)
    
    return ChapterDetail(
        id=chapter.id,
        number=chapter.number,
        name=chapter.name,
        weight=chapter.weight,
        focus=chapter.focus,
        part_number=part.number if part else "",
        part_name=part.name if part else "",
        color=part.color if part else "#666666",
        criteria=chapter.criteria,
        incoming_relationships=relationships["incoming"],
        outgoing_relationships=relationships["outgoing"]
    )


@router.get(
    "/relationships",
    response_model=List[CausalRelationship],
    summary="Get all causal relationships"
)
async def get_relationships(
    source: Optional[str] = None,
    target: Optional[str] = None,
    relationship_type: Optional[str] = None,
    min_strength: Optional[float] = None,
    current_user: dict = Depends(get_current_user_with_role)
):
    """
    Get causal relationships with optional filtering.
    
    Args:
        source: Filter by source chapter ID
        target: Filter by target chapter ID
        relationship_type: Filter by type (prerequisite, strong_support, etc.)
        min_strength: Minimum relationship strength (0.0 - 1.0)
    """
    relationships = standards_service.get_causal_relationships()
    
    # Apply filters
    if source:
        relationships = [r for r in relationships if r.source == source]
    if target:
        relationships = [r for r in relationships if r.target == target]
    if relationship_type:
        relationships = [r for r in relationships if r.relationship_type == relationship_type]
    if min_strength is not None:
        relationships = [r for r in relationships if r.strength >= min_strength]
    
    return relationships


@router.get(
    "/relationships/{source}/{target}",
    response_model=RelationshipDetail,
    summary="Get relationship between two chapters"
)
async def get_relationship_detail(
    source: str,
    target: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Get detailed information about a specific causal relationship."""
    relationships = standards_service.get_causal_relationships()
    
    for rel in relationships:
        if rel.source == source and rel.target == target:
            source_chapter = standards_service.get_chapter(source)
            target_chapter = standards_service.get_chapter(target)
            
            return RelationshipDetail(
                source=source,
                source_name=source_chapter.name if source_chapter else source,
                target=target,
                target_name=target_chapter.name if target_chapter else target,
                strength=rel.strength,
                relationship_type=rel.relationship_type,
                mechanism=rel.mechanism
            )
    
    raise HTTPException(
        status_code=404,
        detail=f"Relationship from {source} to {target} not found"
    )


@router.get(
    "/criteria",
    response_model=List[Criterion],
    summary="Get all criteria"
)
async def get_criteria(
    chapter: Optional[str] = None,
    category: Optional[CriterionCategory] = None,
    current_user: dict = Depends(get_current_user_with_role)
):
    """
    Get all criteria with optional filtering.
    
    Args:
        chapter: Filter by chapter ID (e.g., "I-1", "II-4")
        category: Filter by category (essential, core, basic)
    """
    if chapter:
        chapter_obj = standards_service.get_chapter(chapter)
        if not chapter_obj:
            raise HTTPException(status_code=404, detail=f"Chapter {chapter} not found")
        criteria = chapter_obj.criteria
    else:
        criteria = standards_service.get_all_criteria()
    
    if category:
        criteria = [c for c in criteria if c.category == category]
    
    return criteria


@router.get(
    "/statistics",
    summary="Get graph statistics"
)
async def get_graph_statistics(
    current_user: dict = Depends(get_current_user_with_role)
):
    """Get statistics about the standards graph."""
    parts = standards_service.get_parts()
    chapters = standards_service.get_all_chapters()
    criteria = standards_service.get_all_criteria()
    relationships = standards_service.get_causal_relationships()
    
    essential_count = sum(1 for c in criteria if c.category == CriterionCategory.ESSENTIAL)
    core_count = sum(1 for c in criteria if c.category == CriterionCategory.CORE)
    basic_count = sum(1 for c in criteria if c.category == CriterionCategory.BASIC)
    
    # Calculate average relationship strength
    avg_strength = sum(r.strength for r in relationships) / len(relationships) if relationships else 0
    
    # Group relationships by type
    rel_by_type = {}
    for r in relationships:
        rel_by_type[r.relationship_type] = rel_by_type.get(r.relationship_type, 0) + 1
    
    return {
        "parts": len(parts),
        "chapters": len(chapters),
        "criteria": {
            "total": len(criteria),
            "essential": essential_count,
            "core": core_count,
            "basic": basic_count,
        },
        "relationships": {
            "total": len(relationships),
            "average_strength": round(avg_strength, 3),
            "by_type": rel_by_type,
        },
        "parts_detail": [
            {
                "number": p.number,
                "name": p.name,
                "chapters": len(p.chapters),
                "criteria": sum(len(c.criteria) for c in p.chapters),
            }
            for p in parts
        ]
    }


