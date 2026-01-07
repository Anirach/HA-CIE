"""
Assessment Service - CRUD operations for assessments.
Uses JSON file storage for development mode.
"""
import json
import random
from datetime import datetime, date
from typing import List, Optional, Dict, Tuple
from pathlib import Path

from app.models.assessment import (
    Assessment, CriterionScore, AccreditationLevel,
    ChapterScore, PartScore
)
from app.services.standards_service import standards_service
from app.core.config import settings


class AssessmentService:
    """Service for managing assessment data."""
    
    def __init__(self):
        self._data_dir = Path(settings.data_dir)
        self._assessments_file = self._data_dir / "assessments.json"
        self._ensure_data_dir()
        self._assessments: Dict[str, Assessment] = {}
        self._load_assessments()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists."""
        self._data_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_assessments(self):
        """Load assessments from JSON file."""
        if self._assessments_file.exists():
            try:
                with open(self._assessments_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for a_data in data:
                        # Convert date strings back to date objects
                        if 'assessment_date' in a_data and isinstance(a_data['assessment_date'], str):
                            a_data['assessment_date'] = date.fromisoformat(a_data['assessment_date'])
                        assessment = Assessment(**a_data)
                        self._assessments[assessment.id] = assessment
            except Exception as e:
                print(f"Error loading assessments: {e}")
                self._assessments = {}
        
        # Initialize with sample data if empty
        if not self._assessments:
            self._init_sample_data()
    
    def _save_assessments(self):
        """Save assessments to JSON file."""
        data = [a.model_dump() for a in self._assessments.values()]
        with open(self._assessments_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
    
    def _generate_sample_scores(self, base_score: float, variation: float = 0.5) -> List[CriterionScore]:
        """Generate sample criterion scores for demo data."""
        scores = []
        criteria = standards_service.get_all_criteria()
        
        for criterion in criteria:
            # Generate score with some variation
            score = base_score + random.uniform(-variation, variation)
            score = max(1.0, min(5.0, score))  # Clamp between 1 and 5
            
            # Essential criteria tend to have higher priority/scores
            if criterion.category.value == "essential":
                score = min(5.0, score + 0.2)
            
            scores.append(CriterionScore(
                criterion_id=criterion.id,
                score=round(score, 1),
                notes=None,
            ))
        
        return scores
    
    def _init_sample_data(self):
        """Initialize with sample assessment data."""
        # Hospital 1: 3 assessment cycles showing improvement
        assessments_h1 = [
            Assessment(
                id="assess-001-2022",
                hospital_id="hosp-001",
                assessment_date=date(2022, 6, 15),
                assessment_cycle="2022-Annual",
                assessment_type="self",
                criterion_scores=self._generate_sample_scores(2.8, 0.4),
                is_draft=False,
                is_submitted=True,
            ),
            Assessment(
                id="assess-001-2023",
                hospital_id="hosp-001",
                assessment_date=date(2023, 6, 20),
                assessment_cycle="2023-Annual",
                assessment_type="self",
                criterion_scores=self._generate_sample_scores(3.1, 0.4),
                is_draft=False,
                is_submitted=True,
            ),
            Assessment(
                id="assess-001-2024",
                hospital_id="hosp-001",
                assessment_date=date(2024, 6, 18),
                assessment_cycle="2024-Annual",
                assessment_type="self",
                criterion_scores=self._generate_sample_scores(3.4, 0.3),
                is_draft=False,
                is_submitted=True,
            ),
        ]
        
        # Hospital 2: 2 assessment cycles
        assessments_h2 = [
            Assessment(
                id="assess-002-2023",
                hospital_id="hosp-002",
                assessment_date=date(2023, 9, 10),
                assessment_cycle="2023-Annual",
                assessment_type="self",
                criterion_scores=self._generate_sample_scores(2.6, 0.5),
                is_draft=False,
                is_submitted=True,
            ),
            Assessment(
                id="assess-002-2024",
                hospital_id="hosp-002",
                assessment_date=date(2024, 9, 12),
                assessment_cycle="2024-Annual",
                assessment_type="self",
                criterion_scores=self._generate_sample_scores(3.0, 0.4),
                is_draft=False,
                is_submitted=True,
            ),
        ]
        
        # Hospital 3: High performing
        assessments_h3 = [
            Assessment(
                id="assess-003-2024",
                hospital_id="hosp-003",
                assessment_date=date(2024, 3, 25),
                assessment_cycle="2024-Annual",
                assessment_type="external",
                criterion_scores=self._generate_sample_scores(4.2, 0.3),
                is_draft=False,
                is_submitted=True,
            ),
        ]
        
        all_assessments = assessments_h1 + assessments_h2 + assessments_h3
        
        for assessment in all_assessments:
            # Calculate scores
            self._calculate_assessment_scores(assessment)
            self._assessments[assessment.id] = assessment
        
        self._save_assessments()
    
    def _calculate_assessment_scores(self, assessment: Assessment) -> None:
        """Calculate part scores and overall maturity score."""
        # Build lookup of criterion scores
        score_lookup = {cs.criterion_id: cs.score for cs in assessment.criterion_scores}
        
        parts = standards_service.get_parts()
        part_weights = {"I": 0.20, "II": 0.35, "III": 0.30, "IV": 0.15}
        
        total_weighted = 0.0
        
        for part in parts:
            chapter_total = 0.0
            chapter_weight_total = 0.0
            
            for chapter in part.chapters:
                criteria_scores = []
                for criterion in chapter.criteria:
                    if criterion.id in score_lookup:
                        criteria_scores.append(score_lookup[criterion.id])
                
                if criteria_scores:
                    chapter_avg = sum(criteria_scores) / len(criteria_scores)
                    chapter_total += chapter_avg * chapter.weight
                    chapter_weight_total += chapter.weight
            
            if chapter_weight_total > 0:
                part_score = chapter_total / chapter_weight_total
                assessment.part_scores[part.number] = round(part_score, 2)
                total_weighted += part_score * part_weights.get(part.number, 0.25)
        
        # Calculate overall score
        assessment.overall_maturity_score = round(total_weighted, 2)
        
        # Determine accreditation level
        score = assessment.overall_maturity_score
        if score >= 4.0:
            assessment.accreditation_level = AccreditationLevel.EXCELLENT
        elif score >= 3.5:
            assessment.accreditation_level = AccreditationLevel.VERY_GOOD
        elif score >= 3.0:
            assessment.accreditation_level = AccreditationLevel.GOOD
        elif score >= 2.5:
            assessment.accreditation_level = AccreditationLevel.PASS
        else:
            assessment.accreditation_level = AccreditationLevel.NOT_ACCREDITED
        
        # Calculate data completeness
        total_criteria = len(standards_service.get_all_criteria())
        assessed_criteria = len(assessment.criterion_scores)
        assessment.data_completeness = round(assessed_criteria / total_criteria * 100, 1) if total_criteria > 0 else 0
    
    def get_all(self) -> List[Assessment]:
        """Get all assessments."""
        return list(self._assessments.values())
    
    def get_by_id(self, assessment_id: str) -> Optional[Assessment]:
        """Get assessment by ID."""
        return self._assessments.get(assessment_id)
    
    def get_by_hospital(self, hospital_id: str) -> List[Assessment]:
        """Get all assessments for a hospital, sorted by date."""
        assessments = [a for a in self._assessments.values() if a.hospital_id == hospital_id]
        return sorted(assessments, key=lambda a: a.assessment_date)
    
    def get_latest_by_hospital(self, hospital_id: str) -> Optional[Assessment]:
        """Get the latest assessment for a hospital."""
        assessments = self.get_by_hospital(hospital_id)
        return assessments[-1] if assessments else None
    
    def create(self, assessment: Assessment) -> Assessment:
        """Create a new assessment."""
        assessment.created_at = datetime.utcnow()
        assessment.updated_at = datetime.utcnow()
        self._calculate_assessment_scores(assessment)
        self._assessments[assessment.id] = assessment
        self._save_assessments()
        return assessment
    
    def update(self, assessment_id: str, updates: dict) -> Optional[Assessment]:
        """Update an assessment."""
        assessment = self._assessments.get(assessment_id)
        if not assessment:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(assessment, key) and key not in ['id', 'created_at']:
                setattr(assessment, key, value)
        
        assessment.updated_at = datetime.utcnow()
        
        # Recalculate scores if criterion_scores changed
        if 'criterion_scores' in updates:
            self._calculate_assessment_scores(assessment)
        
        self._assessments[assessment_id] = assessment
        self._save_assessments()
        return assessment
    
    def delete(self, assessment_id: str) -> bool:
        """Delete an assessment."""
        if assessment_id in self._assessments:
            del self._assessments[assessment_id]
            self._save_assessments()
            return True
        return False
    
    def delete_by_hospital(self, hospital_id: str) -> int:
        """Delete all assessments for a hospital. Returns count deleted."""
        to_delete = [a.id for a in self._assessments.values() if a.hospital_id == hospital_id]
        for aid in to_delete:
            del self._assessments[aid]
        if to_delete:
            self._save_assessments()
        return len(to_delete)
    
    def get_trends(self, hospital_id: str) -> Dict:
        """Get score trends across assessments for a hospital."""
        assessments = self.get_by_hospital(hospital_id)
        
        if not assessments:
            return {"assessments": [], "trends": {}}
        
        # Build trend data
        trends = {
            "overall": [],
            "part_I": [],
            "part_II": [],
            "part_III": [],
            "part_IV": [],
        }
        
        assessment_summaries = []
        
        for a in assessments:
            assessment_summaries.append({
                "id": a.id,
                "date": a.assessment_date.isoformat(),
                "cycle": a.assessment_cycle,
                "overall_score": a.overall_maturity_score,
                "level": a.accreditation_level.value,
                "part_scores": a.part_scores,
            })
            
            trends["overall"].append({
                "date": a.assessment_date.isoformat(),
                "value": a.overall_maturity_score,
            })
            
            for part_num in ["I", "II", "III", "IV"]:
                if part_num in a.part_scores:
                    trends[f"part_{part_num}"].append({
                        "date": a.assessment_date.isoformat(),
                        "value": a.part_scores[part_num],
                    })
        
        # Calculate improvement
        improvement = None
        if len(assessments) >= 2:
            first_score = assessments[0].overall_maturity_score or 0
            last_score = assessments[-1].overall_maturity_score or 0
            improvement = round(last_score - first_score, 2)
        
        return {
            "assessments": assessment_summaries,
            "trends": trends,
            "improvement": improvement,
            "assessment_count": len(assessments),
        }
    
    def get_chapter_scores(self, assessment_id: str) -> List[ChapterScore]:
        """Get detailed chapter scores for an assessment."""
        assessment = self._assessments.get(assessment_id)
        if not assessment:
            return []
        
        score_lookup = {cs.criterion_id: cs for cs in assessment.criterion_scores}
        chapter_scores = []
        
        for chapter in standards_service.get_all_chapters():
            criteria_scores = []
            for criterion in chapter.criteria:
                if criterion.id in score_lookup:
                    criteria_scores.append(score_lookup[criterion.id])
            
            if criteria_scores:
                avg_score = sum(cs.score for cs in criteria_scores) / len(criteria_scores)
            else:
                avg_score = 0.0
            
            chapter_scores.append(ChapterScore(
                chapter_id=chapter.id,
                score=round(avg_score, 2),
                criteria_scores=criteria_scores,
                criteria_count=len(chapter.criteria),
                criteria_assessed=len(criteria_scores),
            ))
        
        return chapter_scores
    
    def compare_assessments(self, assessment_id_1: str, assessment_id_2: str) -> Dict:
        """Compare two assessments and return differences."""
        a1 = self._assessments.get(assessment_id_1)
        a2 = self._assessments.get(assessment_id_2)
        
        if not a1 or not a2:
            return {"error": "Assessment not found"}
        
        # Compare overall scores
        overall_diff = (a2.overall_maturity_score or 0) - (a1.overall_maturity_score or 0)
        
        # Compare part scores
        part_diffs = {}
        for part in ["I", "II", "III", "IV"]:
            score1 = a1.part_scores.get(part, 0)
            score2 = a2.part_scores.get(part, 0)
            part_diffs[part] = round(score2 - score1, 2)
        
        # Find improved and regressed criteria
        score_lookup_1 = {cs.criterion_id: cs.score for cs in a1.criterion_scores}
        score_lookup_2 = {cs.criterion_id: cs.score for cs in a2.criterion_scores}
        
        improved = []
        regressed = []
        
        all_criteria_ids = set(score_lookup_1.keys()) | set(score_lookup_2.keys())
        for cid in all_criteria_ids:
            s1 = score_lookup_1.get(cid, 0)
            s2 = score_lookup_2.get(cid, 0)
            diff = s2 - s1
            
            if diff >= 0.5:
                improved.append({"criterion_id": cid, "change": round(diff, 1)})
            elif diff <= -0.5:
                regressed.append({"criterion_id": cid, "change": round(diff, 1)})
        
        # Sort by magnitude of change
        improved.sort(key=lambda x: x["change"], reverse=True)
        regressed.sort(key=lambda x: x["change"])
        
        return {
            "assessment_1": {
                "id": a1.id,
                "date": a1.assessment_date.isoformat(),
                "overall_score": a1.overall_maturity_score,
                "level": a1.accreditation_level.value,
            },
            "assessment_2": {
                "id": a2.id,
                "date": a2.assessment_date.isoformat(),
                "overall_score": a2.overall_maturity_score,
                "level": a2.accreditation_level.value,
            },
            "overall_change": round(overall_diff, 2),
            "part_changes": part_diffs,
            "improved_criteria": improved[:10],  # Top 10
            "regressed_criteria": regressed[:10],  # Top 10
        }


# Singleton instance
assessment_service = AssessmentService()


def get_assessment_service() -> AssessmentService:
    """Get the assessment service singleton instance."""
    return assessment_service

