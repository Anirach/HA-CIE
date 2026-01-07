"""Causal inference API endpoints - QI Team only."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

from app.core.security import require_role, UserRole, get_current_user_with_role
from app.services.causal_service import get_causal_service, CausalMethod

router = APIRouter(prefix="/causal", tags=["Causal Inference"])


class EstimateEffectRequest(BaseModel):
    """Request schema for effect estimation."""
    treatment_criterion: str
    outcome_criterion: str
    method: str = CausalMethod.LINEAR_REGRESSION
    confounders: Optional[List[str]] = None
    include_sensitivity: bool = False


class CounterfactualRequest(BaseModel):
    """Request schema for counterfactual analysis."""
    hospital_id: str
    intervention_criterion: str
    intervention_value: float
    target_criterion: str


class RootCauseRequest(BaseModel):
    """Request schema for root cause analysis."""
    gap_criterion: str
    hospital_id: str


class CascadeRequest(BaseModel):
    """Request schema for cascade analysis."""
    intervention_criterion: str
    max_depth: int = 3


@router.post(
    "/estimate-effect",
    summary="Estimate causal effect (ATE) - QI Team only"
)
async def estimate_effect(
    request: EstimateEffectRequest,
    current_user: dict = Depends(require_role([UserRole.QI_TEAM]))
):
    """
    Estimate the Average Treatment Effect (ATE) of improving one criterion on another.

    This endpoint uses causal inference methods including:
    - Linear Regression
    - Propensity Score Weighting
    - Propensity Score Matching
    - Double Machine Learning (CausalForestDML)
    - Instrumental Variable

    **Requires QI Team role.**
    """
    service = get_causal_service()
    
    result = service.estimate_ate(
        treatment=request.treatment_criterion,
        outcome=request.outcome_criterion,
        method=request.method,
        confounders=request.confounders,
    )
    
    # Add sensitivity analysis if requested
    if request.include_sensitivity:
        sensitivity = service.sensitivity_analysis(
            treatment=request.treatment_criterion,
            outcome=request.outcome_criterion,
            ate=result["ate"],
        )
        result["sensitivity_analysis"] = sensitivity
    
    return result


@router.post(
    "/counterfactual",
    summary="Generate counterfactual prediction - QI Team only"
)
async def counterfactual_prediction(
    request: CounterfactualRequest,
    current_user: dict = Depends(require_role([UserRole.QI_TEAM]))
):
    """
    Generate a counterfactual prediction: what would the target criterion
    score be if we improved the intervention criterion to the specified value?

    **Requires QI Team role.**
    """
    service = get_causal_service()
    
    return service.counterfactual_analysis(
        hospital_id=request.hospital_id,
        intervention_criterion=request.intervention_criterion,
        intervention_value=request.intervention_value,
        target_criterion=request.target_criterion,
    )


@router.post(
    "/root-cause",
    summary="Analyze root cause of a quality gap - QI Team only"
)
async def root_cause_analysis(
    request: RootCauseRequest,
    current_user: dict = Depends(require_role([UserRole.QI_TEAM]))
):
    """
    Perform root cause analysis for a quality gap using the causal graph.

    Identifies upstream criteria that may be causing the gap and provides
    recommendations for improvement.

    **Requires QI Team role.**
    """
    service = get_causal_service()
    
    return service.root_cause_analysis(
        gap_criterion=request.gap_criterion,
        hospital_id=request.hospital_id,
    )


@router.post(
    "/cascade",
    summary="Analyze cascade effects - QI Team only"
)
async def cascade_analysis(
    request: CascadeRequest,
    current_user: dict = Depends(require_role([UserRole.QI_TEAM]))
):
    """
    Analyze the cascade effects of improving a criterion.

    Shows how improvement propagates through the causal graph to
    downstream criteria.

    **Requires QI Team role.**
    """
    service = get_causal_service()
    
    return service.cascade_analysis(
        intervention_criterion=request.intervention_criterion,
        max_depth=request.max_depth,
    )


@router.get(
    "/methods",
    summary="Get available causal inference methods"
)
async def get_methods(
    current_user: dict = Depends(get_current_user_with_role)
):
    """
    Get list of available causal inference methods with descriptions.

    Available to all authenticated users.
    """
    service = get_causal_service()
    return {"methods": service.get_available_methods()}


@router.get(
    "/sensitivity/{treatment}/{outcome}",
    summary="Perform sensitivity analysis - QI Team only"
)
async def sensitivity_analysis(
    treatment: str,
    outcome: str,
    ate: float = Query(..., description="The estimated ATE to analyze"),
    current_user: dict = Depends(require_role([UserRole.QI_TEAM]))
):
    """
    Perform sensitivity analysis to assess robustness to unmeasured confounding.

    **Requires QI Team role.**
    """
    service = get_causal_service()
    
    return service.sensitivity_analysis(
        treatment=treatment,
        outcome=outcome,
        ate=ate,
    )


@router.get(
    "/paths/{source}/{target}",
    summary="Find causal paths between criteria"
)
async def find_causal_paths(
    source: str,
    target: str,
    current_user: dict = Depends(get_current_user_with_role)
):
    """
    Find all causal paths between a source and target criterion.

    Available to all authenticated users.
    """
    service = get_causal_service()
    return service._find_causal_paths(source, target)


@router.get(
    "/graph/summary",
    summary="Get causal graph summary"
)
async def get_graph_summary(
    current_user: dict = Depends(get_current_user_with_role)
):
    """
    Get a summary of the causal graph structure.

    Available to all authenticated users.
    """
    service = get_causal_service()
    graph = service._causal_graph
    
    return {
        "total_nodes": len(graph["nodes"]),
        "total_edges": len(graph["edges"]),
        "nodes_by_part": _count_by_part(graph["nodes"]),
        "edges_sample": graph["edges"][:10],
    }


def _count_by_part(nodes: dict) -> dict:
    """Count nodes by part."""
    counts = {}
    for node_id, node_data in nodes.items():
        part = node_data.get("part", "Unknown")
        counts[part] = counts.get(part, 0) + 1
    return counts
