"""
ISQua EEA (External Evaluation Association) Integration Service.
Maps ISQua 9 Principles to HA Thailand Standards.
"""

from typing import Optional, List, Dict
from enum import Enum


class ISQuaRating(int, Enum):
    """ISQua 3-point rating scale."""
    NOT_MET = 1
    PARTIALLY_MET = 2
    FULLY_MET = 3


class ISQuaService:
    """Service for ISQua EEA framework integration."""
    
    def __init__(self):
        self._principles = self._build_isqua_principles()
        self._ha_mapping = self._build_ha_mapping()
    
    def _build_isqua_principles(self) -> List[Dict]:
        """Build the ISQua 9 Principles framework."""
        return [
            {
                "id": "principle_1",
                "number": 1,
                "name": "Governance, Leadership and Management",
                "description": "The organization has effective governance, leadership and management systems that support person-centred care.",
                "focus_areas": [
                    "Governance structure and accountability",
                    "Strategic planning and resource allocation",
                    "Performance management and improvement",
                    "Risk management framework",
                    "Ethical decision-making",
                ],
                "ha_chapters": ["I-1", "I-2", "I-4"],
                "weight": 0.12,
            },
            {
                "id": "principle_2",
                "number": 2,
                "name": "Person-Centred Care",
                "description": "Care is planned, coordinated and delivered with the person at the centre.",
                "focus_areas": [
                    "Patient rights and dignity",
                    "Informed consent and shared decision-making",
                    "Cultural safety and diversity",
                    "Patient and family engagement",
                    "Complaint and feedback management",
                ],
                "ha_chapters": ["I-3", "III-2", "III-3", "III-5"],
                "weight": 0.12,
            },
            {
                "id": "principle_3",
                "number": 3,
                "name": "Safety and Risk Management",
                "description": "Systems exist to identify, assess and manage risks to ensure the safety of all.",
                "focus_areas": [
                    "Patient safety culture",
                    "Clinical risk identification",
                    "Incident reporting and learning",
                    "Medication safety",
                    "Infection prevention and control",
                ],
                "ha_chapters": ["II-1", "II-4", "II-6"],
                "weight": 0.15,
            },
            {
                "id": "principle_4",
                "number": 4,
                "name": "Process of Care Delivery",
                "description": "Care processes are evidence-based, coordinated and delivered safely.",
                "focus_areas": [
                    "Clinical pathways and protocols",
                    "Care coordination and transitions",
                    "Diagnostic services",
                    "Surgical and procedural care",
                    "Emergency and critical care",
                ],
                "ha_chapters": ["III-1", "III-4", "III-6", "II-7"],
                "weight": 0.15,
            },
            {
                "id": "principle_5",
                "number": 5,
                "name": "Sustainable Care",
                "description": "The organization demonstrates commitment to environmental and social sustainability.",
                "focus_areas": [
                    "Environmental management",
                    "Resource efficiency",
                    "Waste management",
                    "Climate resilience",
                    "Community health impact",
                ],
                "ha_chapters": ["II-3", "II-9"],
                "weight": 0.08,
            },
            {
                "id": "principle_6",
                "number": 6,
                "name": "Digital Care and AI Systems",
                "description": "Digital technologies and AI are used safely and ethically to support care.",
                "focus_areas": [
                    "Health information systems",
                    "Data governance and privacy",
                    "Clinical decision support",
                    "Telehealth services",
                    "AI ethics and safety",
                ],
                "ha_chapters": ["I-4", "II-5", "III-4"],
                "weight": 0.10,
            },
            {
                "id": "principle_7",
                "number": 7,
                "name": "Supporting Care Workforce",
                "description": "The workforce is competent, supported and engaged.",
                "focus_areas": [
                    "Workforce planning and recruitment",
                    "Competency and credentialing",
                    "Education and development",
                    "Staff wellbeing and safety",
                    "Professional governance",
                ],
                "ha_chapters": ["I-5", "II-2"],
                "weight": 0.12,
            },
            {
                "id": "principle_8",
                "number": 8,
                "name": "Quality Performance",
                "description": "Performance is monitored, measured and used for improvement.",
                "focus_areas": [
                    "Quality indicators and metrics",
                    "Clinical outcomes measurement",
                    "Patient experience monitoring",
                    "Benchmarking and comparison",
                    "Continuous improvement",
                ],
                "ha_chapters": ["IV-1", "IV-2", "IV-5"],
                "weight": 0.12,
            },
            {
                "id": "principle_9",
                "number": 9,
                "name": "Standards Development and Rating",
                "description": "Standards are developed, reviewed and applied consistently.",
                "focus_areas": [
                    "Standards governance",
                    "Rating methodology",
                    "Surveyor training",
                    "Accreditation decisions",
                    "Appeals process",
                ],
                "ha_chapters": ["I-1", "I-4"],
                "weight": 0.04,
            },
        ]
    
    def _build_ha_mapping(self) -> Dict[str, Dict]:
        """Build detailed HA to ISQua mapping."""
        return {
            "I-1": {
                "chapter_name": "Leadership",
                "isqua_principles": ["principle_1", "principle_9"],
                "alignment_strength": 0.9,
                "alignment_notes": "Strong alignment with Governance, Leadership and Management",
            },
            "I-2": {
                "chapter_name": "Strategy",
                "isqua_principles": ["principle_1"],
                "alignment_strength": 0.85,
                "alignment_notes": "Strategic planning and resource allocation alignment",
            },
            "I-3": {
                "chapter_name": "Patient/Customer",
                "isqua_principles": ["principle_2"],
                "alignment_strength": 0.95,
                "alignment_notes": "Direct alignment with Person-Centred Care",
            },
            "I-4": {
                "chapter_name": "Measurement, Analysis and KM",
                "isqua_principles": ["principle_1", "principle_6", "principle_9"],
                "alignment_strength": 0.85,
                "alignment_notes": "Supports governance, digital care and quality measurement",
            },
            "I-5": {
                "chapter_name": "Workforce",
                "isqua_principles": ["principle_7"],
                "alignment_strength": 0.95,
                "alignment_notes": "Direct alignment with Supporting Care Workforce",
            },
            "II-1": {
                "chapter_name": "Quality, Risk and Safety",
                "isqua_principles": ["principle_3"],
                "alignment_strength": 0.95,
                "alignment_notes": "Direct alignment with Safety and Risk Management",
            },
            "II-2": {
                "chapter_name": "Professional Governance",
                "isqua_principles": ["principle_7"],
                "alignment_strength": 0.85,
                "alignment_notes": "Professional governance and credentialing",
            },
            "II-3": {
                "chapter_name": "Environment of Care",
                "isqua_principles": ["principle_5"],
                "alignment_strength": 0.80,
                "alignment_notes": "Environmental management and safety",
            },
            "II-4": {
                "chapter_name": "Infection Prevention and Control",
                "isqua_principles": ["principle_3"],
                "alignment_strength": 0.90,
                "alignment_notes": "IPC is critical component of safety",
            },
            "II-5": {
                "chapter_name": "Medical Record System",
                "isqua_principles": ["principle_6"],
                "alignment_strength": 0.85,
                "alignment_notes": "Health information systems and data governance",
            },
            "II-6": {
                "chapter_name": "Medication Management",
                "isqua_principles": ["principle_3"],
                "alignment_strength": 0.90,
                "alignment_notes": "Medication safety alignment",
            },
            "II-7": {
                "chapter_name": "Diagnostic Investigation",
                "isqua_principles": ["principle_4"],
                "alignment_strength": 0.80,
                "alignment_notes": "Diagnostic services as part of care processes",
            },
            "II-9": {
                "chapter_name": "Working with Communities",
                "isqua_principles": ["principle_5"],
                "alignment_strength": 0.75,
                "alignment_notes": "Community health impact and outreach",
            },
            "III-1": {
                "chapter_name": "Access and Entry",
                "isqua_principles": ["principle_4"],
                "alignment_strength": 0.85,
                "alignment_notes": "Part of care delivery processes",
            },
            "III-2": {
                "chapter_name": "Patient Assessment",
                "isqua_principles": ["principle_2", "principle_4"],
                "alignment_strength": 0.90,
                "alignment_notes": "Person-centred assessment processes",
            },
            "III-3": {
                "chapter_name": "Planning",
                "isqua_principles": ["principle_2"],
                "alignment_strength": 0.90,
                "alignment_notes": "Shared decision-making in care planning",
            },
            "III-4": {
                "chapter_name": "Patient Care Delivery",
                "isqua_principles": ["principle_4", "principle_6"],
                "alignment_strength": 0.95,
                "alignment_notes": "Core care delivery processes",
            },
            "III-5": {
                "chapter_name": "Information and Empowerment",
                "isqua_principles": ["principle_2"],
                "alignment_strength": 0.90,
                "alignment_notes": "Patient engagement and education",
            },
            "III-6": {
                "chapter_name": "Continuity of Care",
                "isqua_principles": ["principle_4"],
                "alignment_strength": 0.85,
                "alignment_notes": "Care coordination and transitions",
            },
            "IV-1": {
                "chapter_name": "Healthcare Results",
                "isqua_principles": ["principle_8"],
                "alignment_strength": 0.95,
                "alignment_notes": "Clinical outcomes measurement",
            },
            "IV-2": {
                "chapter_name": "Patient/Customer-Focused Results",
                "isqua_principles": ["principle_8"],
                "alignment_strength": 0.90,
                "alignment_notes": "Patient experience monitoring",
            },
            "IV-5": {
                "chapter_name": "Key Work Process Results",
                "isqua_principles": ["principle_8"],
                "alignment_strength": 0.85,
                "alignment_notes": "Process performance metrics",
            },
        }
    
    def get_principles(self) -> List[Dict]:
        """Get all ISQua 9 Principles."""
        return self._principles
    
    def get_principle(self, principle_id: str) -> Optional[Dict]:
        """Get a specific ISQua principle."""
        for p in self._principles:
            if p["id"] == principle_id:
                return p
        return None
    
    def get_ha_to_isqua_mapping(self) -> Dict[str, Dict]:
        """Get the HA to ISQua mapping."""
        return self._ha_mapping
    
    def convert_ha_score_to_isqua(self, ha_score: float) -> int:
        """Convert HA Thailand score (1-5) to ISQua rating (1-3)."""
        if ha_score >= 4.0:
            return ISQuaRating.FULLY_MET.value
        elif ha_score >= 2.0:
            return ISQuaRating.PARTIALLY_MET.value
        return ISQuaRating.NOT_MET.value
    
    def convert_isqua_to_ha_score(self, isqua_rating: int) -> float:
        """Convert ISQua rating (1-3) to HA Thailand score range."""
        mapping = {
            1: 1.5,  # Not met -> 1-1.5
            2: 2.5,  # Partially met -> 2-3
            3: 4.5,  # Fully met -> 4-5
        }
        return mapping.get(isqua_rating, 2.5)
    
    def assess_principle_compliance(
        self,
        principle_id: str,
        ha_chapter_scores: Dict[str, float],
    ) -> Dict:
        """Assess compliance with an ISQua principle based on HA scores."""
        principle = self.get_principle(principle_id)
        if not principle:
            return {"error": "Principle not found"}
        
        # Get scores for mapped chapters
        chapter_scores = []
        for chapter_id in principle["ha_chapters"]:
            if chapter_id in ha_chapter_scores:
                mapping = self._ha_mapping.get(chapter_id, {})
                chapter_scores.append({
                    "chapter_id": chapter_id,
                    "chapter_name": mapping.get("chapter_name", chapter_id),
                    "ha_score": ha_chapter_scores[chapter_id],
                    "isqua_rating": self.convert_ha_score_to_isqua(ha_chapter_scores[chapter_id]),
                    "alignment_strength": mapping.get("alignment_strength", 0.8),
                })
        
        # Calculate principle score
        if chapter_scores:
            weighted_sum = sum(
                cs["ha_score"] * cs["alignment_strength"]
                for cs in chapter_scores
            )
            total_weight = sum(cs["alignment_strength"] for cs in chapter_scores)
            principle_score = weighted_sum / total_weight if total_weight > 0 else 0
        else:
            principle_score = 0
        
        return {
            "principle_id": principle_id,
            "principle_name": principle["name"],
            "principle_number": principle["number"],
            "ha_score": round(principle_score, 2),
            "isqua_rating": self.convert_ha_score_to_isqua(principle_score),
            "isqua_rating_text": self._get_rating_text(self.convert_ha_score_to_isqua(principle_score)),
            "chapter_details": chapter_scores,
            "focus_areas": principle["focus_areas"],
        }
    
    def full_isqua_assessment(self, ha_chapter_scores: Dict[str, float]) -> Dict:
        """Perform full ISQua assessment based on HA chapter scores."""
        principle_results = []
        total_weighted_score = 0
        total_weight = 0
        
        for principle in self._principles:
            result = self.assess_principle_compliance(
                principle["id"],
                ha_chapter_scores,
            )
            result["weight"] = principle["weight"]
            principle_results.append(result)
            
            total_weighted_score += result["ha_score"] * principle["weight"]
            total_weight += principle["weight"]
        
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0
        
        # Summary by rating
        rating_summary = {1: 0, 2: 0, 3: 0}
        for pr in principle_results:
            rating_summary[pr["isqua_rating"]] = rating_summary.get(pr["isqua_rating"], 0) + 1
        
        return {
            "overall_ha_score": round(overall_score, 2),
            "overall_isqua_rating": self.convert_ha_score_to_isqua(overall_score),
            "overall_isqua_text": self._get_rating_text(self.convert_ha_score_to_isqua(overall_score)),
            "principle_results": principle_results,
            "rating_summary": {
                "not_met": rating_summary[1],
                "partially_met": rating_summary[2],
                "fully_met": rating_summary[3],
            },
            "strengths": [
                pr for pr in principle_results if pr["isqua_rating"] == 3
            ][:3],
            "improvements_needed": [
                pr for pr in principle_results if pr["isqua_rating"] == 1
            ],
        }
    
    def _get_rating_text(self, rating: int) -> str:
        """Get text description for ISQua rating."""
        texts = {
            1: "Does not meet criterion",
            2: "Partially meets criterion",
            3: "Fully meets criterion",
        }
        return texts.get(rating, "Unknown")


# Global instance
_isqua_service: Optional[ISQuaService] = None


def get_isqua_service() -> ISQuaService:
    """Get or create the ISQua service instance."""
    global _isqua_service
    if _isqua_service is None:
        _isqua_service = ISQuaService()
    return _isqua_service


