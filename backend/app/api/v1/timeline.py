"""
Timeline API endpoints for assessment history visualization.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.services.timeline_service import get_timeline_service

router = APIRouter(prefix="/timeline", tags=["timeline"])


@router.get("/snapshots")
async def get_all_snapshots():
    """
    Get all available timeline snapshots.
    Returns a list of snapshot summaries for timeline navigation.
    """
    service = get_timeline_service()
    return {
        "snapshots": service.get_all_snapshots(),
        "total": len(service.get_all_snapshots()),
    }


@router.get("/snapshots/{index}")
async def get_snapshot(index: int):
    """
    Get a specific snapshot by index.
    Returns full snapshot data including all chapter scores.
    """
    service = get_timeline_service()
    snapshot = service.get_snapshot(index)
    
    if not snapshot:
        raise HTTPException(
            status_code=404,
            detail=f"Snapshot with index {index} not found"
        )
    
    return snapshot


@router.get("/compare")
async def compare_snapshots(
    from_index: int = Query(..., description="Starting snapshot index"),
    to_index: int = Query(..., description="Ending snapshot index"),
):
    """
    Compare two snapshots and return detailed changes.
    Useful for understanding what changed between assessments.
    """
    service = get_timeline_service()
    comparison = service.get_snapshot_comparison(from_index, to_index)
    
    if "error" in comparison:
        raise HTTPException(status_code=400, detail=comparison["error"])
    
    return comparison


@router.get("/chapters/{chapter_id}/history")
async def get_chapter_history(chapter_id: str):
    """
    Get the score history for a specific chapter across all snapshots.
    Useful for showing trends over time for individual chapters.
    """
    service = get_timeline_service()
    history = service.get_chapter_history(chapter_id)
    
    if not history.get("history"):
        raise HTTPException(
            status_code=404,
            detail=f"No history found for chapter {chapter_id}"
        )
    
    return history


@router.get("/latest")
async def get_latest_snapshot():
    """
    Get the most recent snapshot.
    Convenience endpoint for showing current state.
    """
    service = get_timeline_service()
    snapshots = service.get_all_snapshots()
    
    if not snapshots:
        raise HTTPException(status_code=404, detail="No snapshots available")
    
    latest_index = len(snapshots) - 1
    return service.get_snapshot(latest_index)

