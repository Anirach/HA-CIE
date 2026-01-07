"""Hospital data model."""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class HospitalType(str, Enum):
    """Hospital type classification."""
    GENERAL = "general"
    SPECIALTY = "specialty"
    UNIVERSITY = "university"
    COMMUNITY = "community"
    REGIONAL = "regional"
    PROVINCIAL = "provincial"


class Ownership(str, Enum):
    """Hospital ownership type."""
    PUBLIC = "public"
    PRIVATE = "private"
    FOUNDATION = "foundation"
    MILITARY = "military"


class Region(str, Enum):
    """Thailand regions."""
    CENTRAL = "central"
    NORTHERN = "northern"
    NORTHEASTERN = "northeastern"
    EASTERN = "eastern"
    WESTERN = "western"
    SOUTHERN = "southern"
    BANGKOK = "bangkok"


class Hospital(BaseModel):
    """Hospital model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    name_th: Optional[str] = None  # Thai name
    bed_count: int = 0
    hospital_type: HospitalType = HospitalType.GENERAL
    region: Region = Region.CENTRAL
    ownership: Ownership = Ownership.PUBLIC
    province: Optional[str] = None
    address: Optional[str] = None
    
    # Services offered
    has_emergency: bool = True
    has_icu: bool = True
    has_surgery: bool = True
    has_obstetrics: bool = True
    has_pediatrics: bool = True
    
    # Accreditation info
    first_accreditation_year: Optional[int] = None
    current_accreditation_level: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


