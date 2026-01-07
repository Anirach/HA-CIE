"""
Standards Service - HA Thailand Standards 5th Edition data model.
Provides the complete standards framework with Parts, Chapters, and Criteria.
"""
from typing import List, Dict, Optional
from pydantic import BaseModel
from enum import Enum


class CriterionCategory(str, Enum):
    """Criterion classification categories."""
    ESSENTIAL = "essential"  # Essential for Safety - 30% weight, 1.5x multiplier
    CORE = "core"  # Core for Sustainability - 35% weight, 1.25x multiplier
    BASIC = "basic"  # Basic Requirements - 35% weight, 1.0x multiplier


class Criterion(BaseModel):
    """A criterion within a chapter."""
    id: str
    name: str
    weight: float
    category: CriterionCategory = CriterionCategory.BASIC
    description: Optional[str] = None


class Chapter(BaseModel):
    """A chapter within a part."""
    id: str
    number: str
    name: str
    weight: float
    focus: str
    criteria: List[Criterion] = []


class Part(BaseModel):
    """A part of the HA Thailand Standards."""
    number: str
    name: str
    weight: float
    color: str
    chapters: List[Chapter] = []


class CausalRelationship(BaseModel):
    """A causal relationship between criteria/chapters."""
    source: str
    target: str
    strength: float  # 0.0 - 1.0
    relationship_type: str  # prerequisite, strong_support, moderate_support, weak_support
    mechanism: str  # Description of how source affects target
    direction: str = "positive"  # positive or negative


class StandardsFramework(BaseModel):
    """Complete HA Thailand Standards Framework."""
    parts: List[Part]
    causal_relationships: List[CausalRelationship]


