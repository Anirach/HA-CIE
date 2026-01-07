"""Assessment data model."""
from datetime import datetime, date
from typing import Optional, List, Dict
from enum import Enum
from pydantic import BaseModel, Field, computed_field
import uuid


class AccreditationLevel(str, Enum):
    """Accreditation levels based on HA Thailand standards."""
    NOT_ACCREDITED = "not_accredited"
    PASS = "pass"              # Score 2.5-2.9
    GOOD = "good"              # Score 3.0-3.4
    VERY_GOOD = "very_good"    # Score 3.5-3.9
    EXCELLENT = "excellent"    # Score 4.0+


class CriterionScore(BaseModel):
    """Score for a single criterion."""
    criterion_id: str
    score: float = Field(ge=0, le=5)  # HA Thailand uses 1-5 scale
    notes: Optional[str] = None
    evidence: Optional[str] = None
    assessed_by: Optional[str] = None
    assessed_at: Optional[datetime] = None


class ChapterScore(BaseModel):
    """Aggregated score for a chapter."""
    chapter_id: str
    score: float
    criteria_scores: List[CriterionScore] = []
    criteria_count: int = 0
    criteria_assessed: int = 0


class PartScore(BaseModel):
    """Aggregated score for a part."""
    part_number: str
    score: float
    weight: float
    weighted_score: float
    chapter_scores: List[ChapterScore] = []


class Assessment(BaseModel):
    """Assessment model representing a single assessment cycle."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hospital_id: str
    
    # Assessment metadata
    assessment_date: date
    assessment_cycle: str  # e.g., "2024-Q1", "2024-Annual"
    assessment_type: str = "self"  # self, internal, external, survey
    assessor_name: Optional[str] = None
    assessor_organization: Optional[str] = None
    
    # Scores
    criterion_scores: List[CriterionScore] = []
    
    # Calculated scores (stored for quick access)
    part_scores: Dict[str, float] = {}  # {"I": 3.2, "II": 3.5, ...}
    overall_maturity_score: Optional[float] = None
    accreditation_level: AccreditationLevel = AccreditationLevel.NOT_ACCREDITED
    
    # Confidence metrics
    confidence_score: Optional[float] = None  # 0-1
    data_completeness: Optional[float] = None  # Percentage of criteria assessed
    
    # Status
    is_draft: bool = True
    is_submitted: bool = False
    submitted_at: Optional[datetime] = None
    
    # Metadata
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def calculate_scores(self, standards_service) -> None:
        """
        Calculate part scores and overall maturity score from criterion scores.
        
        Formula: Overall = (Part_I × 0.20) + (Part_II × 0.35) + (Part_III × 0.30) + (Part_IV × 0.15)
        """
        from app.services.standards_service import standards_service as std_svc
        
        # Build lookup of criterion scores
        score_lookup = {cs.criterion_id: cs.score for cs in self.criterion_scores}
        
        # Calculate scores per part
        parts = std_svc.get_parts()
        part_weights = {"I": 0.20, "II": 0.35, "III": 0.30, "IV": 0.15}
        
        total_weighted = 0.0
        total_weight = 0.0
        
        for part in parts:
            chapter_scores = []
            for chapter in part.chapters:
                criteria_in_chapter = []
                for criterion in chapter.criteria:
                    if criterion.id in score_lookup:
                        criteria_in_chapter.append(score_lookup[criterion.id])
                
                if criteria_in_chapter:
                    chapter_avg = sum(criteria_in_chapter) / len(criteria_in_chapter)
                    chapter_scores.append(chapter_avg * chapter.weight)
            
            if chapter_scores:
                part_score = sum(chapter_scores)
                self.part_scores[part.number] = round(part_score, 2)
                
                weight = part_weights.get(part.number, 0.25)
                total_weighted += part_score * weight
                total_weight += weight
        
        # Calculate overall score
        if total_weight > 0:
            self.overall_maturity_score = round(total_weighted / total_weight, 2)
            
            # Determine accreditation level
            score = self.overall_maturity_score
            if score >= 4.0:
                self.accreditation_level = AccreditationLevel.EXCELLENT
            elif score >= 3.5:
                self.accreditation_level = AccreditationLevel.VERY_GOOD
            elif score >= 3.0:
                self.accreditation_level = AccreditationLevel.GOOD
            elif score >= 2.5:
                self.accreditation_level = AccreditationLevel.PASS
            else:
                self.accreditation_level = AccreditationLevel.NOT_ACCREDITED
        
        # Calculate data completeness
        total_criteria = len(std_svc.get_all_criteria())
        assessed_criteria = len(self.criterion_scores)
        self.data_completeness = round(assessed_criteria / total_criteria * 100, 1) if total_criteria > 0 else 0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }

