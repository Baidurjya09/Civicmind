"""
CivicMind — Training Dataset Generator
Generates synthetic episodes for training.
"""

import json
import random
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tqdm import tqdm
from environment.civic_env import CivicMindEnv, CivicMindConfig
from agents.agent_definitions import ALL_AGENTS, build_agent_prompt


class DatasetGenerator:
    """
    Dataset generator for CivicMind training data.
    
    Creates synthetic training samples with configurable good/bad action ratio
    across all 6 agent types (mayor, health_minister, finance_officer, 
    police_chief, infrastructure_head, media_spokesperson).
    
    Good actions include:
    - Welfare investment (invest_in_welfare)
    - Trust building (press_conference, community_policing, social_media_campaign)
    - Crisis response (mass_vaccination, emergency_repairs, emergency_budget_release)
    
    Bad actions include:
    - Tax increases during low trust (increase_tax)
    - Riot control (deploy_riot_control)
    - Inaction during crisis (hold when action is needed)
    
    Usage:
        generator = DatasetGenerator(n_samples=500, good_ratio=0.7)
        samples = generator.generate_dataset()
        generator.save_dataset("training/civicmind_dataset.jsonl")
        stats = generator.get_statistics()
    """
    
    def __init__(self, n_samples: int = 500, good_ratio: float = 0.7, seed: int = 42):
        """
        Initialize dataset generator.
        
        Args:
            n_samples: Total number of samples to generate
            good_ratio: Ratio of good actions (0.0 to 1.0)
            seed: Random seed for reproducibility
        """
        self.n_samples = n_samples
        self.good_ratio = good_ratio
        self.seed = seed
        self.samples = []
        
        # Initialize environment
        random.seed(seed)
        self.env = CivicMindEnv(CivicMindConfig(max_weeks=12, difficulty=3, seed=seed))
        self.obs = self.env.reset()
        
        # Agent types (exclude oversight agent)
        self.agent_types = [
            "mayor",
            "health_minister", 
            "finance_officer",
            "police_chief",
            "infrastructure_head",
            "media_spokesperson"
        ]
    
    def generate_sample(self, agent_id: str, is_good: bool) -> dict:
        """
        Generate a single training sample.
        
        Args:
            agent_id: ID of the agent (e.g., "mayor", "health_minister")
            is_good: Whether to generate a good (True) or bad (False) action
            
        Returns:
            Dictionary with prompt, completion, agent_id, decision, is_good_action, reward
        """
        agent = ALL_AGENTS[agent_id]
        prompt = build_agent_prompt(agent_id, self.obs[agent_id])
        
        # Choose action based on is_good
        if is_good:
            # Good actions: welfare investment, trust building, crisis response
            if agent_id == "mayor":
                if self.obs[agent_id].get("budget_remaining", 1e6) < 200_000:
                    decision = "emergency_budget_release"
                elif self.obs[agent_id].get("trust_score", 0.75) < 0.4:
                    decision = "reduce_tax"
                else:
                    decision = "hold"
            elif agent_id == "health_minister":
                if self.obs[agent_id].get("disease_prevalence", 0) > 0.08:
                    decision = "mass_vaccination"
                elif self.obs[agent_id].get("hospital_capacity", 1) < 0.60:
                    decision = "increase_hospital_staff"
                else:
                    decision = "invest_in_welfare"
            elif agent_id == "finance_officer":
                if self.obs[agent_id].get("budget_remaining", 1e6) < 150_000:
                    decision = "issue_bonds"
                elif self.obs[agent_id].get("gdp_index", 1) < 0.70:
                    decision = "stimulus_package"
                else:
                    decision = "hold"
            elif agent_id == "police_chief":
                if self.obs[agent_id].get("crime_index", 0) > 0.30:
                    decision = "community_policing"  # Good choice - trust building
                else:
                    decision = "hold"
            elif agent_id == "infrastructure_head":
                if self.obs[agent_id].get("power_grid_health", 1) < 0.55:
                    decision = "emergency_repairs"  # Crisis response
                else:
                    decision = "hold"
            elif agent_id == "media_spokesperson":
                if self.obs[agent_id].get("trust_score", 0.75) < 0.55:
                    decision = "press_conference"  # Trust building
                else:
                    decision = "social_media_campaign"
            else:
                decision = "hold"
        else:
            # Bad actions: tax increases during low trust, riot control, inaction during crisis
            bad_choices = {
                "mayor": ["increase_tax", "increase_tax"],  # Tax increase during low trust
                "health_minister": ["hold", "hold"],  # Inaction during crisis
                "finance_officer": ["increase_tax", "hold"],  # Tax increase or inaction
                "police_chief": ["deploy_riot_control"],  # Riot control - backfires!
                "infrastructure_head": ["hold"],  # Inaction during crisis
                "media_spokesperson": ["hold"],  # Inaction during crisis
            }
            decision = random.choice(bad_choices.get(agent_id, ["hold"]))
        
        # Build completion
        completion = json.dumps({
            "reasoning": f"{'Good' if is_good else 'Bad'} policy decision",
            "tool_calls": [],
            "policy_decision": decision,
        })
        
        # Calculate approximate reward
        if is_good:
            reward = random.uniform(0.55, 0.85)
        else:
            reward = random.uniform(0.25, 0.50)
        
        return {
            "prompt": prompt,
            "completion": completion,
            "agent_id": agent_id,
            "decision": decision,
            "is_good_action": is_good,
            "reward": reward,
        }
    
    def generate_dataset(self) -> list:
        """
        Generate full dataset with progress bar.
        
        Updates progress every 100 samples.
        
        Returns:
            List of sample dictionaries
        """
        self.samples = []
        
        # Use tqdm for progress bar
        with tqdm(total=self.n_samples, desc="Generating samples", unit="sample") as pbar:
            for i in range(self.n_samples):
                # Reset env periodically to get varied observations
                if i % 50 == 0:
                    self.obs = self.env.reset()
                
                # Choose agent (balanced distribution)
                agent_id = self.agent_types[i % len(self.agent_types)]
                
                # Choose if good or bad based on ratio
                is_good = random.random() < self.good_ratio
                
                # Generate sample
                sample = self.generate_sample(agent_id, is_good)
                self.samples.append(sample)
                
                # Update progress bar every sample
                pbar.update(1)
        
        return self.samples
    
    def save_dataset(self, path: str) -> None:
        """
        Save dataset in JSONL format.
        
        Args:
            path: Output file path (e.g., "training/civicmind_dataset.jsonl")
        """
        # Create parent directory if needed
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save in JSONL format
        with open(path, "w") as f:
            for sample in self.samples:
                f.write(json.dumps(sample) + "\n")
        
        print(f"✓ Saved {len(self.samples)} samples to: {path}")
    
    def get_statistics(self) -> dict:
        """
        Get dataset statistics.
        
        Returns:
            Dictionary with total samples, good/bad ratio, samples per agent
        """
        if not self.samples:
            return {
                "total_samples": 0,
                "good_samples": 0,
                "bad_samples": 0,
                "good_ratio": 0.0,
                "bad_ratio": 0.0,
                "samples_per_agent": {}
            }
        
        # Count good/bad
        good_count = sum(1 for s in self.samples if s["is_good_action"])
        bad_count = len(self.samples) - good_count
        
        # Count per agent
        samples_per_agent = {}
        for agent_id in self.agent_types:
            samples_per_agent[agent_id] = sum(1 for s in self.samples if s["agent_id"] == agent_id)
        
        return {
            "total_samples": len(self.samples),
            "good_samples": good_count,
            "bad_samples": bad_count,
            "good_ratio": good_count / len(self.samples),
            "bad_ratio": bad_count / len(self.samples),
            "samples_per_agent": samples_per_agent
        }


