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

from environment.civic_env import CivicMindEnv, CivicMindConfig
from agents.agent_definitions import ALL_AGENTS, build_agent_prompt


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
