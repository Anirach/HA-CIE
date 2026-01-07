"""
ISQua EEA Integration API endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict

from app.services.isqua_service import get_isqua_service

router = APIRouter(prefix="/isqua", tags=["isqua"])


class ISQuaAssessmentRequest(BaseModel):
    """Request for ISQua assessment."""
    ha_chapter_scores: Dict[str, float]


@router.get("/principles")
async def get_isqua_principles():
    """
    Get the ISQua 9 Principles framework.
    
    Returns all principles with their focus areas and HA mappings.
    """
    service = get_isqua_service()
    return {"principles": service.get_principles()}


@router.get("/principles/{principle_id}")
async def get_principle_details(principle_id: str):
    """
    Get detailed information about an ISQua principle.
    """
    service = get_isqua_service()
    principle = service.get_principle(principle_id)
    
    if not principle:
        raise HTTPException(status_code=404, detail="Principle not found")
    
    return principle


@router.get("/ha-mapping")
async def get_ha_to_isqua_mapping():
    """
    Get the mapping between HA Thailand chapters and ISQua principles.
    
    Shows alignment strength and notes for each mapping.
    """
    service = get_isqua_service()
    return {"mapping": service.get_ha_to_isqua_mapping()}


@router.post("/assess")
async def assess_isqua_compliance(request: ISQuaAssessmentRequest):
    """
    Perform full ISQua assessment based on HA Thailand chapter scores.
    
    Converts HA scores to ISQua ratings and provides principle-level analysis.
    """
    service = get_isqua_service()
    return service.full_isqua_assessment(request.ha_chapter_scores)


@router.post("/assess/{principle_id}")
async def assess_single_principle(
    principle_id: str,
    request: ISQuaAssessmentRequest,
):
    """
    Assess compliance with a single ISQua principle.
    """
    service = get_isqua_service()
    result = service.assess_principle_compliance(
        principle_id,
        request.ha_chapter_scores,
    )
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/convert/ha-to-isqua")
async def convert_ha_to_isqua(
    ha_score: float = Query(..., ge=1.0, le=5.0, description="HA Thailand score (1-5)"),
):
    """
    Convert HA Thailand score to ISQua rating.
    
    HA 1.0-1.9 → ISQua 1 (Does not meet)
    HA 2.0-3.9 → ISQua 2 (Partially meets)
    HA 4.0-5.0 → ISQua 3 (Fully meets)
    """
    service = get_isqua_service()
    isqua_rating = service.convert_ha_score_to_isqua(ha_score)
    
    rating_texts = {
        1: "Does not meet criterion",
        2: "Partially meets criterion", 
        3: "Fully meets criterion",
    }
    
    return {
        "ha_score": ha_score,
        "isqua_rating": isqua_rating,
        "isqua_description": rating_texts.get(isqua_rating, "Unknown"),
    }


@router.get("/convert/isqua-to-ha")
async def convert_isqua_to_ha(
    isqua_rating: int = Query(..., ge=1, le=3, description="ISQua rating (1-3)"),
):
    """
    Convert ISQua rating to approximate HA Thailand score.
    
    ISQua 1 → HA ~1.5
    ISQua 2 → HA ~2.5
    ISQua 3 → HA ~4.5
    """
    service = get_isqua_service()
    ha_score = service.convert_isqua_to_ha_score(isqua_rating)
    
    return {
        "isqua_rating": isqua_rating,
        "ha_score_approximate": ha_score,
        "ha_score_range": {
            1: "1.0 - 1.9",
            2: "2.0 - 3.9",
            3: "4.0 - 5.0",
        }.get(isqua_rating, "Unknown"),
    }