def generate_sample(env: CivicMindEnv, agent_id: str, observation: dict, is_good: bool) -> dict:
    """Generate one training sample"""
    agent = ALL_AGENTS[agent_id]
    prompt = build_agent_prompt(agent_id, observation)
    
    # Choose action based on is_good
    if is_good:
        # Good actions: appropriate responses
        if agent_id == "mayor":
            if observation.get("budget_remaining", 1e6) < 200_000:
                decision = "emergency_budget_release"
            elif observation.get("trust_score", 0.75) < 0.4:
                decision = "reduce_tax"
            else:
                decision = "hold"
        elif agent_id == "health_minister":
            if observation.get("disease_prevalence", 0) > 0.08:
                decision = "mass_vaccination"
            elif observation.get("hospital_capacity", 1) < 0.60:
                decision = "increase_hospital_staff"
            else:
                decision = "hold"
        elif agent_id == "finance_officer":
            if observation.get("budget_remaining", 1e6) < 150_000:
                decision = "issue_bonds"
            elif observation.get("gdp_index", 1) < 0.70:
                decision = "stimulus_package"
            else:
                decision = "hold"
        elif agent_id == "police_chief":
            if observation.get("crime_index", 0) > 0.30:
                decision = "community_policing"  # Good choice
            else:
                decision = "hold"
        elif agent_id == "infrastructure_head":
            if observation.get("power_grid_health", 1) < 0.55:
                decision = "emergency_repairs"
            else:
                decision = "hold"
        elif agent_id == "media_spokesperson":
            if observation.get("trust_score", 0.75) < 0.55:
                decision = "press_conference"
            else:
                decision = "hold"
        else:
            decision = "hold"
    else:
        # Bad actions: inappropriate or harmful
        bad_choices = {
            "mayor": ["increase_tax", "increase_tax"],  # Always bad
            "health_minister": ["hold", "hold"],  # Ignoring health crisis
            "finance_officer": ["increase_tax", "hold"],
            "police_chief": ["deploy_riot_control"],  # Backfires!
            "infrastructure_head": ["hold"],
            "media_spokesperson": ["hold"],
        }
        decision = random.choice(bad_choices.get(agent_id, ["hold"]))
    
    # Build completion
    completion = json.dumps({
        "reasoning": f"{'Good' if is_good else 'Bad'} policy decision",
        "tool_calls": [],
        "policy_decision": decision,
    })
    
    # Calculate approximate reward
    if is_good:
        reward = random.uniform(0.55, 0.85)
    else:
        reward = random.uniform(0.25, 0.50)
    
    return {
        "prompt": prompt,
        "completion": completion,
        "agent_id": agent_id,
        "decision": decision,
        "is_good_action": is_good,
        "reward": reward,
    }


