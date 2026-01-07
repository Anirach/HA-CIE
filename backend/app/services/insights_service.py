"""
AI Insights Service for generating analytical insights and recommendations.
Analyzes assessment data to provide actionable insights for quality improvement.
"""

from datetime import datetime, date
from typing import Optional, List
import random

from app.services.standards_service import StandardsService, get_standards_service
from app.services.assessment_service import AssessmentService, get_assessment_service


class InsightCategory:
    """Categories of insights."""
    GAP_ANALYSIS = "gap_analysis"
    TREND_ANALYSIS = "trend_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    RECOMMENDATION = "recommendation"
    ROOT_CAUSE = "root_cause"
    BENCHMARK = "benchmark"


class InsightPriority:
    """Priority levels for insights."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class InsightsService:
    """Service for generating AI-powered insights."""
    
    def __init__(self):
        self.standards_service = get_standards_service()
        self.assessment_service = get_assessment_service()
    
    def generate_insights(self, hospital_id: str) -> dict:
        """Generate comprehensive insights for a hospital."""
        # Get latest assessment
        assessments = self.assessment_service.get_by_hospital(hospital_id)
        if not assessments:
            return {
                "hospital_id": hospital_id,
                "generated_at": datetime.now().isoformat(),
                "insights": [],
                "summary": {"total": 0, "by_category": {}, "by_priority": {}},
                "recommendations": [],
                "risk_score": 0,
            }
        
        latest = assessments[-1]
        insights = []
        
        # Generate gap analysis insights
        gap_insights = self._generate_gap_insights(latest)
        insights.extend(gap_insights)
        
        # Generate trend insights
        if len(assessments) > 1:
            trend_insights = self._generate_trend_insights(assessments)
            insights.extend(trend_insights)
        
        # Generate risk assessment
        risk_insights = self._generate_risk_insights(latest)
        insights.extend(risk_insights)
        
        # Generate root cause insights
        root_cause_insights = self._generate_root_cause_insights(latest)
        insights.extend(root_cause_insights)
        
        # Generate benchmark insights
        benchmark_insights = self._generate_benchmark_insights(latest)
        insights.extend(benchmark_insights)
        
        # Generate prioritized recommendations
        recommendations = self._generate_recommendations(insights, latest)
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(latest)
        
        # Build summary
        summary = self._build_summary(insights)
        
        return {
            "hospital_id": hospital_id,
            "generated_at": datetime.now().isoformat(),
            "assessment_date": latest.assessment_date.isoformat() if latest.assessment_date else None,
            "overall_score": latest.overall_maturity_score,
            "insights": [self._insight_to_dict(i) for i in insights],
            "summary": summary,
            "recommendations": recommendations,
            "risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score),
        }
    
    def _generate_gap_insights(self, assessment) -> list:
        """Generate insights about compliance gaps."""
        insights = []
        
        # Get criteria with low scores
        low_scores = [
            cs for cs in assessment.criterion_scores
            if cs.score < 3.0
        ]
        
        # Group by category
        essential_gaps = [cs for cs in low_scores if self._get_criterion_category(cs.criterion_id) == "essential"]
        core_gaps = [cs for cs in low_scores if self._get_criterion_category(cs.criterion_id) == "core"]
        
        if essential_gaps:
            insights.append({
                "id": f"gap-essential-{len(essential_gaps)}",
                "category": InsightCategory.GAP_ANALYSIS,
                "priority": InsightPriority.CRITICAL,
                "title": f"{len(essential_gaps)} Essential Safety Criteria Below Target",
                "description": f"There are {len(essential_gaps)} essential safety criteria with scores below 3.0. These must be addressed immediately as they directly impact patient safety.",
                "affected_criteria": [cs.criterion_id for cs in essential_gaps[:5]],
                "metric": {
                    "name": "Essential Gaps",
                    "value": len(essential_gaps),
                    "trend": "critical",
                },
                "action_items": [
                    "Conduct immediate safety audit for affected areas",
                    "Implement temporary risk mitigation measures",
                    "Schedule urgent improvement initiatives",
                ],
            })
        
        if core_gaps:
            insights.append({
                "id": f"gap-core-{len(core_gaps)}",
                "category": InsightCategory.GAP_ANALYSIS,
                "priority": InsightPriority.HIGH,
                "title": f"{len(core_gaps)} Core Sustainability Criteria Need Attention",
                "description": f"There are {len(core_gaps)} core criteria scoring below 3.0. These affect long-term sustainability and should be prioritized in the improvement plan.",
                "affected_criteria": [cs.criterion_id for cs in core_gaps[:5]],
                "metric": {
                    "name": "Core Gaps",
                    "value": len(core_gaps),
                    "trend": "warning",
                },
                "action_items": [
                    "Review current processes for sustainability",
                    "Develop improvement roadmap with milestones",
                    "Allocate resources for systematic improvement",
                ],
            })
        
        # Domain-specific gaps
        chapters = self.standards_service.get_all_chapters()
        for chapter in chapters:
            chapter_scores = [
                cs for cs in assessment.criterion_scores
                if cs.criterion_id.startswith(chapter.id)
            ]
            if chapter_scores:
                avg_score = sum(cs.score for cs in chapter_scores) / len(chapter_scores)
                if avg_score < 2.5:
                    insights.append({
                        "id": f"gap-chapter-{chapter.id}",
                        "category": InsightCategory.GAP_ANALYSIS,
                        "priority": InsightPriority.HIGH,
                        "title": f"Significant Gap in {chapter.name}",
                        "description": f"Chapter {chapter.id} ({chapter.name}) has an average score of {avg_score:.2f}, significantly below the target threshold.",
                        "affected_criteria": [cs.criterion_id for cs in chapter_scores if cs.score < 3.0][:3],
                        "metric": {
                            "name": f"{chapter.id} Score",
                            "value": round(avg_score, 2),
                            "trend": "declining",
                        },
                        "action_items": [
                            f"Focus improvement efforts on {chapter.name}",
                            "Assign dedicated team for chapter improvement",
                            "Review best practices from high-performing hospitals",
                        ],
                    })
        
        return insights
    
    def _generate_trend_insights(self, assessments: list) -> list:
        """Generate insights about score trends over time."""
        insights = []
        
        if len(assessments) < 2:
            return insights
        
        # Overall trend
        scores = [a.overall_maturity_score for a in assessments]
        recent_change = scores[-1] - scores[-2]
        total_change = scores[-1] - scores[0]
        
        if recent_change < -0.2:
            insights.append({
                "id": "trend-declining",
                "category": InsightCategory.TREND_ANALYSIS,
                "priority": InsightPriority.HIGH,
                "title": "Recent Score Decline Detected",
                "description": f"The overall maturity score has declined by {abs(recent_change):.2f} points since the previous assessment. This trend requires immediate attention.",
                "metric": {
                    "name": "Score Change",
                    "value": round(recent_change, 2),
                    "trend": "declining",
                },
                "action_items": [
                    "Investigate root causes of decline",
                    "Review recent organizational changes",
                    "Implement corrective actions immediately",
                ],
            })
        elif recent_change > 0.3:
            insights.append({
                "id": "trend-improving",
                "category": InsightCategory.TREND_ANALYSIS,
                "priority": InsightPriority.LOW,
                "title": "Strong Improvement Momentum",
                "description": f"Excellent progress! The overall score improved by {recent_change:.2f} points. Continue current improvement strategies.",
                "metric": {
                    "name": "Score Change",
                    "value": round(recent_change, 2),
                    "trend": "improving",
                },
                "action_items": [
                    "Document successful improvement strategies",
                    "Share learnings across departments",
                    "Set higher targets for next assessment",
                ],
            })
        
        # Velocity analysis
        if len(assessments) >= 3:
            velocities = [scores[i] - scores[i-1] for i in range(1, len(scores))]
            avg_velocity = sum(velocities) / len(velocities)
            
            if avg_velocity > 0.2:
                months_to_target = max(0, (4.0 - scores[-1]) / avg_velocity * 3)  # Assuming quarterly assessments
                insights.append({
                    "id": "trend-projection",
                    "category": InsightCategory.TREND_ANALYSIS,
                    "priority": InsightPriority.MEDIUM,
                    "title": "Projected Target Achievement",
                    "description": f"At the current improvement rate of {avg_velocity:.2f} points per assessment, you are projected to reach Advanced HA level in approximately {int(months_to_target)} months.",
                    "metric": {
                        "name": "Months to Target",
                        "value": int(months_to_target),
                        "trend": "improving",
                    },
                })
        
        return insights
    
    def _generate_risk_insights(self, assessment) -> list:
        """Generate risk assessment insights."""
        insights = []
        
        # Identify high-risk areas
        score_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for cs in assessment.criterion_scores:
            if cs.score < 2.0:
                score_counts["critical"] += 1
            elif cs.score < 2.5:
                score_counts["high"] += 1
            elif cs.score < 3.0:
                score_counts["medium"] += 1
            else:
                score_counts["low"] += 1
        
        if score_counts["critical"] > 0:
            insights.append({
                "id": "risk-critical",
                "category": InsightCategory.RISK_ASSESSMENT,
                "priority": InsightPriority.CRITICAL,
                "title": f"{score_counts['critical']} Criteria at Critical Risk Level",
                "description": "These criteria have scores below 2.0 and pose immediate compliance risks. Urgent intervention is required.",
                "metric": {
                    "name": "Critical Risk Count",
                    "value": score_counts["critical"],
                    "trend": "critical",
                },
                "action_items": [
                    "Escalate to leadership immediately",
                    "Implement emergency improvement measures",
                    "Consider engaging external consultants",
                ],
            })
        
        # Accreditation risk
        if assessment.overall_maturity_score < 3.0:
            insights.append({
                "id": "risk-accreditation",
                "category": InsightCategory.RISK_ASSESSMENT,
                "priority": InsightPriority.CRITICAL,
                "title": "Accreditation Status at Risk",
                "description": f"Current overall score of {assessment.overall_maturity_score:.2f} is below the minimum threshold for HA accreditation (3.0).",
                "metric": {
                    "name": "Gap to Threshold",
                    "value": round(3.0 - assessment.overall_maturity_score, 2),
                    "trend": "critical",
                },
                "action_items": [
                    "Develop intensive improvement plan",
                    "Prioritize essential and core criteria",
                    "Request additional resources if needed",
                ],
            })
        
        return insights
    
    def _generate_root_cause_insights(self, assessment) -> list:
        """Generate root cause analysis insights using causal relationships."""
        insights = []
        
        relationships = self.standards_service.get_causal_relationships()
        
        # Find chapters with low scores that might be root causes
        chapter_scores = {}
        chapters = self.standards_service.get_all_chapters()
        
        for chapter in chapters:
            chapter_criteria = [
                cs for cs in assessment.criterion_scores
                if cs.criterion_id.startswith(chapter.id)
            ]
            if chapter_criteria:
                chapter_scores[chapter.id] = sum(cs.score for cs in chapter_criteria) / len(chapter_criteria)
        
        # Identify potential root causes (low-scoring chapters that influence many others)
        influence_count = {}
        for rel in relationships:
            if rel.source not in influence_count:
                influence_count[rel.source] = 0
            influence_count[rel.source] += 1
        
        # Find high-influence, low-score chapters
        root_causes = []
        for chapter_id, score in chapter_scores.items():
            if score < 3.0 and influence_count.get(chapter_id, 0) >= 2:
                root_causes.append({
                    "chapter_id": chapter_id,
                    "score": score,
                    "influence": influence_count.get(chapter_id, 0),
                })
        
        if root_causes:
            root_causes.sort(key=lambda x: (-x["influence"], x["score"]))
            top_cause = root_causes[0]
            chapter = self.standards_service.get_chapter(top_cause["chapter_id"])
            
            insights.append({
                "id": f"root-cause-{top_cause['chapter_id']}",
                "category": InsightCategory.ROOT_CAUSE,
                "priority": InsightPriority.HIGH,
                "title": f"Root Cause Identified: {chapter.name if chapter else top_cause['chapter_id']}",
                "description": f"Analysis suggests {chapter.name if chapter else top_cause['chapter_id']} (score: {top_cause['score']:.2f}) may be a root cause affecting {top_cause['influence']} other areas through causal dependencies.",
                "affected_areas": [
                    rel.target for rel in relationships
                    if rel.source == top_cause["chapter_id"]
                ][:5],
                "metric": {
                    "name": "Downstream Impact",
                    "value": top_cause["influence"],
                    "trend": "causal",
                },
                "action_items": [
                    f"Prioritize improvement in {chapter.name if chapter else top_cause['chapter_id']}",
                    "Addressing this area may improve multiple downstream metrics",
                    "Consider this a high-leverage improvement opportunity",
                ],
            })
        
        return insights
    
    def _generate_benchmark_insights(self, assessment) -> list:
        """Generate benchmark comparison insights."""
        insights = []
        
        # Simulated benchmark data (in production, would come from aggregate data)
        national_avg = 3.2
        top_quartile = 3.8
        
        if assessment.overall_maturity_score >= top_quartile:
            insights.append({
                "id": "benchmark-top",
                "category": InsightCategory.BENCHMARK,
                "priority": InsightPriority.LOW,
                "title": "Top Quartile Performance",
                "description": f"Your score of {assessment.overall_maturity_score:.2f} places you in the top 25% of hospitals nationally. Excellent work!",
                "metric": {
                    "name": "Percentile",
                    "value": 90,
                    "trend": "excellent",
                },
                "action_items": [
                    "Share best practices with peer hospitals",
                    "Consider pursuing Advanced HA recognition",
                    "Focus on innovation and continuous improvement",
                ],
            })
        elif assessment.overall_maturity_score < national_avg:
            gap = national_avg - assessment.overall_maturity_score
            insights.append({
                "id": "benchmark-below",
                "category": InsightCategory.BENCHMARK,
                "priority": InsightPriority.MEDIUM,
                "title": "Below National Average",
                "description": f"Your score is {gap:.2f} points below the national average of {national_avg}. There is significant room for improvement.",
                "metric": {
                    "name": "Gap to Average",
                    "value": round(gap, 2),
                    "trend": "below_average",
                },
                "action_items": [
                    "Study improvement strategies from higher-performing hospitals",
                    "Consider peer learning programs",
                    "Request benchmark reports for specific areas",
                ],
            })
        
        return insights
    
    def _generate_recommendations(self, insights: list, assessment) -> list:
        """Generate prioritized recommendations based on insights."""
        recommendations = []
        
        # Extract action items from critical and high priority insights
        priority_insights = [i for i in insights if i.get("priority") in [InsightPriority.CRITICAL, InsightPriority.HIGH]]
        
        for i, insight in enumerate(priority_insights[:5]):
            actions = insight.get("action_items", [])
            if actions:
                recommendations.append({
                    "rank": i + 1,
                    "title": insight.get("title", "Improvement Recommendation"),
                    "description": actions[0] if actions else "",
                    "priority": insight.get("priority", InsightPriority.MEDIUM),
                    "category": insight.get("category", InsightCategory.RECOMMENDATION),
                    "estimated_impact": self._estimate_impact(insight),
                    "estimated_effort": self._estimate_effort(insight),
                    "related_insight_id": insight.get("id"),
                })
        
        # Add standard recommendations if not enough from insights
        if len(recommendations) < 5:
            standard_recs = [
                {
                    "title": "Establish QI Committee Review Cycle",
                    "description": "Implement monthly QI committee reviews to track progress on improvement initiatives.",
                    "priority": InsightPriority.MEDIUM,
                    "category": InsightCategory.RECOMMENDATION,
                    "estimated_impact": "medium",
                    "estimated_effort": "low",
                },
                {
                    "title": "Staff Training Program",
                    "description": "Develop comprehensive training program for staff on accreditation standards.",
                    "priority": InsightPriority.MEDIUM,
                    "category": InsightCategory.RECOMMENDATION,
                    "estimated_impact": "high",
                    "estimated_effort": "medium",
                },
            ]
            for rec in standard_recs:
                if len(recommendations) >= 5:
                    break
                rec["rank"] = len(recommendations) + 1
                recommendations.append(rec)
        
        return recommendations
    
    def _calculate_risk_score(self, assessment) -> int:
        """Calculate overall risk score (0-100)."""
        risk_score = 0
        
        # Score-based risk (40 points max)
        if assessment.overall_maturity_score < 2.0:
            risk_score += 40
        elif assessment.overall_maturity_score < 2.5:
            risk_score += 30
        elif assessment.overall_maturity_score < 3.0:
            risk_score += 20
        elif assessment.overall_maturity_score < 3.5:
            risk_score += 10
        
        # Essential criteria risk (30 points max)
        essential_gaps = sum(
            1 for cs in assessment.criterion_scores
            if cs.score < 3.0 and self._get_criterion_category(cs.criterion_id) == "essential"
        )
        risk_score += min(30, essential_gaps * 5)
        
        # Critical score risk (30 points max)
        critical_scores = sum(1 for cs in assessment.criterion_scores if cs.score < 2.0)
        risk_score += min(30, critical_scores * 3)
        
        return min(100, risk_score)
    
    def _get_risk_level(self, risk_score: int) -> str:
        """Get risk level label from score."""
        if risk_score >= 70:
            return "critical"
        elif risk_score >= 50:
            return "high"
        elif risk_score >= 30:
            return "medium"
        return "low"
    
    def _get_criterion_category(self, criterion_id: str) -> str:
        """Get the category of a criterion."""
        # Parse criterion ID to get chapter
        parts = criterion_id.split("-")
        if len(parts) >= 2:
            chapter_id = f"{parts[0]}-{parts[1]}"
            chapter = self.standards_service.get_chapter(chapter_id)
            if chapter:
                for criterion in chapter.criteria:
                    if criterion.id == criterion_id:
                        return criterion.category.value
        return "basic"
    
    def _estimate_impact(self, insight: dict) -> str:
        """Estimate impact level of addressing an insight."""
        priority = insight.get("priority", "")
        if priority == InsightPriority.CRITICAL:
            return "very_high"
        elif priority == InsightPriority.HIGH:
            return "high"
        elif priority == InsightPriority.MEDIUM:
            return "medium"
        return "low"
    
    def _estimate_effort(self, insight: dict) -> str:
        """Estimate effort required to address an insight."""
        category = insight.get("category", "")
        if category == InsightCategory.ROOT_CAUSE:
            return "high"
        elif category == InsightCategory.GAP_ANALYSIS:
            return "medium"
        return "low"
    
    def _insight_to_dict(self, insight: dict) -> dict:
        """Convert insight to dictionary format."""
        return insight
    
    def _build_summary(self, insights: list) -> dict:
        """Build summary statistics for insights."""
        by_category = {}
        by_priority = {}
        
        for insight in insights:
            cat = insight.get("category", "other")
            pri = insight.get("priority", "medium")
            
            by_category[cat] = by_category.get(cat, 0) + 1
            by_priority[pri] = by_priority.get(pri, 0) + 1
        
        return {
            "total": len(insights),
            "by_category": by_category,
            "by_priority": by_priority,
        }
    
    def get_insight_categories(self) -> list:
        """Get available insight categories."""
        return [
            {"id": InsightCategory.GAP_ANALYSIS, "name": "Gap Analysis", "icon": "target"},
            {"id": InsightCategory.TREND_ANALYSIS, "name": "Trend Analysis", "icon": "trending-up"},
            {"id": InsightCategory.RISK_ASSESSMENT, "name": "Risk Assessment", "icon": "alert-triangle"},
            {"id": InsightCategory.ROOT_CAUSE, "name": "Root Cause Analysis", "icon": "git-branch"},
            {"id": InsightCategory.BENCHMARK, "name": "Benchmarking", "icon": "bar-chart"},
            {"id": InsightCategory.RECOMMENDATION, "name": "Recommendations", "icon": "lightbulb"},
        ]


# Global instance
_insights_service: Optional[InsightsService] = None


def get_insights_service() -> InsightsService:
    """Get or create the insights service instance."""
    global _insights_service
    if _insights_service is None:
        _insights_service = InsightsService()
    return _insights_service

