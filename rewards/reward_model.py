"""
CivicMind — Reward Model (PyTorch)
Composite reward scorer with MLP shaper for dense intermediate rewards.
"""

import torch
import torch.nn as nn
from typing import Dict, Any


def city_metrics_to_tensor(metrics: Dict[str, Any]) -> torch.Tensor:
    """Convert city metrics dict to tensor"""
    features = [
        metrics.get("survival_rate", 0.98),
        metrics.get("trust_score", 0.75),
        metrics.get("gdp_index", 1.0) / 2.0,  # Normalize
        1 - metrics.get("crime_index", 0.15),
        1 - metrics.get("civil_unrest", 0.10),
        metrics.get("power_grid_health", 0.85),
        metrics.get("hospital_capacity", 0.70),
        1 - metrics.get("disease_prevalence", 0.02),
        1 - metrics.get("corruption", 0.10),
        metrics.get("policy_effectiveness", 0.75),
    ]
    return torch.tensor(features, dtype=torch.float32)


class RewardModel:
    """
    Composite reward model.
    Bounded [0, 1] for stable training.
    """
    
    def __init__(self):
        self.weights = {
            "survival": 0.40,
            "trust": 0.30,
            "economy": 0.20,
            "security": 0.10,
        }
    
    def compute(
        self,
        city_state,
        oversight_score: float = 0.75,
        crisis_resolved: bool = False,
        week: int = 1,
    ) -> float:
        """
        Calculate composite reward.
        
        Returns: float in [0, 1]
        """
        # Core components
        survival_component = city_state.survival_rate * self.weights["survival"]
        trust_component = city_state.trust_score * self.weights["trust"]
        economy_component = (city_state.gdp_index / 1.5) * self.weights["economy"]
        security_component = (1 - city_state.crime_index) * self.weights["security"]
        
        # Bonuses
        crisis_bonus = 0.05 if crisis_resolved else 0.0
        oversight_bonus = (oversight_score - 0.5) * 0.05  # Fleet AI bonus
        
        # Penalties
        rebel_penalty = city_state.rebel_strength * 0.20 if city_state.rebel_active else 0.0
        corruption_penalty = city_state.corruption * 0.05
        
        reward = (
            survival_component +
            trust_component +
            economy_component +
            security_component +
            crisis_bonus +
            oversight_bonus -
            rebel_penalty -
            corruption_penalty
        )
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, reward))


class RewardShaperMLP(nn.Module):
    """
    MLP for shaping intermediate rewards.
    Provides dense reward signal for training.
    """
    
    def __init__(self, input_dim: int = 10, hidden_dim: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid(),  # Output [0, 1]
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, input_dim) city metrics
        Returns:
            (batch, 1) shaped reward in [0, 1]
        """
        return self.net(x)
