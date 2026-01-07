"""
WHO DISAH Framework Integration Service.
Digital Health Interventions, Services and Applications in Health.
"""

from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class DISAHCategory(str, Enum):
    """DISAH intervention categories."""
    POINT_OF_SERVICE = "point_of_service"
    PROVIDER_ADMIN = "provider_administration"
    REGISTRIES = "registries_directories"
    DATA_MANAGEMENT = "data_management"
    SURVEILLANCE = "surveillance_response"


class ReadinessLevel(str, Enum):
    """Digital health readiness levels."""
    NOT_STARTED = "not_started"
    PLANNING = "planning"
    PILOT = "pilot"
    PARTIAL = "partial_implementation"
    FULL = "full_implementation"
    OPTIMIZING = "optimizing"


class DigitalHealthService:
    """Service for WHO DISAH framework tracking."""
    
    def __init__(self):
        self._framework = self._build_disah_framework()
        self._hospital_assessments: Dict[str, Dict] = {}
    
    def _build_disah_framework(self) -> Dict:
        """Build the DISAH framework structure."""
        return {
            DISAHCategory.POINT_OF_SERVICE: {
                "name": "Point of Service Applications",
                "description": "Digital tools used at the point of care delivery",
                "ha_mapping": ["III-2", "III-4", "III-5"],
                "interventions": [
                    {
                        "id": "emr",
                        "name": "Electronic Medical Records (EMR)",
                        "description": "Digital patient health records management",
                        "critical": True,
                        "weight": 0.25,
                    },
                    {
                        "id": "cdss",
                        "name": "Clinical Decision Support System (CDSS)",
                        "description": "AI-powered clinical recommendations",
                        "critical": True,
                        "weight": 0.20,
                    },
                    {
                        "id": "telehealth",
                        "name": "Telehealth/Telemedicine",
                        "description": "Remote patient consultation and monitoring",
                        "critical": False,
                        "weight": 0.15,
                    },
                    {
                        "id": "cpoe",
                        "name": "Computerized Provider Order Entry (CPOE)",
                        "description": "Electronic ordering system for medications and tests",
                        "critical": True,
                        "weight": 0.20,
                    },
                    {
                        "id": "emar",
                        "name": "Electronic Medication Administration Record",
                        "description": "Digital medication tracking and administration",
                        "critical": True,
                        "weight": 0.20,
                    },
                ],
            },
            DISAHCategory.PROVIDER_ADMIN: {
                "name": "Provider Administration",
                "description": "Administrative and operational systems",
                "ha_mapping": ["I-4", "I-5", "I-6"],
                "interventions": [
                    {
                        "id": "hris",
                        "name": "Human Resource Information System (HRIS)",
                        "description": "Staff management and scheduling",
                        "critical": False,
                        "weight": 0.25,
                    },
                    {
                        "id": "lms",
                        "name": "Learning Management System (LMS)",
                        "description": "Staff training and competency tracking",
                        "critical": False,
                        "weight": 0.20,
                    },
                    {
                        "id": "finance",
                        "name": "Financial Management System",
                        "description": "Billing, accounting, and financial reporting",
                        "critical": False,
                        "weight": 0.20,
                    },
                    {
                        "id": "supply",
                        "name": "Supply Chain Management",
                        "description": "Inventory and procurement management",
                        "critical": False,
                        "weight": 0.20,
                    },
                    {
                        "id": "scheduling",
                        "name": "Appointment Scheduling System",
                        "description": "Patient and resource scheduling",
                        "critical": False,
                        "weight": 0.15,
                    },
                ],
            },
            DISAHCategory.REGISTRIES: {
                "name": "Registries and Directories",
                "description": "Master data management systems",
                "ha_mapping": ["II-5", "I-4"],
                "interventions": [
                    {
                        "id": "mpi",
                        "name": "Master Patient Index (MPI)",
                        "description": "Unique patient identification across systems",
                        "critical": True,
                        "weight": 0.30,
                    },
                    {
                        "id": "provider_registry",
                        "name": "Provider Registry",
                        "description": "Healthcare provider directory and credentials",
                        "critical": False,
                        "weight": 0.25,
                    },
                    {
                        "id": "facility_registry",
                        "name": "Facility Registry",
                        "description": "Healthcare facility master data",
                        "critical": False,
                        "weight": 0.20,
                    },
                    {
                        "id": "terminology",
                        "name": "Terminology Services",
                        "description": "Standardized clinical vocabularies (ICD, SNOMED)",
                        "critical": True,
                        "weight": 0.25,
                    },
                ],
            },
            DISAHCategory.DATA_MANAGEMENT: {
                "name": "Data Management and Analytics",
                "description": "Data collection, analysis, and exchange",
                "ha_mapping": ["I-4", "IV-1", "IV-5"],
                "interventions": [
                    {
                        "id": "analytics",
                        "name": "Health Analytics Platform",
                        "description": "Data warehouse and business intelligence",
                        "critical": False,
                        "weight": 0.25,
                    },
                    {
                        "id": "hie",
                        "name": "Health Information Exchange (HIE)",
                        "description": "Interoperability and data sharing",
                        "critical": True,
                        "weight": 0.30,
                    },
                    {
                        "id": "data_quality",
                        "name": "Data Quality Management",
                        "description": "Data validation and cleansing tools",
                        "critical": False,
                        "weight": 0.20,
                    },
                    {
                        "id": "reporting",
                        "name": "Reporting and Dashboards",
                        "description": "Performance monitoring and KPI tracking",
                        "critical": False,
                        "weight": 0.25,
                    },
                ],
            },
            DISAHCategory.SURVEILLANCE: {
                "name": "Surveillance and Response",
                "description": "Public health monitoring systems",
                "ha_mapping": ["II-4", "II-8"],
                "interventions": [
                    {
                        "id": "disease_surveillance",
                        "name": "Disease Surveillance System",
                        "description": "Outbreak detection and reporting",
                        "critical": True,
                        "weight": 0.35,
                    },
                    {
                        "id": "adverse_events",
                        "name": "Adverse Event Reporting",
                        "description": "Safety incident tracking and reporting",
                        "critical": True,
                        "weight": 0.30,
                    },
                    {
                        "id": "emergency",
                        "name": "Emergency Response System",
                        "description": "Crisis management and communication",
                        "critical": False,
                        "weight": 0.20,
                    },
                    {
                        "id": "antimicrobial",
                        "name": "Antimicrobial Stewardship System",
                        "description": "Antibiotic usage monitoring",
                        "critical": False,
                        "weight": 0.15,
                    },
                ],
            },
        }
    
    def get_framework(self) -> Dict:
        """Get the complete DISAH framework."""
        return {
            "categories": [
                {
                    "id": cat.value,
                    "name": data["name"],
                    "description": data["description"],
                    "ha_mapping": data["ha_mapping"],
                    "intervention_count": len(data["interventions"]),
                    "critical_count": sum(1 for i in data["interventions"] if i["critical"]),
                }
                for cat, data in self._framework.items()
            ],
            "total_interventions": sum(
                len(data["interventions"]) for data in self._framework.values()
            ),
        }
    
    def get_category_details(self, category_id: str) -> Optional[Dict]:
        """Get detailed information about a DISAH category."""
        try:
            category = DISAHCategory(category_id)
            data = self._framework[category]
            return {
                "id": category.value,
                "name": data["name"],
                "description": data["description"],
                "ha_mapping": data["ha_mapping"],
                "interventions": data["interventions"],
            }
        except (ValueError, KeyError):
            return None
    
    def assess_readiness(
        self,
        hospital_id: str,
        assessments: Dict[str, str],  # intervention_id -> readiness_level
    ) -> Dict:
        """Assess digital health readiness for a hospital."""
        results = {
            "hospital_id": hospital_id,
            "assessment_date": datetime.now().isoformat(),
            "categories": [],
            "overall_score": 0,
            "overall_level": ReadinessLevel.NOT_STARTED.value,
            "critical_gaps": [],
            "recommendations": [],
        }
        
        level_scores = {
            ReadinessLevel.NOT_STARTED.value: 0,
            ReadinessLevel.PLANNING.value: 1,
            ReadinessLevel.PILOT.value: 2,
            ReadinessLevel.PARTIAL.value: 3,
            ReadinessLevel.FULL.value: 4,
            ReadinessLevel.OPTIMIZING.value: 5,
        }
        
        total_weighted_score = 0
        total_weight = 0
        
        for category, data in self._framework.items():
            cat_score = 0
            cat_weight = 0
            interventions_status = []
            
            for intervention in data["interventions"]:
                int_id = intervention["id"]
                level = assessments.get(int_id, ReadinessLevel.NOT_STARTED.value)
                score = level_scores.get(level, 0)
                weight = intervention["weight"]
                
                cat_score += score * weight
                cat_weight += weight
                
                interventions_status.append({
                    "id": int_id,
                    "name": intervention["name"],
                    "level": level,
                    "score": score,
                    "critical": intervention["critical"],
                })
                
                # Track critical gaps
                if intervention["critical"] and score < 3:
                    results["critical_gaps"].append({
                        "category": category.value,
                        "intervention": intervention["name"],
                        "current_level": level,
                        "gap_severity": "high" if score < 2 else "medium",
                    })
            
            category_score = (cat_score / cat_weight) if cat_weight > 0 else 0
            total_weighted_score += category_score * len(data["interventions"])
            total_weight += len(data["interventions"])
            
            results["categories"].append({
                "id": category.value,
                "name": data["name"],
                "score": round(category_score, 2),
                "level": self._score_to_level(category_score),
                "interventions": interventions_status,
            })
        
        # Calculate overall score
        results["overall_score"] = round(
            (total_weighted_score / total_weight) if total_weight > 0 else 0, 2
        )
        results["overall_level"] = self._score_to_level(results["overall_score"])
        
        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)
        
        # Store assessment
        self._hospital_assessments[hospital_id] = results
        
        return results
    
    def get_hospital_assessment(self, hospital_id: str) -> Optional[Dict]:
        """Get the latest digital health assessment for a hospital."""
        return self._hospital_assessments.get(hospital_id)
    
    def get_ha_alignment(self) -> List[Dict]:
        """Get mapping between DISAH interventions and HA criteria."""
        alignments = []
        
        for category, data in self._framework.items():
            for intervention in data["interventions"]:
                alignments.append({
                    "intervention_id": intervention["id"],
                    "intervention_name": intervention["name"],
                    "category": category.value,
                    "ha_chapters": data["ha_mapping"],
                    "critical_for_accreditation": intervention["critical"],
                    "impact_description": self._get_impact_description(
                        intervention["id"], data["ha_mapping"]
                    ),
                })
        
        return alignments
    
    def _score_to_level(self, score: float) -> str:
        """Convert numeric score to readiness level."""
        if score >= 4.5:
            return ReadinessLevel.OPTIMIZING.value
        elif score >= 3.5:
            return ReadinessLevel.FULL.value
        elif score >= 2.5:
            return ReadinessLevel.PARTIAL.value
        elif score >= 1.5:
            return ReadinessLevel.PILOT.value
        elif score >= 0.5:
            return ReadinessLevel.PLANNING.value
        return ReadinessLevel.NOT_STARTED.value
    
    def _generate_recommendations(self, assessment: Dict) -> List[Dict]:
        """Generate improvement recommendations based on assessment."""
        recommendations = []
        
        # Priority 1: Critical gaps
        for gap in assessment["critical_gaps"][:3]:
            recommendations.append({
                "priority": 1,
                "type": "critical_gap",
                "intervention": gap["intervention"],
                "recommendation": f"Prioritize implementation of {gap['intervention']} - critical for patient safety",
                "expected_impact": "High impact on accreditation readiness",
            })
        
        # Priority 2: Low-scoring categories
        for cat in sorted(assessment["categories"], key=lambda x: x["score"])[:2]:
            if cat["score"] < 3:
                recommendations.append({
                    "priority": 2,
                    "type": "category_improvement",
                    "category": cat["name"],
                    "recommendation": f"Strengthen {cat['name']} systems (current score: {cat['score']}/5)",
                    "expected_impact": "Medium impact on operational efficiency",
                })
        
        # Priority 3: Integration opportunities
        if assessment["overall_score"] >= 2.5:
            recommendations.append({
                "priority": 3,
                "type": "integration",
                "recommendation": "Focus on Health Information Exchange (HIE) to improve interoperability",
                "expected_impact": "Enhanced care coordination and data sharing",
            })
        
        return recommendations
    
    def _get_impact_description(self, intervention_id: str, ha_chapters: List[str]) -> str:
        """Get impact description for intervention-HA alignment."""
        impact_map = {
            "emr": "Supports patient assessment documentation and care planning",
            "cdss": "Enhances clinical decision-making and reduces errors",
            "telehealth": "Improves access to care and continuity",
            "cpoe": "Reduces medication errors and improves safety",
            "emar": "Ensures accurate medication administration tracking",
            "hris": "Supports workforce management and competency tracking",
            "lms": "Enables continuous staff education and training",
            "mpi": "Ensures unique patient identification across encounters",
            "hie": "Enables seamless data exchange for care coordination",
            "disease_surveillance": "Supports infection control and outbreak response",
            "adverse_events": "Enables safety event tracking and learning",
        }
        return impact_map.get(intervention_id, f"Supports HA chapters: {', '.join(ha_chapters)}")


# Global instance
_digital_health_service: Optional[DigitalHealthService] = None


def get_digital_health_service() -> DigitalHealthService:
    """Get or create the digital health service instance."""
    global _digital_health_service
    if _digital_health_service is None:
        _digital_health_service = DigitalHealthService()
    return _digital_health_service

