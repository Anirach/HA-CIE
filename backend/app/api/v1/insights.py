"""
AI Insights API endpoints.
Provides AI-generated insights and recommendations for quality improvement.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.services.insights_service import get_insights_service

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("")
async def get_insights(
    hospital_id: str = Query(default="hosp-001", description="Hospital ID to generate insights for"),
):
    """
    Generate comprehensive AI insights for a hospital.
    
    Returns gap analysis, trend analysis, risk assessment,
    root cause analysis, benchmarks, and prioritized recommendations.
    """
    service = get_insights_service()
    insights = service.generate_insights(hospital_id)
    return insights


@router.get("/categories")
async def get_insight_categories():
    """
    Get available insight categories.
    
    Returns a list of category definitions with icons for UI rendering.
    """
    service = get_insights_service()
    return {
        "categories": service.get_insight_categories()
    }


@router.get("/summary")
async def get_insights_summary(
    hospital_id: str = Query(default="hosp-001", description="Hospital ID"),
):
    """
    Get a brief summary of insights.
    
    Returns only summary statistics without full insight details.
    Useful for dashboard widgets.
    """
    service = get_insights_service()
    full_insights = service.generate_insights(hospital_id)
    
    return {
        "hospital_id": hospital_id,
        "generated_at": full_insights["generated_at"],
        "risk_score": full_insights["risk_score"],
        "risk_level": full_insights["risk_level"],
        "summary": full_insights["summary"],
        "top_recommendations": full_insights["recommendations"][:3] if full_insights["recommendations"] else [],
    }


@router.get("/risk-assessment")
async def get_risk_assessment(
    hospital_id: str = Query(default="hosp-001", description="Hospital ID"),
):
    """
    Get detailed risk assessment.
    
    Returns risk score, risk level, and risk-related insights.
    """
    service = get_insights_service()
    full_insights = service.generate_insights(hospital_id)
    
    risk_insights = [
        i for i in full_insights["insights"]
        if i.get("category") == "risk_assessment"
    ]
    
    return {
        "hospital_id": hospital_id,
        "risk_score": full_insights["risk_score"],
        "risk_level": full_insights["risk_level"],
        "risk_insights": risk_insights,
        "critical_count": full_insights["summary"]["by_priority"].get("critical", 0),
        "high_count": full_insights["summary"]["by_priority"].get("high", 0),
    }


@router.get("/recommendations")
async def get_recommendations(
    hospital_id: str = Query(default="hosp-001", description="Hospital ID"),
    limit: int = Query(default=10, ge=1, le=20, description="Maximum recommendations to return"),
):
    """
    Get prioritized improvement recommendations.
    
    Returns a ranked list of actionable recommendations.
    """
    service = get_insights_service()
    full_insights = service.generate_insights(hospital_id)
    
    return {
        "hospital_id": hospital_id,
        "recommendations": full_insights["recommendations"][:limit],
        "total_available": len(full_insights["recommendations"]),
    }