class StandardsService:
    """Service for accessing HA Thailand Standards data."""
    
    def __init__(self):
        self._framework = self._build_framework()
    
    def _build_framework(self) -> StandardsFramework:
        """Build the complete standards framework."""
        parts = [
            self._build_part_1(),
            self._build_part_2(),
            self._build_part_3(),
            self._build_part_4(),
        ]
        relationships = self._build_causal_relationships()
        return StandardsFramework(parts=parts, causal_relationships=relationships)
    
    def _build_part_1(self) -> Part:
        """Part I - Organization Management Overview (20%)."""
        return Part(
            number="I",
            name="Organization Management Overview",
            weight=0.20,
            color="#9333ea",  # Purple
            chapters=[
                Chapter(
                    id="I-1",
                    number="1",
                    name="Leadership",
                    weight=0.25,
                    focus="Vision, Mission, Values, Senior Leadership",
                    criteria=[
                        Criterion(id="I-1.1", name="Vision, Mission, Values", weight=0.30, 
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Organization has clear vision, mission, and values that guide all activities"),
                        Criterion(id="I-1.2", name="Communication", weight=0.20,
                                  description="Leadership effectively communicates direction and expectations"),
                        Criterion(id="I-1.3", name="Organization Success", weight=0.20,
                                  category=CriterionCategory.CORE,
                                  description="Leadership creates environment for organizational success"),
                        Criterion(id="I-1.4", name="Governance", weight=0.20,
                                  description="Effective governance structures and processes"),
                        Criterion(id="I-1.5", name="Societal Contribution", weight=0.10,
                                  description="Organization contributes to community and society"),
                    ]
                ),
                Chapter(
                    id="I-2",
                    number="2",
                    name="Strategy",
                    weight=0.15,
                    focus="Strategic Planning, Action Plans",
                    criteria=[
                        Criterion(id="I-2.1", name="Strategic Planning Process", weight=0.40,
                                  category=CriterionCategory.CORE,
                                  description="Systematic strategic planning process"),
                        Criterion(id="I-2.2", name="Strategy Implementation", weight=0.35,
                                  description="Effective deployment of strategic objectives"),
                        Criterion(id="I-2.3", name="Action Plans", weight=0.25,
                                  description="Action plans aligned with strategy"),
                    ]
                ),
                Chapter(
                    id="I-3",
                    number="3",
                    name="Patient/Customer",
                    weight=0.20,
                    focus="Needs, Expectations, Engagement",
                    criteria=[
                        Criterion(id="I-3.1", name="Patient Voice", weight=0.35,
                                  category=CriterionCategory.CORE,
                                  description="Systems to capture patient voice and expectations"),
                        Criterion(id="I-3.2", name="Patient Engagement", weight=0.35,
                                  description="Meaningful patient engagement in care"),
                        Criterion(id="I-3.3", name="Customer Relations", weight=0.30,
                                  description="Effective customer relationship management"),
                    ]
                ),
                Chapter(
                    id="I-4",
                    number="4",
                    name="Measurement, Analysis and Knowledge Management",
                    weight=0.15,
                    focus="Performance Measurement, Knowledge Management",
                    criteria=[
                        Criterion(id="I-4.1", name="Performance Measurement", weight=0.35,
                                  category=CriterionCategory.CORE,
                                  description="Comprehensive performance measurement system"),
                        Criterion(id="I-4.2", name="Data Analysis", weight=0.35,
                                  description="Effective use of data for decision making"),
                        Criterion(id="I-4.3", name="Knowledge Management", weight=0.30,
                                  description="Systems for managing organizational knowledge"),
                    ]
                ),
                Chapter(
                    id="I-5",
                    number="5",
                    name="Workforce",
                    weight=0.15,
                    focus="Staff Development, Engagement, Safety",
                    criteria=[
                        Criterion(id="I-5.1", name="Workforce Planning", weight=0.25,
                                  category=CriterionCategory.CORE,
                                  description="Strategic workforce planning and capability building"),
                        Criterion(id="I-5.2", name="Staff Development", weight=0.25,
                                  description="Comprehensive staff training and development"),
                        Criterion(id="I-5.3", name="Staff Engagement", weight=0.25,
                                  description="Staff engagement and satisfaction"),
                        Criterion(id="I-5.4", name="Workforce Safety", weight=0.25,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Workforce health and safety programs"),
                    ]
                ),
                Chapter(
                    id="I-6",
                    number="6",
                    name="Operation",
                    weight=0.10,
                    focus="Process Management, Effectiveness",
                    criteria=[
                        Criterion(id="I-6.1", name="Process Design", weight=0.35,
                                  description="Effective process design and management"),
                        Criterion(id="I-6.2", name="Process Improvement", weight=0.35,
                                  description="Continuous process improvement"),
                        Criterion(id="I-6.3", name="Supply Chain", weight=0.30,
                                  description="Effective supply chain management"),
                    ]
                ),
            ]
        )
    
    def _build_part_2(self) -> Part:
        """Part II - Key Hospital Systems (35%)."""
        return Part(
            number="II",
            name="Key Hospital Systems",
            weight=0.35,
            color="#dc2626",  # Red
            chapters=[
                Chapter(
                    id="II-1",
                    number="1",
                    name="Quality, Risk and Safety",
                    weight=0.20,
                    focus="Quality Management, Risk Framework",
                    criteria=[
                        Criterion(id="II-1.1", name="Quality Management System", weight=0.30,
                                  category=CriterionCategory.CORE,
                                  description="Comprehensive quality management system"),
                        Criterion(id="II-1.2", name="Patient Care Quality", weight=0.25,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Quality of patient care processes"),
                        Criterion(id="II-1.3", name="Risk Management Framework", weight=0.25,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Integrated risk management framework"),
                        Criterion(id="II-1.4", name="Safety Strategies", weight=0.20,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Patient safety strategies and culture"),
                    ]
                ),
                Chapter(
                    id="II-2",
                    number="2",
                    name="Professional Governance",
                    weight=0.10,
                    focus="Nursing, Medical Staff Oversight",
                    criteria=[
                        Criterion(id="II-2.1", name="Medical Staff Organization", weight=0.35,
                                  description="Medical staff organization and governance"),
                        Criterion(id="II-2.2", name="Nursing Governance", weight=0.35,
                                  description="Nursing governance and leadership"),
                        Criterion(id="II-2.3", name="Credentialing", weight=0.30,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Credentialing and privileging processes"),
                    ]
                ),
                Chapter(
                    id="II-3",
                    number="3",
                    name="Environment of Care",
                    weight=0.12,
                    focus="Physical Environment, Equipment, Safety",
                    criteria=[
                        Criterion(id="II-3.1", name="Physical Environment", weight=0.35,
                                  description="Safe and appropriate physical environment"),
                        Criterion(id="II-3.2", name="Equipment Management", weight=0.35,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Medical equipment management and safety"),
                        Criterion(id="II-3.3", name="Utility Systems", weight=0.30,
                                  description="Utility systems reliability and safety"),
                    ]
                ),
                Chapter(
                    id="II-4",
                    number="4",
                    name="Infection Prevention and Control",
                    weight=0.15,
                    focus="IPC Program, Surveillance, Practices",
                    criteria=[
                        Criterion(id="II-4.1", name="IPC Program", weight=0.25,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Comprehensive infection prevention program"),
                        Criterion(id="II-4.2", name="Surveillance System", weight=0.25,
                                  description="HAI surveillance and monitoring system"),
                        Criterion(id="II-4.3", name="General Prevention Practices", weight=0.25,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Standard precautions and hand hygiene"),
                        Criterion(id="II-4.4", name="Specific Prevention Practices", weight=0.25,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Device-associated and surgical site infection prevention"),
                    ]
                ),
                Chapter(
                    id="II-5",
                    number="5",
                    name="Medical Record System",
                    weight=0.08,
                    focus="Documentation, Security, Confidentiality",
                    criteria=[
                        Criterion(id="II-5.1", name="Documentation Standards", weight=0.40,
                                  description="Complete and accurate medical documentation"),
                        Criterion(id="II-5.2", name="Record Security", weight=0.30,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Medical record security and confidentiality"),
                        Criterion(id="II-5.3", name="Information Availability", weight=0.30,
                                  description="Timely availability of patient information"),
                    ]
                ),
                Chapter(
                    id="II-6",
                    number="6",
                    name="Medication Management",
                    weight=0.15,
                    focus="Drug Safety, Prescribing, Administration",
                    criteria=[
                        Criterion(id="II-6.1", name="Medication System", weight=0.25,
                                  category=CriterionCategory.CORE,
                                  description="Safe medication management system"),
                        Criterion(id="II-6.2", name="Prescribing Safety", weight=0.25,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Safe prescribing practices"),
                        Criterion(id="II-6.3", name="Dispensing Safety", weight=0.25,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Safe dispensing and preparation"),
                        Criterion(id="II-6.4", name="Administration Safety", weight=0.25,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Safe medication administration"),
                    ]
                ),
                Chapter(
                    id="II-7",
                    number="7",
                    name="Diagnostic Investigation",
                    weight=0.10,
                    focus="Lab, Radiology, Pathology Services",
                    criteria=[
                        Criterion(id="II-7.1", name="Laboratory Services", weight=0.40,
                                  category=CriterionCategory.CORE,
                                  description="Quality laboratory services"),
                        Criterion(id="II-7.2", name="Radiology Services", weight=0.35,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Safe and effective radiology services"),
                        Criterion(id="II-7.3", name="Blood Bank", weight=0.25,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Safe blood bank services"),
                    ]
                ),
                Chapter(
                    id="II-8",
                    number="8",
                    name="Disease and Health Hazard Surveillance",
                    weight=0.05,
                    focus="Epidemiology, Public Health",
                    criteria=[
                        Criterion(id="II-8.1", name="Disease Surveillance", weight=0.50,
                                  description="Communicable disease surveillance"),
                        Criterion(id="II-8.2", name="Outbreak Management", weight=0.50,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Outbreak detection and response"),
                    ]
                ),
                Chapter(
                    id="II-9",
                    number="9",
                    name="Working with Communities",
                    weight=0.05,
                    focus="Community Engagement, Outreach",
                    criteria=[
                        Criterion(id="II-9.1", name="Community Needs", weight=0.50,
                                  description="Understanding community health needs"),
                        Criterion(id="II-9.2", name="Community Partnership", weight=0.50,
                                  description="Community partnerships and outreach"),
                    ]
                ),
            ]
        )
    
    def _build_part_3(self) -> Part:
        """Part III - Patient Care Process (30%)."""
        return Part(
            number="III",
            name="Patient Care Process",
            weight=0.30,
            color="#16a34a",  # Green
            chapters=[
                Chapter(
                    id="III-1",
                    number="1",
                    name="Access and Entry",
                    weight=0.15,
                    focus="Service Access, Timely Entry",
                    criteria=[
                        Criterion(id="III-1.1", name="Service Access", weight=0.35,
                                  description="Appropriate access to services"),
                        Criterion(id="III-1.2", name="Registration Process", weight=0.35,
                                  description="Efficient registration and admission"),
                        Criterion(id="III-1.3", name="Emergency Access", weight=0.30,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Timely emergency care access"),
                    ]
                ),
                Chapter(
                    id="III-2",
                    number="2",
                    name="Patient Assessment",
                    weight=0.20,
                    focus="Initial and Ongoing Assessment",
                    criteria=[
                        Criterion(id="III-2.1", name="Initial Assessment", weight=0.40,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Comprehensive initial patient assessment"),
                        Criterion(id="III-2.2", name="Ongoing Assessment", weight=0.35,
                                  description="Appropriate ongoing reassessment"),
                        Criterion(id="III-2.3", name="Special Assessments", weight=0.25,
                                  description="Pain, nutrition, fall risk, and other assessments"),
                    ]
                ),
                Chapter(
                    id="III-3",
                    number="3",
                    name="Planning",
                    weight=0.15,
                    focus="Care Planning, Goal Setting",
                    criteria=[
                        Criterion(id="III-3.1", name="Care Planning", weight=0.50,
                                  category=CriterionCategory.CORE,
                                  description="Individualized care planning"),
                        Criterion(id="III-3.2", name="Goal Setting", weight=0.50,
                                  description="Patient-centered goal setting"),
                    ]
                ),
                Chapter(
                    id="III-4",
                    number="4",
                    name="Patient Care Delivery",
                    weight=0.25,
                    focus="Safe, Effective Treatment",
                    criteria=[
                        Criterion(id="III-4.1", name="General Care", weight=0.20,
                                  description="Safe and effective general care"),
                        Criterion(id="III-4.2", name="Surgical Care", weight=0.15,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Safe surgical and procedural care"),
                        Criterion(id="III-4.3", name="Anesthesia Care", weight=0.15,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Safe anesthesia and sedation"),
                        Criterion(id="III-4.4", name="Emergency Care", weight=0.15,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Effective emergency care"),
                        Criterion(id="III-4.5", name="Obstetric Care", weight=0.10,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Safe obstetric care"),
                        Criterion(id="III-4.6", name="Pain Management", weight=0.10,
                                  description="Effective pain management"),
                        Criterion(id="III-4.7", name="End of Life Care", weight=0.10,
                                  description="Compassionate end of life care"),
                        Criterion(id="III-4.8", name="Restraint Use", weight=0.05,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Safe and appropriate restraint use"),
                    ]
                ),
                Chapter(
                    id="III-5",
                    number="5",
                    name="Information and Empowerment",
                    weight=0.10,
                    focus="Patient Education, Engagement",
                    criteria=[
                        Criterion(id="III-5.1", name="Patient Education", weight=0.50,
                                  description="Effective patient and family education"),
                        Criterion(id="III-5.2", name="Patient Rights", weight=0.50,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Patient rights and informed consent"),
                    ]
                ),
                Chapter(
                    id="III-6",
                    number="6",
                    name="Continuity of Care",
                    weight=0.15,
                    focus="Transitions, Discharge, Follow-up",
                    criteria=[
                        Criterion(id="III-6.1", name="Care Transitions", weight=0.35,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Safe care transitions and handoffs"),
                        Criterion(id="III-6.2", name="Discharge Planning", weight=0.35,
                                  description="Comprehensive discharge planning"),
                        Criterion(id="III-6.3", name="Follow-up Care", weight=0.30,
                                  description="Appropriate follow-up and referrals"),
                    ]
                ),
            ]
        )
    
    def _build_part_4(self) -> Part:
        """Part IV - Organization Performance Results (15%)."""
        return Part(
            number="IV",
            name="Organization Performance Results",
            weight=0.15,
            color="#2563eb",  # Blue
            chapters=[
                Chapter(
                    id="IV-1",
                    number="1",
                    name="Healthcare Results",
                    weight=0.25,
                    focus="Clinical Outcomes",
                    criteria=[
                        Criterion(id="IV-1.1", name="Clinical Outcomes", weight=0.40,
                                  category=CriterionCategory.CORE,
                                  description="Clinical outcome measures and trends"),
                        Criterion(id="IV-1.2", name="Safety Outcomes", weight=0.35,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Patient safety outcome measures"),
                        Criterion(id="IV-1.3", name="Process Measures", weight=0.25,
                                  description="Key process performance measures"),
                    ]
                ),
                Chapter(
                    id="IV-2",
                    number="2",
                    name="Patient/Customer-Focused Results",
                    weight=0.20,
                    focus="Satisfaction, Experience",
                    criteria=[
                        Criterion(id="IV-2.1", name="Patient Satisfaction", weight=0.50,
                                  description="Patient satisfaction measures and trends"),
                        Criterion(id="IV-2.2", name="Patient Experience", weight=0.50,
                                  category=CriterionCategory.CORE,
                                  description="Patient experience measures"),
                    ]
                ),
                Chapter(
                    id="IV-3",
                    number="3",
                    name="Workforce Results",
                    weight=0.15,
                    focus="Staff Satisfaction, Retention",
                    criteria=[
                        Criterion(id="IV-3.1", name="Staff Satisfaction", weight=0.35,
                                  description="Staff satisfaction and engagement"),
                        Criterion(id="IV-3.2", name="Staff Retention", weight=0.35,
                                  description="Workforce retention and turnover"),
                        Criterion(id="IV-3.3", name="Staff Safety", weight=0.30,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Workforce safety outcomes"),
                    ]
                ),
                Chapter(
                    id="IV-4",
                    number="4",
                    name="Leadership and Governance Results",
                    weight=0.15,
                    focus="Strategic Achievement",
                    criteria=[
                        Criterion(id="IV-4.1", name="Strategic Achievement", weight=0.50,
                                  description="Achievement of strategic objectives"),
                        Criterion(id="IV-4.2", name="Ethical Behavior", weight=0.50,
                                  description="Ethical behavior and compliance"),
                    ]
                ),
                Chapter(
                    id="IV-5",
                    number="5",
                    name="Key Work Process Results",
                    weight=0.15,
                    focus="Operational Effectiveness",
                    criteria=[
                        Criterion(id="IV-5.1", name="Process Effectiveness", weight=0.50,
                                  description="Work process effectiveness measures"),
                        Criterion(id="IV-5.2", name="Emergency Preparedness", weight=0.50,
                                  category=CriterionCategory.ESSENTIAL,
                                  description="Emergency preparedness results"),
                    ]
                ),
                Chapter(
                    id="IV-6",
                    number="6",
                    name="Financial Results",
                    weight=0.10,
                    focus="Financial Performance",
                    criteria=[
                        Criterion(id="IV-6.1", name="Financial Performance", weight=0.50,
                                  description="Financial performance measures"),
                        Criterion(id="IV-6.2", name="Resource Efficiency", weight=0.50,
                                  description="Resource utilization and efficiency"),
                    ]
                ),
            ]
        )
    
    def _build_causal_relationships(self) -> List[CausalRelationship]:
        """Build the causal relationships between standards."""
        return [
            # Part I -> Part II relationships
            CausalRelationship(
                source="I-1", target="II-1", strength=0.85,
                relationship_type="prerequisite",
                mechanism="Strong leadership commitment is essential for establishing quality management systems"
            ),
            CausalRelationship(
                source="I-1", target="I-5", strength=0.80,
                relationship_type="prerequisite",
                mechanism="Leadership creates workforce development culture and resources"
            ),
            CausalRelationship(
                source="I-2", target="I-4", strength=0.70,
                relationship_type="strong_support",
                mechanism="Strategic planning drives measurement and analysis priorities"
            ),
            CausalRelationship(
                source="I-4", target="II-1", strength=0.75,
                relationship_type="strong_support",
                mechanism="Measurement systems enable quality monitoring and improvement"
            ),
            CausalRelationship(
                source="I-5", target="II-2", strength=0.80,
                relationship_type="prerequisite",
                mechanism="Workforce development enables professional governance"
            ),
            
            # Part II internal relationships
            CausalRelationship(
                source="II-1", target="II-4", strength=0.85,
                relationship_type="prerequisite",
                mechanism="Quality management framework supports infection prevention programs"
            ),
            CausalRelationship(
                source="II-1", target="II-6", strength=0.80,
                relationship_type="prerequisite",
                mechanism="Quality and risk framework enables medication safety"
            ),
            CausalRelationship(
                source="II-1", target="II-3", strength=0.70,
                relationship_type="strong_support",
                mechanism="Risk management supports safe environment of care"
            ),
            CausalRelationship(
                source="II-2", target="II-6", strength=0.65,
                relationship_type="strong_support",
                mechanism="Professional governance oversees medication practices"
            ),
            CausalRelationship(
                source="II-2", target="II-7", strength=0.65,
                relationship_type="strong_support",
                mechanism="Professional governance oversees diagnostic services"
            ),
            CausalRelationship(
                source="II-4", target="II-3", strength=0.60,
                relationship_type="moderate_support",
                mechanism="IPC practices influence environment of care standards"
            ),
            CausalRelationship(
                source="II-5", target="II-6", strength=0.55,
                relationship_type="moderate_support",
                mechanism="Medical records support medication safety checks"
            ),
            CausalRelationship(
                source="II-8", target="II-4", strength=0.70,
                relationship_type="strong_support",
                mechanism="Disease surveillance informs infection prevention strategies"
            ),
            
            # Part II -> Part III relationships
            CausalRelationship(
                source="II-1", target="III-4", strength=0.80,
                relationship_type="prerequisite",
                mechanism="Quality systems enable safe care delivery"
            ),
            CausalRelationship(
                source="II-4", target="III-4", strength=0.85,
                relationship_type="prerequisite",
                mechanism="Infection prevention directly impacts care delivery safety"
            ),
            CausalRelationship(
                source="II-6", target="III-4", strength=0.85,
                relationship_type="prerequisite",
                mechanism="Medication safety is essential for care delivery"
            ),
            CausalRelationship(
                source="II-5", target="III-2", strength=0.70,
                relationship_type="strong_support",
                mechanism="Medical records support patient assessment documentation"
            ),
            CausalRelationship(
                source="II-5", target="III-6", strength=0.75,
                relationship_type="strong_support",
                mechanism="Medical records enable continuity of care"
            ),
            CausalRelationship(
                source="II-7", target="III-2", strength=0.75,
                relationship_type="strong_support",
                mechanism="Diagnostic services support patient assessment"
            ),
            
            # Part I -> Part III relationships
            CausalRelationship(
                source="I-3", target="III-5", strength=0.80,
                relationship_type="prerequisite",
                mechanism="Patient focus enables effective education and empowerment"
            ),
            CausalRelationship(
                source="I-5", target="III-4", strength=0.85,
                relationship_type="prerequisite",
                mechanism="Skilled workforce is essential for quality care delivery"
            ),
            
            # Part III internal relationships
            CausalRelationship(
                source="III-1", target="III-2", strength=0.80,
                relationship_type="prerequisite",
                mechanism="Appropriate access enables timely assessment"
            ),
            CausalRelationship(
                source="III-2", target="III-3", strength=0.90,
                relationship_type="prerequisite",
                mechanism="Assessment findings drive care planning"
            ),
            CausalRelationship(
                source="III-3", target="III-4", strength=0.90,
                relationship_type="prerequisite",
                mechanism="Care plans guide care delivery"
            ),
            CausalRelationship(
                source="III-4", target="III-6", strength=0.75,
                relationship_type="strong_support",
                mechanism="Care delivery outcomes influence discharge planning"
            ),
            CausalRelationship(
                source="III-5", target="III-6", strength=0.65,
                relationship_type="strong_support",
                mechanism="Patient education supports continuity after discharge"
            ),
            
            # Part III -> Part IV relationships
            CausalRelationship(
                source="III-4", target="IV-1", strength=0.90,
                relationship_type="prerequisite",
                mechanism="Care delivery processes directly determine healthcare outcomes"
            ),
            CausalRelationship(
                source="III-5", target="IV-2", strength=0.80,
                relationship_type="strong_support",
                mechanism="Patient empowerment influences satisfaction and experience"
            ),
            CausalRelationship(
                source="III-2", target="IV-1", strength=0.70,
                relationship_type="strong_support",
                mechanism="Thorough assessment contributes to better outcomes"
            ),
            
            # Part II -> Part IV relationships
            CausalRelationship(
                source="II-4", target="IV-1", strength=0.85,
                relationship_type="prerequisite",
                mechanism="Infection prevention directly impacts clinical outcomes"
            ),
            CausalRelationship(
                source="II-6", target="IV-1", strength=0.80,
                relationship_type="prerequisite",
                mechanism="Medication safety impacts patient outcomes"
            ),
            CausalRelationship(
                source="II-1", target="IV-1", strength=0.75,
                relationship_type="strong_support",
                mechanism="Quality systems drive outcome improvement"
            ),
            
            # Part I -> Part IV relationships
            CausalRelationship(
                source="I-5", target="IV-3", strength=0.90,
                relationship_type="prerequisite",
                mechanism="Workforce management directly determines workforce results"
            ),
            CausalRelationship(
                source="I-1", target="IV-4", strength=0.90,
                relationship_type="prerequisite",
                mechanism="Leadership directly determines governance results"
            ),
            CausalRelationship(
                source="I-2", target="IV-4", strength=0.85,
                relationship_type="prerequisite",
                mechanism="Strategy achievement drives leadership results"
            ),
            CausalRelationship(
                source="I-6", target="IV-5", strength=0.85,
                relationship_type="prerequisite",
                mechanism="Operations directly determine work process results"
            ),
            CausalRelationship(
                source="I-4", target="IV-6", strength=0.65,
                relationship_type="strong_support",
                mechanism="Measurement supports financial performance tracking"
            ),
            
            # Part IV internal relationships (feedback loops)
            CausalRelationship(
                source="IV-1", target="IV-2", strength=0.80,
                relationship_type="strong_support",
                mechanism="Good clinical outcomes improve patient satisfaction"
            ),
            CausalRelationship(
                source="IV-3", target="IV-1", strength=0.70,
                relationship_type="strong_support",
                mechanism="Engaged workforce delivers better outcomes"
            ),
            CausalRelationship(
                source="IV-5", target="IV-6", strength=0.65,
                relationship_type="strong_support",
                mechanism="Efficient processes improve financial results"
            ),
        ]
    
    def get_framework(self) -> StandardsFramework:
        """Get the complete standards framework."""
        return self._framework
    
    def get_parts(self) -> List[Part]:
        """Get all parts."""
        return self._framework.parts
    
    def get_part(self, part_number: str) -> Optional[Part]:
        """Get a specific part by number."""
        for part in self._framework.parts:
            if part.number == part_number:
                return part
        return None
    
    def get_chapter(self, chapter_id: str) -> Optional[Chapter]:
        """Get a specific chapter by ID (e.g., 'I-1', 'II-4')."""
        for part in self._framework.parts:
            for chapter in part.chapters:
                if chapter.id == chapter_id:
                    return chapter
        return None
    
    def get_all_chapters(self) -> List[Chapter]:
        """Get all chapters across all parts."""
        chapters = []
        for part in self._framework.parts:
            chapters.extend(part.chapters)
        return chapters
    
    def get_all_criteria(self) -> List[Criterion]:
        """Get all criteria across all chapters."""
        criteria = []
        for part in self._framework.parts:
            for chapter in part.chapters:
                criteria.extend(chapter.criteria)
        return criteria
    
    def get_causal_relationships(self) -> List[CausalRelationship]:
        """Get all causal relationships."""
        return self._framework.causal_relationships
    
    def get_relationships_for_chapter(self, chapter_id: str) -> Dict[str, List[CausalRelationship]]:
        """Get relationships where the chapter is source or target."""
        incoming = []
        outgoing = []
        for rel in self._framework.causal_relationships:
            if rel.target == chapter_id:
                incoming.append(rel)
            if rel.source == chapter_id:
                outgoing.append(rel)
        return {"incoming": incoming, "outgoing": outgoing}
    
    def get_graph_data(self) -> Dict:
        """Get data formatted for Cytoscape.js visualization."""
        nodes = []
        edges = []
        
        # Add chapter nodes
        for part in self._framework.parts:
            for chapter in part.chapters:
                nodes.append({
                    "data": {
                        "id": chapter.id,
                        "label": f"{chapter.id}\n{chapter.name}",
                        "name": chapter.name,
                        "part": part.number,
                        "partName": part.name,
                        "weight": chapter.weight,
                        "focus": chapter.focus,
                        "color": part.color,
                        "criteriaCount": len(chapter.criteria),
                        "essentialCount": sum(1 for c in chapter.criteria if c.category == CriterionCategory.ESSENTIAL),
                        "coreCount": sum(1 for c in chapter.criteria if c.category == CriterionCategory.CORE),
                    }
                })
        
        # Add relationship edges
        for rel in self._framework.causal_relationships:
            edges.append({
                "data": {
                    "id": f"{rel.source}->{rel.target}",
                    "source": rel.source,
                    "target": rel.target,
                    "strength": rel.strength,
                    "type": rel.relationship_type,
                    "mechanism": rel.mechanism,
                    "width": 1 + rel.strength * 4,  # Width based on strength
                }
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
        }


# Singleton instance
standards_service = StandardsService()


def get_standards_service() -> StandardsService:
    """Get the standards service singleton instance."""
    return standards_service

