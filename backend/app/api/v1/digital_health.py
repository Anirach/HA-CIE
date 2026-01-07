"""
WHO DISAH Digital Health API endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Optional

from app.services.digital_health_service import get_digital_health_service

router = APIRouter(prefix="/digital-health", tags=["digital-health"])


class ReadinessAssessmentRequest(BaseModel):
    """Request for digital health readiness assessment."""
    hospital_id: str
    assessments: Dict[str, str]  # intervention_id -> readiness_level


@router.get("/framework")
async def get_disah_framework():
    """
    Get the WHO DISAH framework structure.
    
    Returns all categories and intervention counts.
    """
    service = get_digital_health_service()
    return service.get_framework()


@router.get("/categories/{category_id}")
async def get_category_details(category_id: str):
    """
    Get detailed information about a DISAH category.
    
    Includes all interventions and their properties.
    """
    service = get_digital_health_service()
    details = service.get_category_details(category_id)
    
    if not details:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return details


@router.post("/assess")
async def assess_readiness(request: ReadinessAssessmentRequest):
    """
    Assess digital health readiness for a hospital.
    
    Provide assessment levels for each intervention.
    Valid levels: not_started, planning, pilot, partial_implementation, 
                  full_implementation, optimizing
    """
    service = get_digital_health_service()
    return service.assess_readiness(request.hospital_id, request.assessments)


@router.get("/assessment/{hospital_id}")
async def get_assessment(hospital_id: str):
    """
    Get the latest digital health assessment for a hospital.
    """
    service = get_digital_health_service()
    assessment = service.get_hospital_assessment(hospital_id)
    
    if not assessment:
        raise HTTPException(
            status_code=404, 
            detail="No assessment found for this hospital"
        )
    
    return assessment


@router.get("/ha-alignment")
async def get_ha_alignment():
    """
    Get mapping between DISAH interventions and HA Thailand criteria.
    
    Shows how digital health systems support accreditation requirements.
    """
    service = get_digital_health_service()
    return {"alignments": service.get_ha_alignment()}


@router.get("/readiness-levels")
async def get_readiness_levels():
    """
    Get available readiness levels for assessment.
    """
    return {
        "levels": [
            {"id": "not_started", "name": "Not Started", "score": 0, "description": "No implementation activities"},
            {"id": "planning", "name": "Planning", "score": 1, "description": "Requirements gathering and planning"},
            {"id": "pilot", "name": "Pilot", "score": 2, "description": "Limited pilot implementation"},
            {"id": "partial_implementation", "name": "Partial Implementation", "score": 3, "description": "Deployed in some areas"},
            {"id": "full_implementation", "name": "Full Implementation", "score": 4, "description": "Organization-wide deployment"},
            {"id": "optimizing", "name": "Optimizing", "score": 5, "description": "Continuous improvement and optimization"},
        ]
    }


