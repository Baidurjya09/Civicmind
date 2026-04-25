"""
Evaluation Engine for CivicMind Training Pipeline
Provides evaluation functionality for Colab notebook integration.
"""

import json
import random
from typing import Dict, List, Callable, Any
from pathlib import Path
from dataclasses import dataclass, field

from environment import CivicMindEnv, CivicMindConfig
from agents.agent_definitions import ALL_AGENTS


@dataclass
class EpisodeResult:
    """Results from a single episode evaluation."""
    policy_name: str
    rewards: List[float] = field(default_factory=list)
    survival_rates: List[float] = field(default_factory=list)
    trust_scores: List[float] = field(default_factory=list)
    gdp_indices: List[float] = field(default_factory=list)
    rebel_spawned: bool = False
    rebel_defeated: bool = False
    weeks_survived: int = 0
    city_collapsed: bool = False

    @property
    def mean_reward(self) -> float:
        return sum(self.rewards) / len(self.rewards) if self.rewards else 0.0

    @property
    def final_reward(self) -> float:
        return self.rewards[-1] if self.rewards else 0.0

    def summary(self) -> dict:
        return {
            "policy": self.policy_name,
            "mean_reward": round(self.mean_reward, 4),
            "final_reward": round(self.final_reward, 4),
            "final_survival": round(self.survival_rates[-1] if self.survival_rates else 0, 4),
            "final_trust": round(self.trust_scores[-1] if self.trust_scores else 0, 4),
            "final_gdp": round(self.gdp_indices[-1] if self.gdp_indices else 0, 4),
            "rebel_spawned": self.rebel_spawned,
            "rebel_defeated": self.rebel_defeated,
            "weeks_survived": self.weeks_survived,
            "city_collapsed": self.city_collapsed,
        }


