"""
CivicMind — Citizen Engine (Theme 3.2: Personalized Tasks + Patronus AI Bonus)
Generates citizen petitions with schema drift across 52 weeks.
5 schema versions that evolve over time.
"""

import random
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Petition:
    """Citizen petition with schema version"""
    citizen_id: int
    week: int
    schema_version: str
    urgency_normalized: float  # Always 0-1
    raw: Dict[str, Any]  # Raw petition data


class CitizenEngine:
    """
    Generates personalized citizen petitions.
    Theme 3.2: Personalized Tasks
    Patronus AI Bonus: Schema drift across 5 versions
    """
    
    COMPLAINT_TYPES = [
        "healthcare_access", "crime_safety", "infrastructure_failure",
        "unemployment", "housing_crisis", "education_quality",
        "corruption_report", "environmental_issue", "tax_burden",
        "public_service_failure"
    ]
    
    def __init__(self, schema_drift: bool = True, seed: int = 42):
        self.schema_drift = schema_drift
        self.rng = random.Random(seed)
        self.petition_count = 0
    
    def reset(self):
        """Reset petition counter"""
        self.petition_count = 0
    
    def _get_schema_version(self, week: int) -> str:
        """
        Patronus AI Bonus: Schema drift
        Week 1-5:   v1 (simple)
        Week 6-10:  v2 (adds category)
        Week 11-20: v3 (numeric priority)
        Week 21-35: v4 (nested metadata)
        Week 36+:   v5 (enterprise JSON)
        """
        if not self.schema_drift:
            return "v1"
        
        if week <= 5:
            return "v1"
        elif week <= 10:
            return "v2"
        elif week <= 20:
            return "v3"
        elif week <= 35:
            return "v4"
        else:
            return "v5"
    
    def generate_petitions(self, week: int, city_state, count: int = 5) -> List[Petition]:
        """Generate citizen petitions for this week"""
        petitions = []
        schema_version = self._get_schema_version(week)
        
        for _ in range(count):
            petition = self._generate_single_petition(week, city_state, schema_version)
            petitions.append(petition)
        
        return petitions
    
    def _generate_single_petition(self, week: int, city_state, schema_version: str) -> Petition:
        """Generate one petition with appropriate schema"""
        self.petition_count += 1
        citizen_id = self.rng.randint(1, city_state.num_citizens)
        complaint_type = self.rng.choice(self.COMPLAINT_TYPES)
        
        # Base urgency (influenced by city state)
        base_urgency = self.rng.uniform(0.3, 0.9)
        if city_state.trust_score < 0.4:
            base_urgency += 0.2
        if city_state.survival_rate < 0.7:
            base_urgency += 0.3
        urgency_normalized = min(1.0, base_urgency)
        
        # Generate petition based on schema version
        if schema_version == "v1":
            raw = self._schema_v1(citizen_id, complaint_type, urgency_normalized)
        elif schema_version == "v2":
            raw = self._schema_v2(citizen_id, complaint_type, urgency_normalized)
        elif schema_version == "v3":
            raw = self._schema_v3(citizen_id, complaint_type, urgency_normalized)
        elif schema_version == "v4":
            raw = self._schema_v4(citizen_id, complaint_type, urgency_normalized)
        else:  # v5
            raw = self._schema_v5(citizen_id, complaint_type, urgency_normalized)
        
        return Petition(
            citizen_id=citizen_id,
            week=week,
            schema_version=schema_version,
            urgency_normalized=urgency_normalized,
            raw=raw,
        )
    
    def _schema_v1(self, cid: int, ctype: str, urgency: float) -> Dict:
        """Simple schema: just text"""
        return {
            "message": f"Citizen {cid} reports {ctype.replace('_', ' ')}. Urgency: {urgency:.0%}",
        }
    
    def _schema_v2(self, cid: int, ctype: str, urgency: float) -> Dict:
        """Adds category field"""
        return {
            "citizen_id": cid,
            "category": ctype,
            "message": f"Issue with {ctype.replace('_', ' ')}",
            "urgency": "high" if urgency > 0.7 else "medium" if urgency > 0.4 else "low",
        }
    
    def _schema_v3(self, cid: int, ctype: str, urgency: float) -> Dict:
        """Numeric priority score"""
        return {
            "id": cid,
            "type": ctype,
            "description": f"Complaint about {ctype}",
            "priority_score": int(urgency * 100),  # 0-100
            "timestamp": f"Week {self.petition_count}",
        }
    
    def _schema_v4(self, cid: int, ctype: str, urgency: float) -> Dict:
        """Nested metadata"""
        return {
            "citizen_id": cid,
            "complaint": ctype,
            "metadata": {
                "urgency_level": urgency,
                "requires_immediate_action": urgency > 0.8,
                "affected_services": [ctype.split('_')[0]],
            },
            "contact_info": f"citizen_{cid}@city.gov",
        }
    
    def _schema_v5(self, cid: int, ctype: str, urgency: float) -> Dict:
        """Enterprise JSON with nested structure"""
        return {
            "petition_id": f"PET-{self.petition_count:06d}",
            "submitter": {
                "citizen_id": cid,
                "verified": True,
            },
            "issue": {
                "category": ctype,
                "severity": "critical" if urgency > 0.8 else "high" if urgency > 0.6 else "medium",
                "description": f"Formal complaint regarding {ctype}",
            },
            "meta": {
                "submission_week": self.petition_count // 5,
                "priority_weight": urgency,
                "escalation_required": urgency > 0.75,
            },
        }
