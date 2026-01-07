"""
Simulation Service - What-If analysis and maturity projections.
Calculates the impact of improvement interventions on accreditation scores.
"""
import json
import math
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from pathlib import Path
from pydantic import BaseModel, Field

from app.services.standards_service import standards_service, CriterionCategory
from app.services.assessment_service import assessment_service
from app.core.config import settings


class Intervention(BaseModel):
    """A single improvement intervention."""
    criterion_id: str
    target_score: float = Field(ge=1, le=5)
    current_score: Optional[float] = None
    effort_level: str = "medium"  # low, medium, high
    timeline_months: int = 6


class CascadeEffect(BaseModel):
    """Effect of an intervention cascading to dependent criteria."""
    criterion_id: str
    chapter_id: str
    chapter_name: str
    current_score: float
    projected_score: float
    change: float
    path_length: int
    confidence: float


class SimulationResult(BaseModel):
    """Result of a simulation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hospital_id: str
    scenario_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Input
    interventions: List[Intervention]
    
    # Projected scores
    current_overall_score: float
    projected_overall_score: float
    score_improvement: float
    
    current_part_scores: Dict[str, float]
    projected_part_scores: Dict[str, float]
    
    current_level: str
    projected_level: str
    
    # Cascade effects
    cascade_effects: List[CascadeEffect]
    
    # Confidence
    confidence_interval: Dict[str, float]  # low, mid, high
    
    # Timeline
    estimated_months: int
    effort_summary: str


class Scenario(BaseModel):
    """A pre-built improvement scenario."""
    id: str
    name: str
    description: str
    target_areas: List[str]
    interventions: List[Intervention]
    expected_improvement: float
    effort_level: str
    timeline_months: int
    suitable_for: List[str]  # ['all', 'below_good', 'good_to_very_good', 'very_good_to_excellent']


class SimulationService:
    """Service for what-if simulations and maturity projections."""
    
    def __init__(self):
        self._scenarios = self._build_scenarios()
        self._causal_strengths = self._build_causal_lookup()
    
    def _build_causal_lookup(self) -> Dict[str, Dict[str, float]]:
        """Build lookup table for causal relationship strengths."""
        lookup = {}
        for rel in standards_service.get_causal_relationships():
            if rel.source not in lookup:
                lookup[rel.source] = {}
            lookup[rel.source][rel.target] = rel.strength
        return lookup
    
    def _build_scenarios(self) -> List[Scenario]:
        """Build pre-defined improvement scenarios."""
        return [
            Scenario(
                id="leadership_enhancement",
                name="Leadership Enhancement Program",
                description="Focus on strengthening leadership commitment and governance to drive quality culture",
                target_areas=["I-1", "I-2", "I-5"],
                interventions=[
                    Intervention(criterion_id="I-1.1", target_score=4.0, effort_level="medium", timeline_months=6),
                    Intervention(criterion_id="I-1.2", target_score=3.5, effort_level="low", timeline_months=3),
                    Intervention(criterion_id="I-1.3", target_score=4.0, effort_level="medium", timeline_months=6),
                    Intervention(criterion_id="I-2.1", target_score=3.5, effort_level="medium", timeline_months=6),
                    Intervention(criterion_id="I-5.1", target_score=3.5, effort_level="medium", timeline_months=6),
                ],
                expected_improvement=0.3,
                effort_level="medium",
                timeline_months=6,
                suitable_for=["all"],
            ),
            Scenario(
                id="patient_safety_focus",
                name="Patient Safety Focus",
                description="Intensive focus on essential safety criteria including IPC, medication safety, and care delivery",
                target_areas=["II-1", "II-4", "II-6", "III-4"],
                interventions=[
                    Intervention(criterion_id="II-1.3", target_score=4.0, effort_level="high", timeline_months=9),
                    Intervention(criterion_id="II-1.4", target_score=4.0, effort_level="high", timeline_months=9),
                    Intervention(criterion_id="II-4.1", target_score=4.0, effort_level="high", timeline_months=9),
                    Intervention(criterion_id="II-4.3", target_score=4.0, effort_level="medium", timeline_months=6),
                    Intervention(criterion_id="II-6.2", target_score=4.0, effort_level="high", timeline_months=9),
                    Intervention(criterion_id="II-6.4", target_score=4.0, effort_level="medium", timeline_months=6),
                    Intervention(criterion_id="III-4.2", target_score=4.0, effort_level="high", timeline_months=9),
                ],
                expected_improvement=0.4,
                effort_level="high",
                timeline_months=9,
                suitable_for=["all"],
            ),
            Scenario(
                id="quality_system_foundation",
                name="Quality System Foundation",
                description="Build strong quality management system foundation to enable sustainable improvement",
                target_areas=["II-1", "I-4"],
                interventions=[
                    Intervention(criterion_id="II-1.1", target_score=4.0, effort_level="high", timeline_months=12),
                    Intervention(criterion_id="II-1.2", target_score=3.5, effort_level="medium", timeline_months=6),
                    Intervention(criterion_id="I-4.1", target_score=4.0, effort_level="medium", timeline_months=6),
                    Intervention(criterion_id="I-4.2", target_score=3.5, effort_level="medium", timeline_months=6),
                ],
                expected_improvement=0.35,
                effort_level="high",
                timeline_months=12,
                suitable_for=["below_good"],
            ),
            Scenario(
                id="care_process_improvement",
                name="Care Process Improvement",
                description="Enhance patient care processes from assessment to discharge",
                target_areas=["III-1", "III-2", "III-3", "III-4", "III-6"],
                interventions=[
                    Intervention(criterion_id="III-1.3", target_score=4.0, effort_level="medium", timeline_months=6),
                    Intervention(criterion_id="III-2.1", target_score=4.0, effort_level="medium", timeline_months=6),
                    Intervention(criterion_id="III-3.1", target_score=3.5, effort_level="medium", timeline_months=6),
                    Intervention(criterion_id="III-4.1", target_score=4.0, effort_level="medium", timeline_months=6),
                    Intervention(criterion_id="III-6.1", target_score=4.0, effort_level="medium", timeline_months=6),
                ],
                expected_improvement=0.3,
                effort_level="medium",
                timeline_months=6,
                suitable_for=["good_to_very_good", "very_good_to_excellent"],
            ),
            Scenario(
                id="outcome_excellence",
                name="Outcome Excellence",
                description="Focus on achieving excellent outcomes through measurement and data-driven improvement",
                target_areas=["IV-1", "IV-2", "I-4"],
                interventions=[
                    Intervention(criterion_id="IV-1.1", target_score=4.5, effort_level="high", timeline_months=12),
                    Intervention(criterion_id="IV-1.2", target_score=4.5, effort_level="high", timeline_months=12),
                    Intervention(criterion_id="IV-2.1", target_score=4.0, effort_level="medium", timeline_months=6),
                    Intervention(criterion_id="IV-2.2", target_score=4.0, effort_level="medium", timeline_months=6),
                    Intervention(criterion_id="I-4.1", target_score=4.5, effort_level="high", timeline_months=9),
                ],
                expected_improvement=0.25,
                effort_level="high",
                timeline_months=12,
                suitable_for=["very_good_to_excellent"],
            ),
            Scenario(
                id="quick_wins",
                name="Quick Wins Package",
                description="Low-effort improvements that can show rapid results",
                target_areas=["I-1", "II-5", "III-5"],
                interventions=[
                    Intervention(criterion_id="I-1.2", target_score=3.5, effort_level="low", timeline_months=3),
                    Intervention(criterion_id="II-5.1", target_score=3.5, effort_level="low", timeline_months=3),
                    Intervention(criterion_id="III-5.1", target_score=3.5, effort_level="low", timeline_months=3),
                    Intervention(criterion_id="I-3.2", target_score=3.5, effort_level="low", timeline_months=3),
                ],
                expected_improvement=0.15,
                effort_level="low",
                timeline_months=3,
                suitable_for=["all"],
            ),
        ]
    
    def get_scenarios(self, hospital_id: Optional[str] = None) -> List[Scenario]:
        """Get available scenarios, optionally filtered by hospital's current level."""
        scenarios = self._scenarios.copy()
        
        if hospital_id:
            latest = assessment_service.get_latest_by_hospital(hospital_id)
            if latest:
                score = latest.overall_maturity_score or 0
                
                # Determine current stage
                if score < 3.0:
                    stage = "below_good"
                elif score < 3.5:
                    stage = "good_to_very_good"
                else:
                    stage = "very_good_to_excellent"
                
                # Filter scenarios suitable for this stage
                scenarios = [
                    s for s in scenarios
                    if "all" in s.suitable_for or stage in s.suitable_for
                ]
        
        return scenarios
    
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get a specific scenario by ID."""
        for s in self._scenarios:
            if s.id == scenario_id:
                return s
        return None
    
    def run_simulation(
        self,
        hospital_id: str,
        interventions: List[Intervention],
        scenario_name: str = "Custom Simulation"
    ) -> SimulationResult:
        """Run a what-if simulation with the given interventions."""
        # Get current assessment
        latest = assessment_service.get_latest_by_hospital(hospital_id)
        if not latest:
            raise ValueError("No assessment found for hospital")
        
        # Build current score lookup
        current_scores = {cs.criterion_id: cs.score for cs in latest.criterion_scores}
        
        # Apply interventions and calculate cascade effects
        projected_scores = current_scores.copy()
        cascade_effects = []
        
        for intervention in interventions:
            # Set current score if not provided
            if intervention.current_score is None:
                intervention.current_score = current_scores.get(intervention.criterion_id, 2.5)
            
            # Apply direct intervention
            projected_scores[intervention.criterion_id] = intervention.target_score
            
            # Calculate cascade effects
            chapter_id = intervention.criterion_id.rsplit('.', 1)[0]
            cascades = self._calculate_cascade(
                chapter_id,
                intervention.target_score - intervention.current_score,
                current_scores,
                projected_scores,
                visited=set([chapter_id])
            )
            cascade_effects.extend(cascades)
        
        # Remove duplicates and keep highest confidence
        unique_cascades = {}
        for ce in cascade_effects:
            key = ce.criterion_id
            if key not in unique_cascades or ce.confidence > unique_cascades[key].confidence:
                unique_cascades[key] = ce
        cascade_effects = list(unique_cascades.values())
        
        # Apply cascade effects to projected scores
        for ce in cascade_effects:
            if ce.criterion_id in projected_scores:
                # Only apply if it improves the score
                if ce.projected_score > projected_scores[ce.criterion_id]:
                    projected_scores[ce.criterion_id] = ce.projected_score
        
        # Calculate part scores
        current_part_scores = self._calculate_part_scores(current_scores)
        projected_part_scores = self._calculate_part_scores(projected_scores)
        
        # Calculate overall scores
        current_overall = self._calculate_overall_score(current_part_scores)
        projected_overall = self._calculate_overall_score(projected_part_scores)
        
        # Calculate confidence interval
        base_variance = 0.15
        intervention_count = len(interventions)
        cascade_count = len(cascade_effects)
        
        # More interventions = more uncertainty
        uncertainty = base_variance + (intervention_count * 0.02) + (cascade_count * 0.01)
        
        confidence_interval = {
            "low": max(current_overall, projected_overall - uncertainty),
            "mid": projected_overall,
            "high": min(5.0, projected_overall + uncertainty * 0.5),
        }
        
        # Determine levels
        current_level = self._score_to_level(current_overall)
        projected_level = self._score_to_level(projected_overall)
        
        # Calculate timeline
        max_months = max([i.timeline_months for i in interventions], default=6)
        effort_counts = {"low": 0, "medium": 0, "high": 0}
        for i in interventions:
            effort_counts[i.effort_level] = effort_counts.get(i.effort_level, 0) + 1
        
        if effort_counts["high"] > effort_counts["medium"]:
            effort_summary = "High effort required - significant resource investment needed"
        elif effort_counts["medium"] > effort_counts["low"]:
            effort_summary = "Moderate effort required - sustained improvement activities"
        else:
            effort_summary = "Lower effort - achievable with focused attention"
        
        return SimulationResult(
            hospital_id=hospital_id,
            scenario_name=scenario_name,
            interventions=interventions,
            current_overall_score=round(current_overall, 2),
            projected_overall_score=round(projected_overall, 2),
            score_improvement=round(projected_overall - current_overall, 2),
            current_part_scores={k: round(v, 2) for k, v in current_part_scores.items()},
            projected_part_scores={k: round(v, 2) for k, v in projected_part_scores.items()},
            current_level=current_level,
            projected_level=projected_level,
            cascade_effects=cascade_effects,
            confidence_interval={k: round(v, 2) for k, v in confidence_interval.items()},
            estimated_months=max_months,
            effort_summary=effort_summary,
        )
    
    def _calculate_cascade(
        self,
        source_chapter: str,
        score_change: float,
        current_scores: Dict[str, float],
        projected_scores: Dict[str, float],
        visited: set,
        depth: int = 1,
        max_depth: int = 3
    ) -> List[CascadeEffect]:
        """Calculate cascade effects from improving a chapter."""
        if depth > max_depth:
            return []
        
        effects = []
        
        # Get outgoing relationships from this chapter
        if source_chapter in self._causal_strengths:
            for target_chapter, strength in self._causal_strengths[source_chapter].items():
                if target_chapter in visited:
                    continue
                
                # Calculate propagated effect (diminishes with strength and depth)
                propagated_change = score_change * strength * (0.7 ** (depth - 1))
                
                if abs(propagated_change) < 0.1:
                    continue
                
                # Get criteria in target chapter
                chapter = standards_service.get_chapter(target_chapter)
                if not chapter:
                    continue
                
                for criterion in chapter.criteria:
                    current = current_scores.get(criterion.id, 2.5)
                    projected = min(5.0, max(1.0, current + propagated_change))
                    
                    if projected > current:
                        effects.append(CascadeEffect(
                            criterion_id=criterion.id,
                            chapter_id=target_chapter,
                            chapter_name=chapter.name,
                            current_score=round(current, 2),
                            projected_score=round(projected, 2),
                            change=round(projected - current, 2),
                            path_length=depth,
                            confidence=round(strength * (0.8 ** depth), 2),
                        ))
                
                # Recurse to next level
                visited.add(target_chapter)
                deeper_effects = self._calculate_cascade(
                    target_chapter,
                    propagated_change,
                    current_scores,
                    projected_scores,
                    visited,
                    depth + 1,
                    max_depth
                )
                effects.extend(deeper_effects)
        
        return effects
    
    def _calculate_part_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate part scores from criterion scores."""
        parts = standards_service.get_parts()
        part_scores = {}
        
        for part in parts:
            chapter_total = 0.0
            chapter_weight_total = 0.0
            
            for chapter in part.chapters:
                criteria_scores = []
                for criterion in chapter.criteria:
                    if criterion.id in scores:
                        criteria_scores.append(scores[criterion.id])
                
                if criteria_scores:
                    chapter_avg = sum(criteria_scores) / len(criteria_scores)
                    chapter_total += chapter_avg * chapter.weight
                    chapter_weight_total += chapter.weight
            
            if chapter_weight_total > 0:
                part_scores[part.number] = chapter_total / chapter_weight_total
            else:
                part_scores[part.number] = 0.0
        
        return part_scores
    
    def _calculate_overall_score(self, part_scores: Dict[str, float]) -> float:
        """Calculate overall maturity score from part scores."""
        weights = {"I": 0.20, "II": 0.35, "III": 0.30, "IV": 0.15}
        total = 0.0
        for part, weight in weights.items():
            total += part_scores.get(part, 0) * weight
        return total
    
    def _score_to_level(self, score: float) -> str:
        """Convert score to accreditation level."""
        if score >= 4.0:
            return "excellent"
        if score >= 3.5:
            return "very_good"
        if score >= 3.0:
            return "good"
        if score >= 2.5:
            return "pass"
        return "not_accredited"
    
    def get_improvement_priorities(self, hospital_id: str, target_level: str = "next") -> List[Dict]:
        """Get prioritized list of criteria to improve for maximum impact."""
        latest = assessment_service.get_latest_by_hospital(hospital_id)
        if not latest:
            return []
        
        current_scores = {cs.criterion_id: cs.score for cs in latest.criterion_scores}
        current_overall = latest.overall_maturity_score or 0
        
        # Determine target score based on target_level
        if target_level == "next":
            if current_overall < 2.5:
                target_score = 2.5
            elif current_overall < 3.0:
                target_score = 3.0
            elif current_overall < 3.5:
                target_score = 3.5
            else:
                target_score = 4.0
        else:
            level_targets = {
                "pass": 2.5,
                "good": 3.0,
                "very_good": 3.5,
                "excellent": 4.0,
            }
            target_score = level_targets.get(target_level, 3.0)
        
        # Calculate impact of improving each criterion
        priorities = []
        all_criteria = standards_service.get_all_criteria()
        
        for criterion in all_criteria:
            current = current_scores.get(criterion.id, 2.5)
            
            # Skip already high-scoring criteria
            if current >= 4.0:
                continue
            
            # Calculate potential improvement
            potential_target = min(5.0, current + 1.0)
            
            # Simulate improvement
            test_scores = current_scores.copy()
            test_scores[criterion.id] = potential_target
            test_part_scores = self._calculate_part_scores(test_scores)
            test_overall = self._calculate_overall_score(test_part_scores)
            
            impact = test_overall - current_overall
            
            # Weight by category
            category_weight = 1.0
            if criterion.category == CriterionCategory.ESSENTIAL:
                category_weight = 1.5
            elif criterion.category == CriterionCategory.CORE:
                category_weight = 1.25
            
            # Count downstream effects
            chapter_id = criterion.id.rsplit('.', 1)[0]
            downstream_count = len(self._causal_strengths.get(chapter_id, {}))
            
            priorities.append({
                "criterion_id": criterion.id,
                "criterion_name": criterion.name,
                "category": criterion.category.value,
                "current_score": round(current, 1),
                "recommended_target": round(potential_target, 1),
                "impact_score": round(impact * category_weight, 3),
                "downstream_effects": downstream_count,
                "effort_estimate": "high" if criterion.category == CriterionCategory.ESSENTIAL else "medium",
            })
        
        # Sort by impact
        priorities.sort(key=lambda x: x["impact_score"], reverse=True)
        
        return priorities[:20]


# Singleton instance
simulation_service = SimulationService()


