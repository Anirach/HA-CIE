"""Hospital API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from app.core.security import get_current_user_with_role
from app.models.hospital import Hospital, HospitalType, Ownership, Region
from app.models.assessment import Assessment, CriterionScore, AccreditationLevel
from app.services.hospital_service import hospital_service
from app.services.assessment_service import assessment_service

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])


class HospitalCreate(BaseModel):
    """Request schema for creating a hospital."""
    name: str
    name_th: Optional[str] = None
    bed_count: int = 0
    hospital_type: HospitalType = HospitalType.GENERAL
    region: Region = Region.CENTRAL
    ownership: Ownership = Ownership.PUBLIC
    province: Optional[str] = None
    address: Optional[str] = None
    has_emergency: bool = True
    has_icu: bool = True
    has_surgery: bool = True
    has_obstetrics: bool = True
    has_pediatrics: bool = True
    first_accreditation_year: Optional[int] = None


class HospitalUpdate(BaseModel):
    """Request schema for updating a hospital."""
    name: Optional[str] = None
    name_th: Optional[str] = None
    bed_count: Optional[int] = None
    hospital_type: Optional[HospitalType] = None
    region: Optional[Region] = None
    ownership: Optional[Ownership] = None
    province: Optional[str] = None
    address: Optional[str] = None
    has_emergency: Optional[bool] = None
    has_icu: Optional[bool] = None
    has_surgery: Optional[bool] = None
    has_obstetrics: Optional[bool] = None
    has_pediatrics: Optional[bool] = None
    first_accreditation_year: Optional[int] = None
    current_accreditation_level: Optional[str] = None


class HospitalSummary(BaseModel):
    """Summary of a hospital with latest assessment info."""
    id: str
    name: str
    name_th: Optional[str]
    bed_count: int
    hospital_type: HospitalType
    region: Region
    ownership: Ownership
    current_accreditation_level: Optional[str]
    latest_assessment_date: Optional[str]
    latest_maturity_score: Optional[float]
    assessment_count: int


@router.get(
    "",
    response_model=List[HospitalSummary],
    summary="Get all hospitals"
)
async def get_hospitals(
    name: Optional[str] = Query(None, description="Filter by name"),
    hospital_type: Optional[HospitalType] = Query(None, description="Filter by type"),
    region: Optional[Region] = Query(None, description="Filter by region"),
    ownership: Optional[Ownership] = Query(None, description="Filter by ownership"),
    min_beds: Optional[int] = Query(None, description="Minimum bed count"),
    max_beds: Optional[int] = Query(None, description="Maximum bed count"),
    current_user: dict = Depends(get_current_user_with_role)
):
    """Get all hospitals with optional filters."""
    hospitals = hospital_service.search(
        name=name,
        hospital_type=hospital_type,
        region=region,
        ownership=ownership,
        min_beds=min_beds,
        max_beds=max_beds,
    )
    
    # Build summaries with assessment info
    summaries = []
    for h in hospitals:
        latest = assessment_service.get_latest_by_hospital(h.id)
        assessments = assessment_service.get_by_hospital(h.id)
        
        summaries.append(HospitalSummary(
            id=h.id,
            name=h.name,
            name_th=h.name_th,
            bed_count=h.bed_count,
            hospital_type=h.hospital_type,
            region=h.region,
            ownership=h.ownership,
            current_accreditation_level=latest.accreditation_level.value if latest else None,
            latest_assessment_date=latest.assessment_date.isoformat() if latest else None,
            latest_maturity_score=latest.overall_maturity_score if latest else None,
            assessment_count=len(assessments),
        ))
    
    return summaries


@router.get(
    "/statistics",
    summary="Get hospital statistics"
)
async def get_hospital_statistics(
    current_user: dict = Depends(get_current_user_with_role)
):
    """Get statistics about hospitals."""
    return hospital_service.get_statistics()


@router.get(
    "/{hospital_id}",
    response_model=Hospital,
    summary="Get hospital details"
)
async def get_hospital(
    hospital_id: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Get detailed information about a specific hospital."""
    hospital = hospital_service.get_by_id(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital


@router.post(
    "",
    response_model=Hospital,
    summary="Create a new hospital"
)
async def create_hospital(
    data: HospitalCreate,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Create a new hospital."""
    hospital = Hospital(**data.model_dump())
    return hospital_service.create(hospital)


@router.patch(
    "/{hospital_id}",
    response_model=Hospital,
    summary="Update a hospital"
)
async def update_hospital(
    hospital_id: str,
    data: HospitalUpdate,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Update a hospital's information."""
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    hospital = hospital_service.update(hospital_id, updates)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital


@router.delete(
    "/{hospital_id}",
    summary="Delete a hospital"
)
async def delete_hospital(
    hospital_id: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Delete a hospital and all its assessments."""
    # Delete associated assessments first
    deleted_assessments = assessment_service.delete_by_hospital(hospital_id)
    
    # Delete hospital
    success = hospital_service.delete(hospital_id)
    if not success:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    return {
        "message": "Hospital deleted successfully",
        "deleted_assessments": deleted_assessments,
    }


class UploadResult(BaseModel):
    """Result of file upload."""
    success: bool
    message: str
    hospital_id: Optional[str] = None
    hospital_name: Optional[str] = None
    assessments_imported: int = 0
    errors: List[str] = []


@router.post(
    "/upload",
    response_model=UploadResult,
    summary="Upload hospital data file"
)
async def upload_hospital_data(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user_with_role)
):
    """
    Upload hospital data from JSON or Excel file.
    
    JSON format:
    ```json
    {
        "hospital": {
            "name": "Hospital Name",
            "bed_count": 200,
            "hospital_type": "General",
            "region": "Central",
            "ownership": "Public"
        },
        "assessments": [
            {
                "assessment_date": "2024-01-15",
                "criterion_scores": [
                    {"criterion_id": "I-1-1", "score": 3.5, "notes": "..."}
                ]
            }
        ]
    }
    ```
    """
    errors: List[str] = []
    
    # Check file type
    filename = file.filename or ""
    if not filename.lower().endswith(('.json', '.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please use JSON or Excel files."
        )
    
    try:
        content = await file.read()
        
        if filename.lower().endswith('.json'):
            # Parse JSON
            try:
                data = json.loads(content.decode('utf-8'))
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
        else:
            # Excel parsing would require openpyxl
            # For now, return an error message
            raise HTTPException(
                status_code=400,
                detail="Excel import requires openpyxl library. Please use JSON format for now."
            )
        
        # Validate and process data
        hospital_data = data.get("hospital", {})
        assessments_data = data.get("assessments", [])
        
        if not hospital_data.get("name"):
            raise HTTPException(status_code=400, detail="Hospital name is required")
        
        # Check if hospital already exists (by name)
        existing = hospital_service.search(name=hospital_data.get("name"))
        
        if existing:
            # Smart merge: use existing hospital
            hospital = existing[0]
            result_msg = f"Merged data with existing hospital: {hospital.name}"
        else:
            # Create new hospital
            hospital_type_str = hospital_data.get("hospital_type", "General")
            region_str = hospital_data.get("region", "Central")
            ownership_str = hospital_data.get("ownership", "Public")
            
            # Map string values to enums
            try:
                h_type = HospitalType(hospital_type_str)
            except ValueError:
                h_type = HospitalType.GENERAL
                errors.append(f"Unknown hospital type '{hospital_type_str}', defaulting to General")
            
            try:
                h_region = Region(region_str)
            except ValueError:
                h_region = Region.CENTRAL
                errors.append(f"Unknown region '{region_str}', defaulting to Central")
            
            try:
                h_ownership = Ownership(ownership_str)
            except ValueError:
                h_ownership = Ownership.PUBLIC
                errors.append(f"Unknown ownership '{ownership_str}', defaulting to Public")
            
            hospital = Hospital(
                name=hospital_data.get("name"),
                name_th=hospital_data.get("name_th"),
                bed_count=hospital_data.get("bed_count", 0),
                hospital_type=h_type,
                region=h_region,
                ownership=h_ownership,
                province=hospital_data.get("province"),
                address=hospital_data.get("address"),
            )
            hospital = hospital_service.create(hospital)
            result_msg = f"Created new hospital: {hospital.name}"
        
        # Process assessments
        assessments_imported = 0
        for a_data in assessments_data:
            try:
                # Parse assessment date
                a_date_str = a_data.get("assessment_date", "")
                if a_date_str:
                    a_date = datetime.fromisoformat(a_date_str.replace('Z', '+00:00'))
                else:
                    a_date = datetime.now()
                
                # Parse criterion scores
                scores = []
                for cs in a_data.get("criterion_scores", []):
                    score_val = cs.get("score", 0)
                    if not (1.0 <= score_val <= 5.0):
                        errors.append(f"Score {score_val} out of range (1-5) for criterion {cs.get('criterion_id')}")
                        continue
                    
                    scores.append(CriterionScore(
                        criterion_id=cs.get("criterion_id", ""),
                        score=score_val,
                        evidence=cs.get("notes") or cs.get("evidence"),
                        notes=cs.get("notes"),
                    ))
                
                # Calculate overall score (simple average for now)
                if scores:
                    overall_score = sum(s.score for s in scores) / len(scores)
                else:
                    overall_score = 0
                
                # Determine accreditation level
                if overall_score >= 4.0:
                    level = AccreditationLevel.EXCELLENT
                elif overall_score >= 3.5:
                    level = AccreditationLevel.VERY_GOOD
                elif overall_score >= 3.0:
                    level = AccreditationLevel.GOOD
                elif overall_score >= 2.5:
                    level = AccreditationLevel.PASS
                else:
                    level = AccreditationLevel.NOT_PASSED
                
                assessment = Assessment(
                    hospital_id=hospital.id,
                    assessment_date=a_date,
                    overall_maturity_score=round(overall_score, 2),
                    accreditation_level=level,
                    criterion_scores=scores,
                )
                assessment_service.create(assessment)
                assessments_imported += 1
                
            except Exception as e:
                errors.append(f"Error importing assessment: {str(e)}")
        
        return UploadResult(
            success=True,
            message=result_msg,
            hospital_id=hospital.id,
            hospital_name=hospital.name,
            assessments_imported=assessments_imported,
            errors=errors,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