def generate_dataset(
    n_samples: int = 500,
    output_path: str = "training/civicmind_dataset.jsonl",
    good_ratio: float = 0.70,
    seed: int = 42,
) -> str:
    """Generate training dataset"""
    random.seed(seed)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating {n_samples} training samples...")
    print(f"  Good actions: {int(n_samples * good_ratio)} ({good_ratio:.0%})")
    print(f"  Bad actions:  {int(n_samples * (1-good_ratio))} ({1-good_ratio:.0%})")
    
    env = CivicMindEnv(CivicMindConfig(max_weeks=12, difficulty=3, seed=seed))
    samples = []
    
    for i in range(n_samples):
        # Reset env periodically
        if i % 50 == 0:
            obs = env.reset()
        
        # Choose agent
        agent_id = random.choice(list(ALL_AGENTS.keys())[:-1])  # Exclude oversight
        
        # Choose if good or bad
        is_good = random.random() < good_ratio
        
        # Generate sample
        sample = generate_sample(env, agent_id, obs[agent_id], is_good)
        samples.append(sample)
        
        if (i + 1) % 100 == 0:
            print(f"  Generated {i+1}/{n_samples} samples...")
    
    # Save
    with open(output_path, "w") as f:
        for sample in samples:
            f.write(json.dumps(sample) + "\n")
    
    print(f"  Saved to: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_samples", type=int, default=500)
    parser.add_argument("--output", type=str, default="training/civicmind_dataset.jsonl")
    parser.add_argument("--good_ratio", type=float, default=0.70)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    
    generate_dataset(
        n_samples=args.n_samples,
        output_path=args.output,
        good_ratio=args.good_ratio,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
