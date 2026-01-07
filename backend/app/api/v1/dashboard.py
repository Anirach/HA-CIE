"""Dashboard API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date

from app.core.security import get_current_user_with_role
from app.services.hospital_service import hospital_service
from app.services.assessment_service import assessment_service
from app.services.standards_service import standards_service, CriterionCategory

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class DomainScore(BaseModel):
    """Score for a domain (part)."""
    part: str
    name: str
    score: float
    weight: float
    color: str
    chapter_count: int


class ChapterTrend(BaseModel):
    """Trend data for a chapter."""
    chapter_id: str
    chapter_name: str
    scores: List[Dict]  # [{date, score}]
    current_score: float
    change: Optional[float]


class CriticalGap(BaseModel):
    """A critical gap that needs attention."""
    criterion_id: str
    criterion_name: str
    chapter_id: str
    chapter_name: str
    score: float
    category: str
    priority: str  # critical, high, medium


class DashboardData(BaseModel):
    """Complete dashboard data."""
    hospital_id: str
    hospital_name: str
    latest_assessment_id: Optional[str]
    latest_assessment_date: Optional[str]
    
    # Overall scores
    overall_maturity_score: Optional[float]
    previous_score: Optional[float]
    score_change: Optional[float]
    accreditation_level: Optional[str]
    target_level: str
    
    # Domain scores
    domain_scores: List[DomainScore]
    
    # Compliance stats
    total_criteria: int
    criteria_assessed: int
    compliance_percentage: float
    
    # Category breakdown
    essential_met: int
    essential_total: int
    core_met: int
    core_total: int
    basic_met: int
    basic_total: int
    
    # Trends
    assessment_count: int
    
    # Gaps
    critical_gaps: List[CriticalGap]


@router.get(
    "/{hospital_id}",
    response_model=DashboardData,
    summary="Get dashboard data for a hospital"
)
async def get_dashboard(
    hospital_id: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Get comprehensive dashboard data for a hospital."""
    # Get hospital
    hospital = hospital_service.get_by_id(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Get assessments
    assessments = assessment_service.get_by_hospital(hospital_id)
    latest = assessments[-1] if assessments else None
    previous = assessments[-2] if len(assessments) >= 2 else None
    
    # Calculate score change
    score_change = None
    if latest and previous and latest.overall_maturity_score and previous.overall_maturity_score:
        score_change = round(latest.overall_maturity_score - previous.overall_maturity_score, 2)
    
    # Get domain scores
    domain_scores = []
    parts = standards_service.get_parts()
    for part in parts:
        part_score = latest.part_scores.get(part.number, 0) if latest else 0
        domain_scores.append(DomainScore(
            part=part.number,
            name=part.name,
            score=part_score,
            weight=part.weight,
            color=part.color,
            chapter_count=len(part.chapters),
        ))
    
    # Calculate criteria stats
    all_criteria = standards_service.get_all_criteria()
    total_criteria = len(all_criteria)
    
    score_lookup = {}
    if latest:
        score_lookup = {cs.criterion_id: cs.score for cs in latest.criterion_scores}
    
    criteria_assessed = len(score_lookup)
    compliance_percentage = round(criteria_assessed / total_criteria * 100, 1) if total_criteria > 0 else 0
    
    # Category breakdown
    essential_criteria = [c for c in all_criteria if c.category == CriterionCategory.ESSENTIAL]
    core_criteria = [c for c in all_criteria if c.category == CriterionCategory.CORE]
    basic_criteria = [c for c in all_criteria if c.category == CriterionCategory.BASIC]
    
    def count_met(criteria_list, threshold=3.0):
        met = 0
        for c in criteria_list:
            if c.id in score_lookup and score_lookup[c.id] >= threshold:
                met += 1
        return met
    
    essential_met = count_met(essential_criteria)
    core_met = count_met(core_criteria)
    basic_met = count_met(basic_criteria)
    
    # Find critical gaps (essential criteria with low scores)
    critical_gaps = []
    for criterion in all_criteria:
        if criterion.id in score_lookup:
            score = score_lookup[criterion.id]
            if score < 3.0:
                # Find chapter for this criterion
                chapter_name = ""
                chapter_id = ""
                for part in parts:
                    for chapter in part.chapters:
                        for c in chapter.criteria:
                            if c.id == criterion.id:
                                chapter_name = chapter.name
                                chapter_id = chapter.id
                                break
                
                # Determine priority
                if criterion.category == CriterionCategory.ESSENTIAL and score < 2.0:
                    priority = "critical"
                elif criterion.category == CriterionCategory.ESSENTIAL:
                    priority = "high"
                elif criterion.category == CriterionCategory.CORE and score < 2.5:
                    priority = "high"
                else:
                    priority = "medium"
                
                critical_gaps.append(CriticalGap(
                    criterion_id=criterion.id,
                    criterion_name=criterion.name,
                    chapter_id=chapter_id,
                    chapter_name=chapter_name,
                    score=score,
                    category=criterion.category.value,
                    priority=priority,
                ))
    
    # Sort gaps by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2}
    critical_gaps.sort(key=lambda g: (priority_order.get(g.priority, 3), g.score))
    
    # Determine target level
    current_level = latest.accreditation_level.value if latest else "not_accredited"
    target_map = {
        "not_accredited": "pass",
        "pass": "good",
        "good": "very_good",
        "very_good": "excellent",
        "excellent": "excellent",
    }
    target_level = target_map.get(current_level, "good")
    
    return DashboardData(
        hospital_id=hospital_id,
        hospital_name=hospital.name,
        latest_assessment_id=latest.id if latest else None,
        latest_assessment_date=latest.assessment_date.isoformat() if latest else None,
        overall_maturity_score=latest.overall_maturity_score if latest else None,
        previous_score=previous.overall_maturity_score if previous else None,
        score_change=score_change,
        accreditation_level=current_level,
        target_level=target_level,
        domain_scores=domain_scores,
        total_criteria=total_criteria,
        criteria_assessed=criteria_assessed,
        compliance_percentage=compliance_percentage,
        essential_met=essential_met,
        essential_total=len(essential_criteria),
        core_met=core_met,
        core_total=len(core_criteria),
        basic_met=basic_met,
        basic_total=len(basic_criteria),
        assessment_count=len(assessments),
        critical_gaps=critical_gaps[:15],  # Top 15 gaps
    )


@router.get(
    "/{hospital_id}/trends",
    summary="Get trend data for dashboard charts"
)
async def get_dashboard_trends(
    hospital_id: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Get trend data for dashboard visualizations."""
    hospital = hospital_service.get_by_id(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    trends = assessment_service.get_trends(hospital_id)
    
    # Add chapter-level trends for sparklines
    assessments = assessment_service.get_by_hospital(hospital_id)
    chapter_trends = []
    
    chapters = standards_service.get_all_chapters()
    for chapter in chapters:
        scores = []
        for assessment in assessments:
            # Calculate chapter score from criterion scores
            score_lookup = {cs.criterion_id: cs.score for cs in assessment.criterion_scores}
            chapter_criteria_scores = []
            for c in chapter.criteria:
                if c.id in score_lookup:
                    chapter_criteria_scores.append(score_lookup[c.id])
            
            if chapter_criteria_scores:
                avg = sum(chapter_criteria_scores) / len(chapter_criteria_scores)
                scores.append({
                    "date": assessment.assessment_date.isoformat(),
                    "score": round(avg, 2),
                })
        
        current_score = scores[-1]["score"] if scores else 0
        change = None
        if len(scores) >= 2:
            change = round(scores[-1]["score"] - scores[0]["score"], 2)
        
        chapter_trends.append({
            "chapter_id": chapter.id,
            "chapter_name": chapter.name,
            "scores": scores,
            "current_score": current_score,
            "change": change,
        })
    
    return {
        **trends,
        "chapter_trends": chapter_trends,
    }


@router.get(
    "/{hospital_id}/domain/{part_number}",
    summary="Get detailed domain data"
)
async def get_domain_detail(
    hospital_id: str,
    part_number: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Get detailed data for a specific domain (part)."""
    hospital = hospital_service.get_by_id(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    part = standards_service.get_part(part_number)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    latest = assessment_service.get_latest_by_hospital(hospital_id)
    score_lookup = {}
    if latest:
        score_lookup = {cs.criterion_id: cs.score for cs in latest.criterion_scores}
    
    chapters_data = []
    for chapter in part.chapters:
        criteria_data = []
        chapter_scores = []
        
        for criterion in chapter.criteria:
            score = score_lookup.get(criterion.id)
            if score is not None:
                chapter_scores.append(score)
            
            criteria_data.append({
                "id": criterion.id,
                "name": criterion.name,
                "category": criterion.category.value,
                "weight": criterion.weight,
                "score": score,
                "status": _get_status(score) if score else "not_assessed",
            })
        
        chapter_avg = sum(chapter_scores) / len(chapter_scores) if chapter_scores else None
        
        chapters_data.append({
            "id": chapter.id,
            "name": chapter.name,
            "weight": chapter.weight,
            "focus": chapter.focus,
            "score": round(chapter_avg, 2) if chapter_avg else None,
            "criteria_count": len(chapter.criteria),
            "criteria_assessed": len(chapter_scores),
            "criteria": criteria_data,
        })
    
    return {
        "part_number": part.number,
        "part_name": part.name,
        "part_weight": part.weight,
        "part_color": part.color,
        "part_score": latest.part_scores.get(part_number) if latest else None,
        "chapters": chapters_data,
    }


def _get_status(score: Optional[float]) -> str:
    """Get status based on score."""
    if score is None:
        return "not_assessed"
    if score >= 4.0:
        return "excellent"
    if score >= 3.0:
        return "good"
    if score >= 2.0:
        return "needs_improvement"
    return "critical"


