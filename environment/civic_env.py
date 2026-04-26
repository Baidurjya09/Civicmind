"""
CivicMind — Main OpenEnv Environment
Covers ALL 5 hackathon themes in one integrated system.
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple

from .city_state import CityState
from .crisis_engine import CrisisEngine
from .citizen_engine import CitizenEngine
from .improvement_reward import calculate_improvement_reward
from .action_executor import ActionExecutor


@dataclass
class CivicMindConfig:
    """Environment configuration"""
    max_weeks: int = 52  # Theme 2: Long-horizon
    difficulty: int = 3  # Theme 4: Self-improvement (1-10)
    num_citizens: int = 10_000
    enable_rebel: bool = True  # Theme 5: Wild card
    enable_schema_drift: bool = True  # Patronus AI bonus
    seed: int = 42


class CivicMindEnv:
    """
    CivicMind OpenEnv Environment
    
    Theme 1: Multi-Agent - 6 government agents + oversight + rebel
    Theme 2: Long-Horizon - 52-week simulation with compound effects
    Theme 3.1: Professional - Real tool calls via APIs
    Theme 3.2: Personal - Citizen petitions with schema drift
    Theme 4: Self-Improvement - Auto-escalating difficulty
    Theme 5: Wild Card - Emergent rebel agent spawns
    """
    
    AGENT_IDS = [
        "mayor",
        "health_minister",
        "finance_officer",
        "police_chief",
        "infrastructure_head",
        "media_spokesperson",
    ]
    
    def __init__(self, config: CivicMindConfig = None):
        self.config = config or CivicMindConfig()
        
        # Core state
        self.city = CityState()
        self.city.num_citizens = self.config.num_citizens
        
        # Engines
        self.crisis_engine = CrisisEngine(
            difficulty=self.config.difficulty,
            seed=self.config.seed
        )
        self.citizen_engine = CitizenEngine(
            schema_drift=self.config.enable_schema_drift,
            seed=self.config.seed + 1
        )
        
        # Action executor (connects LLM outputs to state changes)
        self.action_executor = ActionExecutor()
        
        # Episode state
        self.current_week = 0
        self.done = False
        self.rebel_active = False
        self.rebel_spawn_week = -1
        
        # History
        self.episode_history = []
        
        random.seed(self.config.seed)
    
    def reset(self) -> Dict[str, Dict]:
        """Reset environment, return initial observations"""
        self.city.reset()
        self.city.num_citizens = self.config.num_citizens
        self.crisis_engine.reset(self.config.difficulty)
        self.citizen_engine.reset()
        self.action_executor.reset()
        
        self.current_week = 0
        self.done = False
        self.rebel_active = False
        self.rebel_spawn_week = -1
        self.episode_history = []
        
        return self._get_observations()
    
    def step(self, actions: Dict[str, Dict]) -> Tuple[Dict, float, bool, Dict]:
        """
        Execute one week of simulation.
        
        Args:
            actions: {agent_id: {reasoning, tool_calls, policy_decision}}
        
        Returns:
            observations, reward, done, info
        """
        self.current_week += 1
        
        # 1. Apply agent actions
        action_results = self._apply_actions(actions)
        
        # 2. Tick crisis engine
        new_crises = self.crisis_engine.tick(self.current_week)
        for crisis in new_crises:
            self._apply_crisis_effects(crisis)
        
        # 3. Natural decay
        self.city.apply_natural_decay()
        
        # 4. Check rebel spawn (Theme 5: Wild Card)
        if self.config.enable_rebel:
            self._check_rebel_spawn()
        
        # 5. Clamp values
        self.city.clamp_values()
        
        # 6. Calculate reward (using improvement-based reward function)
        reward = calculate_improvement_reward(self)
        
        # 7. Check termination
        self.done = (
            self.current_week >= self.config.max_weeks or
            self.city.survival_rate < 0.5 or
            self.city.rebel_strength > 0.9
        )
        
        # 8. Build info
        info = {
            "week": self.current_week,
            "new_crises": [c.name for c in new_crises],
            "rebel_active": self.rebel_active,
            "city_collapsed": self.city.survival_rate < 0.5,
        }
        
        # 9. Record history
        self.episode_history.append({
            "week": self.current_week,
            "reward": reward,
            "city_state": self.city.metrics_dict(),
            "actions": actions,
        })
        
        # 10. Get new observations
        observations = self._get_observations()
        
        return observations, reward, self.done, info
    
    def _get_observations(self) -> Dict[str, Dict]:
        """
        Build observations for each agent.
        Theme 3.1: Partial observability - each agent sees different info.
        """
        # Common info
        common = {
            "week": self.current_week,
            "max_weeks": self.config.max_weeks,
            "trust_score": self.city.trust_score,
            "survival_rate": self.city.survival_rate,
            "gdp_index": self.city.gdp_index,
            "budget_remaining": self.city.budget_remaining,
            "rebel_active": self.rebel_active,
            "active_crises": [c.name for c in self.crisis_engine.get_active_crises()],
        }
        
        # Agent-specific observations (partial observability)
        obs = {}
        
        obs["mayor"] = {
            **common,
            "policy_effectiveness": self.city.policy_effectiveness,
            "corruption": self.city.corruption,
            "civil_unrest": self.city.civil_unrest,
        }
        
        obs["health_minister"] = {
            **common,
            "disease_prevalence": self.city.disease_prevalence,
            "hospital_capacity": self.city.hospital_capacity,
            "survival_rate": self.city.survival_rate,
        }
        
        obs["finance_officer"] = {
            **common,
            "unemployment": self.city.unemployment,
            "inflation": self.city.inflation,
            "budget_remaining": self.city.budget_remaining,
        }
        
        obs["police_chief"] = {
            **common,
            "crime_index": self.city.crime_index,
            "civil_unrest": self.city.civil_unrest,
            "rebel_active": self.rebel_active,
        }
        
        obs["infrastructure_head"] = {
            **common,
            "power_grid_health": self.city.power_grid_health,
            "hospital_capacity": self.city.hospital_capacity,
        }
        
        obs["media_spokesperson"] = {
            **common,
            "misinformation_level": self.city.misinformation_level,
            "public_satisfaction": self.city.public_satisfaction,
            "trust_score": self.city.trust_score,
            # Theme 3.2: Personalized tasks - citizen petitions
            "citizen_petitions": [
                p.raw for p in self.citizen_engine.generate_petitions(
                    self.current_week, self.city, count=3
                )
            ],
        }
        
        return obs
    
    def _apply_actions(self, actions: Dict[str, Dict]) -> Dict:
        """Apply agent actions to city state using ActionExecutor"""
        # Use the action executor to properly connect LLM outputs to state changes
        results = self.action_executor.execute_all(actions, self.city)
        return results
    
    def _apply_crisis_effects(self, crisis):
        """Apply crisis effects to city state"""
        for metric, change in crisis.effects.items():
            if hasattr(self.city, metric):
                current = getattr(self.city, metric)
                setattr(self.city, metric, current + change)
    
    def _check_rebel_spawn(self):
        """
        Theme 5: Wild Card - Emergent rebel agent
        Spawns when trust < 0.30 for 2+ consecutive weeks
        """
        if self.city.trust_score < 0.30:
            self.city.consecutive_low_trust_weeks += 1
        else:
            self.city.consecutive_low_trust_weeks = max(
                0, self.city.consecutive_low_trust_weeks - 1
            )
        
        # Spawn rebel
        if (self.city.consecutive_low_trust_weeks >= 2 and 
            not self.rebel_active):
            self.rebel_active = True
            self.city.rebel_active = True
            self.city.rebel_strength = 0.10
            self.rebel_spawn_week = self.current_week
        
        # Grow rebel if active
        if self.rebel_active:
            if self.city.trust_score < 0.30:
                self.city.rebel_strength += 0.06
            elif self.city.trust_score < 0.45:
                self.city.rebel_strength += 0.02
            else:
                self.city.rebel_strength -= 0.04  # De-escalate
            
            # Defeat condition
            if self.city.rebel_strength < 0.02 and self.city.trust_score > 0.55:
                self.rebel_active = False
                self.city.rebel_active = False
    
    def _calculate_reward(self) -> float:
        """
        Calculate composite reward (bounded 0-1).
        Theme 2: Long-horizon - reward considers long-term effects.
        """
        # Survival (40%)
        survival_component = self.city.survival_rate * 0.4
        
        # Trust (30%)
        trust_component = self.city.trust_score * 0.3
        
        # Economy (20%)
        gdp_component = (self.city.gdp_index / 1.5) * 0.2
        
        # Security (10%)
        security_component = (1 - self.city.crime_index) * 0.1
        
        # Penalties
        rebel_penalty = self.city.rebel_strength * 0.2 if self.rebel_active else 0
        crisis_penalty = self.crisis_engine.get_total_severity() * 0.05
        
        reward = (
            survival_component +
            trust_component +
            gdp_component +
            security_component -
            rebel_penalty -
            crisis_penalty
        )
        
        return max(0.0, min(1.0, reward))
    
    def render(self) -> str:
        """Render current state as string"""
        lines = [
            f"Week {self.current_week}/{self.config.max_weeks}",
            f"Trust: {self.city.trust_score:.0%} | Survival: {self.city.survival_rate:.0%} | GDP: {self.city.gdp_index:.2f}",
            f"Budget: ${self.city.budget_remaining:,.0f}",
            f"Crises: {len(self.crisis_engine.get_active_crises())}",
        ]
        if self.rebel_active:
            lines.append(f"⚡ REBEL ACTIVE (strength: {self.city.rebel_strength:.0%})")
        return "\n".join(lines)
