"""
CivicMind — Crisis Engine (Theme 4: Self-Improvement)
Auto-escalating difficulty with 10 tiers.
Crises compound and escalate based on agent performance.
"""

import random
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Crisis:
    """Single crisis event"""
    name: str
    severity: float  # 0.0 - 1.0
    week_triggered: int
    duration: int  # weeks
    effects: Dict[str, float]
    resolved: bool = False


class CrisisEngine:
    """
    Manages crisis generation and escalation.
    Theme 4: Self-Improvement - difficulty auto-escalates.
    """
    
    CRISIS_TEMPLATES = [
        {
            "name": "Flood",
            "base_severity": 0.3,
            "effects": {"survival_rate": -0.05, "power_grid_health": -0.15, "budget_remaining": -50000},
        },
        {
            "name": "Disease Outbreak",
            "base_severity": 0.4,
            "effects": {"disease_prevalence": 0.10, "survival_rate": -0.08, "hospital_capacity": -0.20},
        },
        {
            "name": "Economic Recession",
            "base_severity": 0.5,
            "effects": {"gdp_index": -0.15, "unemployment": 0.08, "trust_score": -0.10},
        },
        {
            "name": "Power Grid Failure",
            "base_severity": 0.4,
            "effects": {"power_grid_health": -0.30, "public_satisfaction": -0.15, "gdp_index": -0.08},
        },
        {
            "name": "Labor Strike",
            "base_severity": 0.3,
            "effects": {"gdp_index": -0.10, "civil_unrest": 0.15, "trust_score": -0.08},
        },
        {
            "name": "Cyber Attack",
            "base_severity": 0.5,
            "effects": {"power_grid_health": -0.20, "trust_score": -0.12, "budget_remaining": -80000},
        },
        {
            "name": "Food Shortage",
            "base_severity": 0.6,
            "effects": {"survival_rate": -0.10, "civil_unrest": 0.20, "trust_score": -0.15},
        },
        {
            "name": "Corruption Scandal",
            "base_severity": 0.4,
            "effects": {"corruption": 0.15, "trust_score": -0.20, "policy_effectiveness": -0.10},
        },
        {
            "name": "Mass Protest",
            "base_severity": 0.3,
            "effects": {"civil_unrest": 0.25, "trust_score": -0.10, "crime_index": 0.08},
        },
        {
            "name": "Infrastructure Collapse",
            "base_severity": 0.7,
            "effects": {"power_grid_health": -0.40, "survival_rate": -0.12, "budget_remaining": -150000},
        },
    ]
    
    def __init__(self, difficulty: int = 1, seed: int = 42):
        """
        difficulty: 1-10 (Theme 4: auto-escalates)
        """
        self.difficulty = max(1, min(10, difficulty))
        self.seed = seed
        self.rng = random.Random(seed)
        self.all_crises: List[Crisis] = []
        self.active_crises: List[Crisis] = []
    
    def reset(self, difficulty: int = None):
        """Reset and generate crises for new episode"""
        if difficulty is not None:
            self.difficulty = max(1, min(10, difficulty))
        self.all_crises = []
        self.active_crises = []
        self._generate_crisis_schedule()
    
    def _generate_crisis_schedule(self):
        """Generate crisis schedule based on difficulty"""
        # Difficulty 1: 1 crisis
        # Difficulty 5: 3-4 crises
        # Difficulty 10: 6-8 crises, overlapping
        
        num_crises = min(1 + (self.difficulty // 2), 8)
        severity_multiplier = 1.0 + (self.difficulty - 1) * 0.15
        
        for i in range(num_crises):
            template = self.rng.choice(self.CRISIS_TEMPLATES)
            week = self.rng.randint(3, 40)  # Crises start after week 3
            duration = self.rng.randint(2, 6)
            severity = min(1.0, template["base_severity"] * severity_multiplier)
            
            # Scale effects by severity
            effects = {k: v * severity for k, v in template["effects"].items()}
            
            crisis = Crisis(
                name=template["name"],
                severity=severity,
                week_triggered=week,
                duration=duration,
                effects=effects,
                resolved=False,
            )
            self.all_crises.append(crisis)
        
        # Sort by week
        self.all_crises.sort(key=lambda c: c.week_triggered)
    
    def tick(self, current_week: int) -> List[Crisis]:
        """
        Advance one week, return newly triggered crises.
        """
        newly_triggered = []
        
        # Check for new crises
        for crisis in self.all_crises:
            if crisis.week_triggered == current_week and not crisis.resolved:
                self.active_crises.append(crisis)
                newly_triggered.append(crisis)
        
        # Remove expired crises
        self.active_crises = [
            c for c in self.active_crises
            if current_week < c.week_triggered + c.duration
        ]
        
        return newly_triggered
    
    def get_active_crises(self) -> List[Crisis]:
        """Return currently active crises"""
        return self.active_crises.copy()
    
    def resolve_crisis(self, crisis_name: str):
        """Mark a crisis as resolved"""
        for crisis in self.active_crises:
            if crisis.name == crisis_name:
                crisis.resolved = True
                self.active_crises.remove(crisis)
                return True
        return False
    
    def get_total_severity(self) -> float:
        """Sum of all active crisis severities"""
        return sum(c.severity for c in self.active_crises)
    
    def crisis_summary(self) -> Dict[str, Any]:
        """Summary of crisis state"""
        return {
            "active_count": len(self.active_crises),
            "total_severity": self.get_total_severity(),
            "active_names": [c.name for c in self.active_crises],
            "difficulty": self.difficulty,
        }