class EvaluationEngine:
    """
    Evaluation engine for CivicMind training pipeline.
    
    Evaluates policies by running multiple episodes and comparing metrics:
    - Mean reward
    - Final reward
    - Survival rate
    - Trust score
    - Rebel spawn rate
    
    Usage:
        engine = EvaluationEngine(n_episodes=5, max_weeks=20, difficulty=3)
        
        # Evaluate single policy
        results = engine.evaluate_policy(policy_fn, "My Policy")
        
        # Compare multiple policies
        comparison = engine.compare_policies({
            "random": random_policy_fn,
            "trained": trained_policy_fn
        })
    """
    
    def __init__(self, n_episodes: int = 5, max_weeks: int = 20, difficulty: int = 3):
        """
        Initialize evaluation engine.
        
        Args:
            n_episodes: Number of episodes to run per policy
            max_weeks: Maximum weeks per episode
            difficulty: Environment difficulty (1-5)
        """
        self.n_episodes = n_episodes
        self.max_weeks = max_weeks
        self.difficulty = difficulty
    
    def run_episode(
        self,
        policy_fn: Callable,
        policy_name: str,
        seed: int = 42,
        verbose: bool = False
    ) -> EpisodeResult:
        """
        Run a single episode with the given policy.
        
        Args:
            policy_fn: Policy function that takes (agent_id, observation) and returns action dict
            policy_name: Name of the policy for tracking
            seed: Random seed for reproducibility
            verbose: Whether to print progress
            
        Returns:
            EpisodeResult with metrics from the episode
        """
        env = CivicMindEnv(CivicMindConfig(
            max_weeks=self.max_weeks,
            difficulty=self.difficulty,
            seed=seed,
            enable_rebel=True,
            enable_schema_drift=True,
        ))
        
        obs = env.reset()
        result = EpisodeResult(policy_name=policy_name)
        
        if verbose:
            print(f"  Running episode (seed={seed})...")
        
        while not env.done:
            # Get actions from policy for all agents
            actions = {}
            for agent_id in env.AGENT_IDS:
                action_dict = policy_fn(agent_id, obs[agent_id])
                actions[agent_id] = action_dict
            
            # Step environment
            obs, reward, done, info = env.step(actions)
            
            # Record metrics
            result.rewards.append(reward)
            result.survival_rates.append(env.city.survival_rate)
            result.trust_scores.append(env.city.trust_score)
            result.gdp_indices.append(env.city.gdp_index)
            
            # Track rebel status
            if env.rebel_active:
                result.rebel_spawned = True
            if not env.rebel_active and result.rebel_spawned:
                result.rebel_defeated = True
            
            result.weeks_survived = info["week"]
            result.city_collapsed = (
                env.city.survival_rate < 0.5 or 
                env.city.rebel_strength > 0.9
            )
        
        return result
    
    def evaluate_policy(
        self,
        policy_fn: Callable,
        policy_name: str,
        seeds: List[int] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a policy over multiple episodes.
        
        Args:
            policy_fn: Policy function
            policy_name: Name of the policy
            seeds: List of seeds (defaults to [42, 43, 44, 45, 46])
            
        Returns:
            Dictionary with aggregate statistics
        """
        if seeds is None:
            seeds = [42 + i for i in range(self.n_episodes)]
        
        results = []
        for i, seed in enumerate(seeds):
            verbose = (i == 0)  # Only verbose for first episode
            result = self.run_episode(policy_fn, policy_name, seed=seed, verbose=verbose)
            results.append(result)
        
        # Aggregate statistics
        mean_rewards = [r.mean_reward for r in results]
        final_rewards = [r.final_reward for r in results]
        survivals = [r.survival_rates[-1] if r.survival_rates else 0 for r in results]
        trusts = [r.trust_scores[-1] if r.trust_scores else 0 for r in results]
        rebels = sum(1 for r in results if r.rebel_spawned)
        collapses = sum(1 for r in results if r.city_collapsed)
        
        return {
            "policy": policy_name,
            "n_episodes": len(results),
            "mean_reward_avg": round(sum(mean_rewards) / len(results), 4),
            "final_reward_avg": round(sum(final_rewards) / len(results), 4),
            "survival_avg": round(sum(survivals) / len(results), 4),
            "trust_avg": round(sum(trusts) / len(results), 4),
            "rebel_rate": round(rebels / len(results), 3),
            "collapse_rate": round(collapses / len(results), 3),
            "episode_results": [r.summary() for r in results],
        }
    
    def compare_policies(
        self,
        policies: Dict[str, Callable]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare multiple policies.
        
        Args:
            policies: Dictionary mapping policy names to policy functions
            
        Returns:
            Dictionary mapping policy names to their evaluation results
        """
        results = {}
        
        for policy_name, policy_fn in policies.items():
            print(f"\n📊 Evaluating {policy_name}...")
            stats = self.evaluate_policy(policy_fn, policy_name)
            results[policy_name] = stats
            print(f"   Mean reward: {stats['mean_reward_avg']:.4f}")
            print(f"   Final reward: {stats['final_reward_avg']:.4f}")
            print(f"   Survival rate: {stats['survival_avg']:.1%}")
        
        return results
    
    def save_results(self, results: Dict[str, Any], path: str) -> None:
        """
        Save evaluation results to JSON file.
        
        Args:
            results: Results dictionary from evaluate_policy or compare_policies
            path: Output file path
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ Results saved to: {path}")


# Policy implementations for baseline comparison
def random_policy(agent_id: str, observation: dict) -> dict:
    """Random baseline policy."""
    agent = ALL_AGENTS[agent_id]
    decision = random.choice(agent.valid_decisions)
    return {
        "reasoning": "Random baseline policy.",
        "tool_calls": [],
        "policy_decision": decision,
    }


def heuristic_policy(agent_id: str, observation: dict) -> dict:
    """Rule-based heuristic policy."""
    active_crises = observation.get("active_crises", [])
    rebel = observation.get("rebel_active", False)
    trust = observation.get("trust_score", 0.7)
    
    rules = {
        "mayor": lambda o: (
            "emergency_budget_release"
            if o.get("budget_remaining", 1e6) < 200_000 or active_crises
            else "hold"
        ),
        "health_minister": lambda o: (
            "mass_vaccination"
            if o.get("disease_prevalence", 0) > 0.08
            else "increase_hospital_staff"
            if o.get("hospital_capacity", 1) < 0.60
            else "hold"
        ),
        "finance_officer": lambda o: (
            "issue_bonds"
            if o.get("budget_remaining", 1e6) < 150_000
            else "stimulus_package"
            if o.get("gdp_index", 1) < 0.70
            else "hold"
        ),
        "police_chief": lambda o: (
            "community_policing"
            if o.get("crime_index", 0) > 0.30 or rebel
            else "hold"
        ),
        "infrastructure_head": lambda o: (
            "emergency_repairs"
            if o.get("power_grid_health", 1) < 0.55
            else "hold"
        ),
        "media_spokesperson": lambda o: (
            "press_conference"
            if o.get("misinformation_level", 0) > 0.30 or rebel
            else "social_media_campaign"
            if trust < 0.55
            else "hold"
        ),
    }
    
    fn = rules.get(agent_id, lambda o: "hold")
    decision = fn(observation)
    
    return {
        "reasoning": f"Heuristic: crisis={bool(active_crises)}, rebel={rebel}, trust={trust:.2f}",
        "tool_calls": [],
        "policy_decision": decision,
    }
