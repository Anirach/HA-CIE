"""Assessment API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

from app.core.security import get_current_user_with_role
from app.models.assessment import Assessment, CriterionScore, AccreditationLevel
from app.services.assessment_service import assessment_service
from app.services.hospital_service import hospital_service

router = APIRouter(prefix="/hospitals/{hospital_id}/assessments", tags=["Assessments"])


class CriterionScoreInput(BaseModel):
    """Input schema for a criterion score."""
    criterion_id: str
    score: float
    notes: Optional[str] = None
    evidence: Optional[str] = None


class AssessmentCreate(BaseModel):
    """Request schema for creating an assessment."""
    assessment_date: date
    assessment_cycle: str
    assessment_type: str = "self"
    assessor_name: Optional[str] = None
    assessor_organization: Optional[str] = None
    criterion_scores: List[CriterionScoreInput] = []
    notes: Optional[str] = None
    is_draft: bool = True


class AssessmentUpdate(BaseModel):
    """Request schema for updating an assessment."""
    assessment_date: Optional[date] = None
    assessment_cycle: Optional[str] = None
    assessment_type: Optional[str] = None
    assessor_name: Optional[str] = None
    assessor_organization: Optional[str] = None
    criterion_scores: Optional[List[CriterionScoreInput]] = None
    notes: Optional[str] = None
    is_draft: Optional[bool] = None


class AssessmentSummary(BaseModel):
    """Summary of an assessment."""
    id: str
    hospital_id: str
    assessment_date: date
    assessment_cycle: str
    assessment_type: str
    overall_maturity_score: Optional[float]
    accreditation_level: AccreditationLevel
    part_scores: dict
    data_completeness: Optional[float]
    is_draft: bool
    is_submitted: bool


@router.get(
    "",
    response_model=List[AssessmentSummary],
    summary="Get all assessments for a hospital"
)
async def get_assessments(
    hospital_id: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Get all assessments for a specific hospital."""
    # Verify hospital exists
    hospital = hospital_service.get_by_id(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    assessments = assessment_service.get_by_hospital(hospital_id)
    
    return [
        AssessmentSummary(
            id=a.id,
            hospital_id=a.hospital_id,
            assessment_date=a.assessment_date,
            assessment_cycle=a.assessment_cycle,
            assessment_type=a.assessment_type,
            overall_maturity_score=a.overall_maturity_score,
            accreditation_level=a.accreditation_level,
            part_scores=a.part_scores,
            data_completeness=a.data_completeness,
            is_draft=a.is_draft,
            is_submitted=a.is_submitted,
        )
        for a in assessments
    ]


@router.get(
    "/latest",
    response_model=Assessment,
    summary="Get latest assessment for a hospital"
)
async def get_latest_assessment(
    hospital_id: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Get the most recent assessment for a hospital."""
    hospital = hospital_service.get_by_id(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    assessment = assessment_service.get_latest_by_hospital(hospital_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="No assessments found")
    
    return assessment


@router.get(
    "/trends",
    summary="Get assessment trends for a hospital"
)
async def get_assessment_trends(
    hospital_id: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Get score trends across all assessments for a hospital."""
    hospital = hospital_service.get_by_id(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    return assessment_service.get_trends(hospital_id)


@router.get(
    "/compare",
    summary="Compare two assessments"
)
async def compare_assessments(
    hospital_id: str,
    assessment_1: str = Query(..., description="First assessment ID"),
    assessment_2: str = Query(..., description="Second assessment ID"),
    current_user: dict = Depends(get_current_user_with_role)
):
    """Compare two assessments and show differences."""
    # Verify both assessments belong to this hospital
    a1 = assessment_service.get_by_id(assessment_1)
    a2 = assessment_service.get_by_id(assessment_2)
    
    if not a1 or a1.hospital_id != hospital_id:
        raise HTTPException(status_code=404, detail="Assessment 1 not found")
    if not a2 or a2.hospital_id != hospital_id:
        raise HTTPException(status_code=404, detail="Assessment 2 not found")
    
    return assessment_service.compare_assessments(assessment_1, assessment_2)


@router.get(
    "/{assessment_id}",
    response_model=Assessment,
    summary="Get assessment details"
)
async def get_assessment(
    hospital_id: str,
    assessment_id: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Get detailed information about a specific assessment."""
    assessment = assessment_service.get_by_id(assessment_id)
    if not assessment or assessment.hospital_id != hospital_id:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


@router.get(
    "/{assessment_id}/chapters",
    summary="Get chapter scores for an assessment"
)
async def get_chapter_scores(
    hospital_id: str,
    assessment_id: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Get detailed chapter-level scores for an assessment."""
    assessment = assessment_service.get_by_id(assessment_id)
    if not assessment or assessment.hospital_id != hospital_id:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    chapter_scores = assessment_service.get_chapter_scores(assessment_id)
    return {"chapter_scores": [cs.model_dump() for cs in chapter_scores]}


@router.post(
    "",
    response_model=Assessment,
    summary="Create a new assessment"
)
async def create_assessment(
    hospital_id: str,
    data: AssessmentCreate,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Create a new assessment for a hospital."""
    # Verify hospital exists
    hospital = hospital_service.get_by_id(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Convert criterion scores
    criterion_scores = [
        CriterionScore(**cs.model_dump())
        for cs in data.criterion_scores
    ]
    
    assessment = Assessment(
        hospital_id=hospital_id,
        assessment_date=data.assessment_date,
        assessment_cycle=data.assessment_cycle,
        assessment_type=data.assessment_type,
        assessor_name=data.assessor_name,
        assessor_organization=data.assessor_organization,
        criterion_scores=criterion_scores,
        notes=data.notes,
        is_draft=data.is_draft,
    )
    
    return assessment_service.create(assessment)


@router.patch(
    "/{assessment_id}",
    response_model=Assessment,
    summary="Update an assessment"
)
async def update_assessment(
    hospital_id: str,
    assessment_id: str,
    data: AssessmentUpdate,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Update an existing assessment."""
    assessment = assessment_service.get_by_id(assessment_id)
    if not assessment or assessment.hospital_id != hospital_id:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    updates = {}
    for k, v in data.model_dump().items():
        if v is not None:
            if k == 'criterion_scores':
                updates[k] = [CriterionScore(**cs) for cs in v]
            else:
                updates[k] = v
    
    updated = assessment_service.update(assessment_id, updates)
    return updated


@router.delete(
    "/{assessment_id}",
    summary="Delete an assessment"
)
async def delete_assessment(
    hospital_id: str,
    assessment_id: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Delete an assessment."""
    assessment = assessment_service.get_by_id(assessment_id)
    if not assessment or assessment.hospital_id != hospital_id:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    success = assessment_service.delete(assessment_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete assessment")
    
    return {"message": "Assessment deleted successfully"}


@router.post(
    "/{assessment_id}/submit",
    summary="Submit an assessment"
)
async def submit_assessment(
    hospital_id: str,
    assessment_id: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Submit a draft assessment for review."""
    assessment = assessment_service.get_by_id(assessment_id)
    if not assessment or assessment.hospital_id != hospital_id:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if assessment.is_submitted:
        raise HTTPException(status_code=400, detail="Assessment already submitted")
    
    from datetime import datetime
    updated = assessment_service.update(assessment_id, {
        "is_draft": False,
        "is_submitted": True,
        "submitted_at": datetime.utcnow(),
    })
    
    return {"message": "Assessment submitted successfully", "assessment": updated}

