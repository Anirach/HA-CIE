"""
Hospital Service - CRUD operations for hospitals.
Uses JSON file storage for development mode.
"""
import json
import os
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

from app.models.hospital import Hospital, HospitalType, Ownership, Region
from app.core.config import settings


class HospitalService:
    """Service for managing hospital data."""
    
    def __init__(self):
        self._data_dir = Path(settings.data_dir)
        self._hospitals_file = self._data_dir / "hospitals.json"
        self._ensure_data_dir()
        self._hospitals: Dict[str, Hospital] = {}
        self._load_hospitals()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists."""
        self._data_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_hospitals(self):
        """Load hospitals from JSON file."""
        if self._hospitals_file.exists():
            try:
                with open(self._hospitals_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for h_data in data:
                        hospital = Hospital(**h_data)
                        self._hospitals[hospital.id] = hospital
            except Exception as e:
                print(f"Error loading hospitals: {e}")
                self._hospitals = {}
        
        # Initialize with sample data if empty
        if not self._hospitals:
            self._init_sample_data()
    
    def _save_hospitals(self):
        """Save hospitals to JSON file."""
        data = [h.model_dump() for h in self._hospitals.values()]
        with open(self._hospitals_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
    
    def _init_sample_data(self):
        """Initialize with sample hospital data."""
        sample_hospitals = [
            Hospital(
                id="hosp-001",
                name="Sample General Hospital",
                name_th="โรงพยาบาลตัวอย่าง",
                bed_count=500,
                hospital_type=HospitalType.GENERAL,
                region=Region.CENTRAL,
                ownership=Ownership.PUBLIC,
                province="Nonthaburi",
                has_emergency=True,
                has_icu=True,
                has_surgery=True,
                has_obstetrics=True,
                has_pediatrics=True,
                first_accreditation_year=2018,
                current_accreditation_level="Good",
            ),
            Hospital(
                id="hosp-002",
                name="Community Care Hospital",
                name_th="โรงพยาบาลชุมชนดูแล",
                bed_count=200,
                hospital_type=HospitalType.COMMUNITY,
                region=Region.NORTHEASTERN,
                ownership=Ownership.PUBLIC,
                province="Khon Kaen",
                has_emergency=True,
                has_icu=True,
                has_surgery=True,
                has_obstetrics=True,
                has_pediatrics=True,
                first_accreditation_year=2020,
                current_accreditation_level="Pass",
            ),
            Hospital(
                id="hosp-003",
                name="University Medical Center",
                name_th="ศูนย์การแพทย์มหาวิทยาลัย",
                bed_count=800,
                hospital_type=HospitalType.UNIVERSITY,
                region=Region.BANGKOK,
                ownership=Ownership.PUBLIC,
                province="Bangkok",
                has_emergency=True,
                has_icu=True,
                has_surgery=True,
                has_obstetrics=True,
                has_pediatrics=True,
                first_accreditation_year=2015,
                current_accreditation_level="Excellent",
            ),
        ]
        
        for hospital in sample_hospitals:
            self._hospitals[hospital.id] = hospital
        
        self._save_hospitals()
    
    def get_all(self) -> List[Hospital]:
        """Get all hospitals."""
        return list(self._hospitals.values())
    
    def get_by_id(self, hospital_id: str) -> Optional[Hospital]:
        """Get hospital by ID."""
        return self._hospitals.get(hospital_id)
    
    def create(self, hospital: Hospital) -> Hospital:
        """Create a new hospital."""
        hospital.created_at = datetime.utcnow()
        hospital.updated_at = datetime.utcnow()
        self._hospitals[hospital.id] = hospital
        self._save_hospitals()
        return hospital
    
    def update(self, hospital_id: str, updates: dict) -> Optional[Hospital]:
        """Update a hospital."""
        hospital = self._hospitals.get(hospital_id)
        if not hospital:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(hospital, key) and key not in ['id', 'created_at']:
                setattr(hospital, key, value)
        
        hospital.updated_at = datetime.utcnow()
        self._hospitals[hospital_id] = hospital
        self._save_hospitals()
        return hospital
    
    def delete(self, hospital_id: str) -> bool:
        """Delete a hospital."""
        if hospital_id in self._hospitals:
            del self._hospitals[hospital_id]
            self._save_hospitals()
            return True
        return False
    
    def search(
        self,
        name: Optional[str] = None,
        hospital_type: Optional[HospitalType] = None,
        region: Optional[Region] = None,
        ownership: Optional[Ownership] = None,
        min_beds: Optional[int] = None,
        max_beds: Optional[int] = None,
    ) -> List[Hospital]:
        """Search hospitals with filters."""
        results = list(self._hospitals.values())
        
        if name:
            name_lower = name.lower()
            results = [h for h in results if name_lower in h.name.lower() or 
                       (h.name_th and name_lower in h.name_th.lower())]
        
        if hospital_type:
            results = [h for h in results if h.hospital_type == hospital_type]
        
        if region:
            results = [h for h in results if h.region == region]
        
        if ownership:
            results = [h for h in results if h.ownership == ownership]
        
        if min_beds is not None:
            results = [h for h in results if h.bed_count >= min_beds]
        
        if max_beds is not None:
            results = [h for h in results if h.bed_count <= max_beds]
        
        return results
    
    def get_statistics(self) -> dict:
        """Get statistics about hospitals."""
        hospitals = list(self._hospitals.values())
        
        if not hospitals:
            return {
                "total": 0,
                "by_type": {},
                "by_region": {},
                "by_ownership": {},
                "avg_beds": 0,
            }
        
        by_type = {}
        by_region = {}
        by_ownership = {}
        total_beds = 0
        
        for h in hospitals:
            by_type[h.hospital_type.value] = by_type.get(h.hospital_type.value, 0) + 1
            by_region[h.region.value] = by_region.get(h.region.value, 0) + 1
            by_ownership[h.ownership.value] = by_ownership.get(h.ownership.value, 0) + 1
            total_beds += h.bed_count
        
        return {
            "total": len(hospitals),
            "by_type": by_type,
            "by_region": by_region,
            "by_ownership": by_ownership,
            "avg_beds": round(total_beds / len(hospitals), 1),
            "total_beds": total_beds,
        }


# Singleton instance
hospital_service = HospitalService()


