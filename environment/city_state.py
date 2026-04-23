"""
CivicMind — City State Management
Tracks all city metrics, handles state transitions, provides tool-callable methods.
"""

import random
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class CityState:
    """Complete city state with all metrics"""
    
    # Population
    num_citizens: int = 10_000
    survival_rate: float = 0.98
    
    # Economy
    gdp_index: float = 1.0
    inflation: float = 0.05
    unemployment: float = 0.08
    budget_remaining: float = 1_000_000.0
    
    # Social
    trust_score: float = 0.75
    public_satisfaction: float = 0.70
    misinformation_level: float = 0.15
    
    # Security
    crime_index: float = 0.15
    civil_unrest: float = 0.10
    
    # Infrastructure
    power_grid_health: float = 0.85
    hospital_capacity: float = 0.70
    
    # Health
    disease_prevalence: float = 0.02
    
    # Governance
    corruption: float = 0.10
    policy_effectiveness: float = 0.75
    
    # Rebel mechanics (Theme 5: Wild Card)
    rebel_active: bool = False
    rebel_strength: float = 0.0
    consecutive_low_trust_weeks: int = 0
    
    def reset(self):
        """Reset to initial state"""
        self.__init__()
    
    def metrics_dict(self) -> Dict[str, Any]:
        """Return all metrics as dict"""
        return {
            "num_citizens": self.num_citizens,
            "survival_rate": self.survival_rate,
            "gdp_index": self.gdp_index,
            "inflation": self.inflation,
            "unemployment": self.unemployment,
            "budget_remaining": self.budget_remaining,
            "trust_score": self.trust_score,
            "public_satisfaction": self.public_satisfaction,
            "misinformation_level": self.misinformation_level,
            "crime_index": self.crime_index,
            "civil_unrest": self.civil_unrest,
            "power_grid_health": self.power_grid_health,
            "hospital_capacity": self.hospital_capacity,
            "disease_prevalence": self.disease_prevalence,
            "corruption": self.corruption,
            "policy_effectiveness": self.policy_effectiveness,
            "rebel_active": self.rebel_active,
            "rebel_strength": self.rebel_strength,
        }
    
    # Tool-callable methods (Theme 3.1: Professional Tasks)
    
    def apply_tax_increase(self, amount: float = 50_000):
        """Increase taxes - gains budget but loses trust"""
        self.budget_remaining += amount
        self.trust_score -= 0.03
        self.civil_unrest += 0.02
        return {"success": True, "budget_change": amount, "trust_change": -0.03}
    
    def apply_tax_decrease(self, amount: float = 30_000):
        """Decrease taxes - loses budget but gains trust"""
        self.budget_remaining -= amount
        self.trust_score += 0.02
        self.gdp_index += 0.01
        return {"success": True, "budget_change": -amount, "trust_change": 0.02}
    
    def invest_in_welfare(self, amount: float = 100_000):
        """Invest in public welfare"""
        if self.budget_remaining < amount:
            return {"success": False, "reason": "insufficient_budget"}
        self.budget_remaining -= amount
        self.trust_score += 0.05
        self.public_satisfaction += 0.04
        self.survival_rate += 0.01
        return {"success": True, "amount": amount}
    
    def increase_hospital_capacity(self, amount: float = 80_000):
        """Build more hospitals"""
        if self.budget_remaining < amount:
            return {"success": False, "reason": "insufficient_budget"}
        self.budget_remaining -= amount
        self.hospital_capacity += 0.10
        self.disease_prevalence -= 0.01
        return {"success": True, "capacity_change": 0.10}
    
    def deploy_police(self, mode: str = "community"):
        """Deploy police - mode: 'community' or 'riot_control'"""
        if mode == "community":
            self.crime_index -= 0.05
            self.trust_score += 0.02
            return {"success": True, "mode": "community", "trust_change": 0.02}
        elif mode == "riot_control":
            self.civil_unrest -= 0.10
            self.trust_score -= 0.08  # Backfires!
            if self.rebel_active:
                self.rebel_strength += 0.10  # Makes rebel stronger!
            return {"success": True, "mode": "riot_control", "trust_change": -0.08}
        return {"success": False, "reason": "invalid_mode"}
    
    def launch_media_campaign(self, campaign_type: str = "trust"):
        """Launch media campaign"""
        if campaign_type == "trust":
            self.trust_score += 0.04
            self.misinformation_level -= 0.03
        elif campaign_type == "health":
            self.disease_prevalence -= 0.02
            self.public_satisfaction += 0.02
        elif campaign_type == "economic":
            self.gdp_index += 0.02
            self.unemployment -= 0.01
        return {"success": True, "type": campaign_type}
    
    def emergency_budget_release(self, amount: float = 150_000):
        """Emergency budget allocation"""
        if self.budget_remaining < amount:
            return {"success": False, "reason": "insufficient_budget"}
        self.budget_remaining -= amount
        self.trust_score += 0.06
        self.public_satisfaction += 0.05
        if self.rebel_active:
            self.rebel_strength -= 0.05  # Shows good faith
        return {"success": True, "amount": amount, "trust_change": 0.06}
    
    def repair_infrastructure(self, amount: float = 70_000):
        """Repair power grid and infrastructure"""
        if self.budget_remaining < amount:
            return {"success": False, "reason": "insufficient_budget"}
        self.budget_remaining -= amount
        self.power_grid_health += 0.15
        self.public_satisfaction += 0.03
        return {"success": True, "grid_change": 0.15}
    
    def anti_corruption_drive(self):
        """Launch anti-corruption campaign"""
        self.corruption -= 0.05
        self.trust_score += 0.03
        self.policy_effectiveness += 0.04
        return {"success": True, "corruption_change": -0.05}
    
    def issue_bonds(self, amount: float = 200_000):
        """Issue government bonds"""
        self.budget_remaining += amount
        self.gdp_index -= 0.02  # Slight economic drag
        return {"success": True, "amount": amount}
    
    def stimulus_package(self, amount: float = 120_000):
        """Economic stimulus"""
        if self.budget_remaining < amount:
            return {"success": False, "reason": "insufficient_budget"}
        self.budget_remaining -= amount
        self.gdp_index += 0.08
        self.unemployment -= 0.03
        self.trust_score += 0.02
        return {"success": True, "gdp_change": 0.08}
    
    def clamp_values(self):
        """Ensure all values stay in valid ranges"""
        self.survival_rate = max(0.0, min(1.0, self.survival_rate))
        self.gdp_index = max(0.3, min(2.0, self.gdp_index))
        self.trust_score = max(0.0, min(1.0, self.trust_score))
        self.public_satisfaction = max(0.0, min(1.0, self.public_satisfaction))
        self.crime_index = max(0.0, min(1.0, self.crime_index))
        self.civil_unrest = max(0.0, min(1.0, self.civil_unrest))
        self.power_grid_health = max(0.0, min(1.0, self.power_grid_health))
        self.hospital_capacity = max(0.0, min(1.0, self.hospital_capacity))
        self.disease_prevalence = max(0.0, min(1.0, self.disease_prevalence))
        self.corruption = max(0.0, min(1.0, self.corruption))
        self.misinformation_level = max(0.0, min(1.0, self.misinformation_level))
        self.rebel_strength = max(0.0, min(1.0, self.rebel_strength))
        self.budget_remaining = max(0.0, self.budget_remaining)
    
    def apply_natural_decay(self):
        """Natural decay/drift of metrics over time"""
        self.trust_score -= random.uniform(0.0, 0.02)
        self.power_grid_health -= random.uniform(0.0, 0.01)
        self.hospital_capacity -= random.uniform(0.0, 0.01)
        self.crime_index += random.uniform(0.0, 0.01)
        self.corruption += random.uniform(0.0, 0.005)
        self.misinformation_level += random.uniform(0.0, 0.01)
        self.clamp_values()
