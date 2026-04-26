"""
Collect training data for LLM agents
Runs episodes and collects (state, action, reward) tuples
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any
import random

sys.path.insert(0, str(Path(__file__).parent.parent))

from environment import CivicMindEnv, CivicMindConfig
from training.llm_agent_wrapper import LLMAgentWrapper


def collect_episode_data(env: CivicMindEnv, wrapper: LLMAgentWrapper, 
                        use_heuristic: bool = True) -> List[Dict[str, Any]]:
    """
    Collect training data from one episode.
    
    Args:
        env: CivicMind environment
        wrapper: LLM agent wrapper
        use_heuristic: If True, use heuristic policy; if False, use random
        
    Returns:
        List of training examples
    """
    examples = []
    
    obs = env.reset()
    done = False
    step = 0
    
    while not done and step < 20:
        # For each agent, generate action
        actions = {}
        step_examples = []
        
        for agent_id in env.AGENT_IDS:
            agent_obs = obs[agent_id]
            
            # Choose action (heuristic or random)
            if use_heuristic:
                action = choose_heuristic_action(agent_id, agent_obs)
            else:
                valid_actions = list(wrapper.AGENT_ACTIONS[agent_id].keys())
                action = random.choice(valid_actions)
            
            actions[agent_id] = {"policy_decision": action}
            
            # Store for later (we'll add reward after step)
            step_examples.append({
                "agent_id": agent_id,
                "observation": agent_obs.copy(),
                "action": action
            })
        
        # Take environment step
        next_obs, reward, done, info = env.step(actions)
        
        # Add reward to all examples from this step
        for example in step_examples:
            training_example = wrapper.create_training_example(
                example["agent_id"],
                example["observation"],
                example["action"],
                reward
            )
            examples.append(training_example)
        
        obs = next_obs
        step += 1
    
    return examples


def choose_heuristic_action(agent_id: str, observation: Dict[str, Any]) -> str:
    """
    Simple heuristic policy for data collection.
    
    Args:
        agent_id: Agent identifier
        observation: Agent observation
        
    Returns:
        Action string
    """
    trust = observation.get("trust_score", 0.5)
    survival = observation.get("survival_rate", 0.9)
    budget = observation.get("budget_remaining", 5000000)
    rebel_active = observation.get("rebel_active", False)
    crises = observation.get("active_crises", [])
    
    # Mayor: Focus on trust and budget
    if agent_id == "mayor":
        if trust < 0.4 and budget > 2000000:
            return "invest_in_welfare"
        elif budget > 5000000:
            return "reduce_tax"
        elif budget < 1000000:
            return "emergency_budget_release"
        else:
            return "hold"
    
    # Health Minister: Focus on survival
    elif agent_id == "health_minister":
        disease = observation.get("disease_prevalence", 0.0)
        if disease > 0.3:
            return "mass_vaccination"
        elif survival < 0.85:
            return "increase_hospital_staff"
        else:
            return "hold"
    
    # Finance Officer: Focus on economy
    elif agent_id == "finance_officer":
        gdp = observation.get("gdp_index", 1.0)
        unemployment = observation.get("unemployment", 0.05)
        if gdp < 0.9 or unemployment > 0.15:
            return "stimulus_package"
        elif budget < 2000000:
            return "issue_bonds"
        else:
            return "hold"
    
    # Police Chief: Focus on security
    elif agent_id == "police_chief":
        crime = observation.get("crime_index", 0.1)
        unrest = observation.get("civil_unrest", 0.1)
        if crime > 0.3 or unrest > 0.3 or rebel_active:
            return "community_policing"
        else:
            return "hold"
    
    # Infrastructure Head: Focus on infrastructure
    elif agent_id == "infrastructure_head":
        power_grid = observation.get("power_grid_health", 0.9)
        if power_grid < 0.7 or "infrastructure_failure" in crises:
            return "emergency_repairs"
        else:
            return "hold"
    
    # Media Spokesperson: Focus on trust
    elif agent_id == "media_spokesperson":
        misinfo = observation.get("misinformation_level", 0.1)
        if trust < 0.5 or misinfo > 0.3:
            return "press_conference"
        else:
            return "hold"
    
    return "hold"


def main():
    print("\n" + "=" * 80)
    print("  LLM TRAINING DATA COLLECTION")
    print("=" * 80)
    print()
    
    # Configuration
    NUM_EPISODES = 100  # Collect 100 episodes
    OUTPUT_FILE = "training/llm_training_data.jsonl"
    
    print(f"Configuration:")
    print(f"  Episodes: {NUM_EPISODES}")
    print(f"  Output: {OUTPUT_FILE}")
    print()
    
    # Create environment and wrapper
    config = CivicMindConfig(
        max_weeks=20,
        difficulty=3,
        enable_rebel=True,
        enable_schema_drift=True
    )
    env = CivicMindEnv(config)
    wrapper = LLMAgentWrapper()
    
    # Collect data
    all_examples = []
    
    print("Collecting data...")
    for episode in range(NUM_EPISODES):
        # Use heuristic policy for data collection
        examples = collect_episode_data(env, wrapper, use_heuristic=True)
        all_examples.extend(examples)
        
        if (episode + 1) % 20 == 0:
            print(f"  Episode {episode + 1}/{NUM_EPISODES} - {len(all_examples)} examples collected")
    
    print(f"\n✅ Collected {len(all_examples)} training examples")
    print()
    
    # Filter for high-reward examples (SFT on good behavior)
    print("Filtering for high-reward examples...")
    high_reward_threshold = 0.7
    high_reward_examples = [ex for ex in all_examples if ex["reward"] >= high_reward_threshold]
    
    print(f"  Total examples: {len(all_examples)}")
    print(f"  High-reward examples (>= {high_reward_threshold}): {len(high_reward_examples)}")
    print()
    
    # Save to JSONL
    print(f"Saving to {OUTPUT_FILE}...")
    Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w') as f:
        for example in high_reward_examples:
            f.write(json.dumps(example) + '\n')
    
    print(f"✅ Saved {len(high_reward_examples)} examples")
    print()
    
    # Statistics
    print("=" * 80)
    print("  DATA STATISTICS")
    print("=" * 80)
    print()
    
    # Per-agent breakdown
    agent_counts = {}
    for ex in high_reward_examples:
        agent_id = ex["agent_id"]
        agent_counts[agent_id] = agent_counts.get(agent_id, 0) + 1
    
    print("Examples per agent:")
    for agent_id, count in sorted(agent_counts.items()):
        print(f"  {agent_id}: {count}")
    print()
    
    # Reward distribution
    rewards = [ex["reward"] for ex in high_reward_examples]
    print(f"Reward statistics:")
    print(f"  Mean: {sum(rewards) / len(rewards):.4f}")
    print(f"  Min: {min(rewards):.4f}")
    print(f"  Max: {max(rewards):.4f}")
    print()
    
    # Sample example
    print("Sample training example:")
    print("-" * 80)
    sample = high_reward_examples[0]
    print(f"Agent: {sample['agent_id']}")
    print(f"Reward: {sample['reward']:.4f}")
    print(f"\nPrompt (first 300 chars):")
    print(sample['prompt'][:300] + "...")
    print(f"\nCompletion: {sample['completion']}")
    print("-" * 80)
    print()
    
    print("=" * 80)
    print("✅ DATA COLLECTION COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Train LLM: python training/train_llm_sft.py")
    print("  2. Evaluate: python training/evaluate_llm_agent.py")
    print()


if __name__ == "__main__":
    main()
