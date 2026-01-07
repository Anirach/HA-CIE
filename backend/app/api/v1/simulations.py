"""Simulation API endpoints for What-If analysis."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from app.core.security import get_current_user_with_role, require_role, UserRole
from app.services.simulation_service import (
    simulation_service,
    Intervention,
    SimulationResult,
    Scenario,
)

router = APIRouter(prefix="/simulations", tags=["Simulations"])


class InterventionInput(BaseModel):
    """Input for a single intervention."""
    criterion_id: str
    target_score: float = Field(ge=1, le=5)
    effort_level: str = "medium"
    timeline_months: int = 6


class SimulationRequest(BaseModel):
    """Request to run a simulation."""
    hospital_id: str
    scenario_name: str = "Custom Simulation"
    interventions: List[InterventionInput]


class ScenarioSimulationRequest(BaseModel):
    """Request to run a pre-built scenario."""
    hospital_id: str
    scenario_id: str


class SimulationSummary(BaseModel):
    """Executive-friendly simulation summary."""
    hospital_id: str
    scenario_name: str
    current_score: float
    projected_score: float
    improvement: float
    current_level: str
    projected_level: str
    timeline_months: int
    effort_summary: str
    key_actions: List[str]
    risk_level: str
    confidence: str


@router.get(
    "/scenarios",
    response_model=List[Scenario],
    summary="Get available improvement scenarios"
)
async def get_scenarios(
    hospital_id: Optional[str] = Query(None, description="Filter scenarios suitable for this hospital"),
    current_user: dict = Depends(get_current_user_with_role)
):
    """
    Get list of pre-built improvement scenarios.
    
    If hospital_id is provided, returns only scenarios suitable for
    the hospital's current accreditation level.
    """
    return simulation_service.get_scenarios(hospital_id)


@router.get(
    "/scenarios/{scenario_id}",
    response_model=Scenario,
    summary="Get a specific scenario"
)
async def get_scenario(
    scenario_id: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """Get details of a specific improvement scenario."""
    scenario = simulation_service.get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.post(
    "/run",
    response_model=SimulationResult,
    summary="Run a custom simulation (QI Team)"
)
async def run_simulation(
    request: SimulationRequest,
    current_user: dict = Depends(require_role([UserRole.QI_TEAM]))
):
    """
    Run a what-if simulation with custom interventions.
    
    This endpoint is only available to QI Team members who need
    full access to technical simulation parameters.
    
    **Requires QI Team role.**
    """
    try:
        interventions = [
            Intervention(
                criterion_id=i.criterion_id,
                target_score=i.target_score,
                effort_level=i.effort_level,
                timeline_months=i.timeline_months,
            )
            for i in request.interventions
        ]
        
        result = simulation_service.run_simulation(
            hospital_id=request.hospital_id,
            interventions=interventions,
            scenario_name=request.scenario_name,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/run-scenario",
    response_model=SimulationResult,
    summary="Run a pre-built scenario"
)
async def run_scenario(
    request: ScenarioSimulationRequest,
    current_user: dict = Depends(get_current_user_with_role)
):
    """
    Run a pre-built improvement scenario.
    
    Available to all authenticated users.
    """
    scenario = simulation_service.get_scenario(request.scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    try:
        result = simulation_service.run_simulation(
            hospital_id=request.hospital_id,
            interventions=scenario.interventions,
            scenario_name=scenario.name,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/run-scenario/summary",
    response_model=SimulationSummary,
    summary="Run scenario and get executive summary"
)
async def run_scenario_summary(
    request: ScenarioSimulationRequest,
    current_user: dict = Depends(get_current_user_with_role)
):
    """
    Run a scenario and return an executive-friendly summary.
    
    Provides plain-language explanations suitable for hospital executives.
    """
    scenario = simulation_service.get_scenario(request.scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    try:
        result = simulation_service.run_simulation(
            hospital_id=request.hospital_id,
            interventions=scenario.interventions,
            scenario_name=scenario.name,
        )
        
        # Generate executive summary
        level_labels = {
            "excellent": "Excellent",
            "very_good": "Very Good",
            "good": "Good",
            "pass": "Pass",
            "not_accredited": "Not Accredited",
        }
        
        # Key actions from interventions
        key_actions = []
        for intervention in result.interventions[:5]:
            key_actions.append(
                f"Improve {intervention.criterion_id} to score {intervention.target_score}"
            )
        
        # Determine risk level
        if result.score_improvement > 0.3:
            risk_level = "Moderate - ambitious targets require sustained commitment"
        elif result.score_improvement > 0.15:
            risk_level = "Low - achievable with focused effort"
        else:
            risk_level = "Very Low - incremental improvements"
        
        # Confidence description
        spread = result.confidence_interval["high"] - result.confidence_interval["low"]
        if spread < 0.2:
            confidence = "High confidence in projections"
        elif spread < 0.4:
            confidence = "Moderate confidence - results may vary"
        else:
            confidence = "Lower confidence - multiple variables at play"
        
        return SimulationSummary(
            hospital_id=result.hospital_id,
            scenario_name=result.scenario_name,
            current_score=result.current_overall_score,
            projected_score=result.projected_overall_score,
            improvement=result.score_improvement,
            current_level=level_labels.get(result.current_level, result.current_level),
            projected_level=level_labels.get(result.projected_level, result.projected_level),
            timeline_months=result.estimated_months,
            effort_summary=result.effort_summary,
            key_actions=key_actions,
            risk_level=risk_level,
            confidence=confidence,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/priorities/{hospital_id}",
    summary="Get improvement priorities"
)
async def get_improvement_priorities(
    hospital_id: str,
    target_level: str = Query("next", description="Target level: next, good, very_good, excellent"),
    current_user: dict = Depends(get_current_user_with_role)
):
    """
    Get prioritized list of criteria to improve for maximum impact.
    
    Returns criteria ranked by their potential impact on overall score,
    weighted by category (Essential, Core, Basic).
    """
    priorities = simulation_service.get_improvement_priorities(hospital_id, target_level)
    if not priorities:
        raise HTTPException(status_code=404, detail="No assessment found for hospital")
    return {"priorities": priorities}


@router.get(
    "/cascade-preview",
    summary="Preview cascade effects (QI Team)"
)
async def preview_cascade(
    hospital_id: str,
    criterion_id: str,
    target_score: float = Query(..., ge=1, le=5),
    current_user: dict = Depends(require_role([UserRole.QI_TEAM]))
):
    """
    Preview the cascade effects of improving a single criterion.
    
    Shows how improving one criterion will affect related criteria
    through the causal graph.
    
    **Requires QI Team role.**
    """
    try:
        intervention = Intervention(
            criterion_id=criterion_id,
            target_score=target_score,
        )
        
        result = simulation_service.run_simulation(
            hospital_id=hospital_id,
            interventions=[intervention],
            scenario_name="Cascade Preview",
        )
        
        return {
            "intervention": {
                "criterion_id": criterion_id,
                "target_score": target_score,
                "current_score": intervention.current_score,
            },
            "direct_impact": result.score_improvement,
            "cascade_effects": result.cascade_effects,
            "total_criteria_affected": len(result.cascade_effects),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

