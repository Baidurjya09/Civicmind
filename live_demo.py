#!/usr/bin/env python3
"""
Live Execution Demo - Watch the RL Agent Act
This shows the system is REAL, not just a report
"""

import sys
import time
import pickle
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from environment.civic_env import CivicMindEnv, CivicMindConfig
from environment.crisis_engine import Crisis
from train_and_evaluate import RLPolicy

def print_separator():
    print("\n" + "=" * 80 + "\n")

def print_state(env, step):
    """Print current state in readable format"""
    print(f"📊 STEP {step} - CURRENT STATE:")
    print(f"  • Trust Score: {env.city.trust_score:.2%}")
    print(f"  • Budget: ${env.city.budget_remaining:,.0f}")
    print(f"  • Survival Rate: {env.city.survival_rate:.2%}")
    print(f"  • Active Crises: {len(env.crisis_engine.active_crises)}")
    if env.crisis_engine.active_crises:
        for crisis in env.crisis_engine.active_crises:
            print(f"    - {crisis.name} (severity: {crisis.severity:.1f})")

def print_actions(actions):
    """Print agent decisions"""
    print(f"\n🤖 AGENT DECISIONS:")
    for agent_id, action_dict in actions.items():
        action = action_dict["policy_decision"]
        emoji = "🏛️" if agent_id == "mayor" else "🏥" if agent_id == "health_minister" else "💰" if agent_id == "finance_officer" else "👮" if agent_id == "police_chief" else "🏗️" if agent_id == "infrastructure_head" else "📢"
        print(f"  {emoji} {agent_id.replace('_', ' ').title()}: {action}")

def print_outcome(reward, info):
    """Print step outcome"""
    print(f"\n📈 OUTCOME:")
    print(f"  • Reward: {reward:+.3f}")
    if "trust_change" in info:
        print(f"  • Trust change: {info['trust_change']:+.2%}")
    if "budget_change" in info:
        print(f"  • Budget change: ${info['budget_change']:+,.0f}")

def run_live_demo(policy_type="trained", n_steps=10):
    """Run live demo with step-by-step visualization"""
    
    print_separator()
    print("🎬 LIVE EXECUTION DEMO - WATCH THE RL AGENT ACT")
    print_separator()
    
    # Load policy
    if policy_type == "trained":
        print("Loading TRAINED policy...")
        policy = RLPolicy()
        policy.load("training/checkpoints/rl_policy.pkl")
        policy.epsilon = 0.0  # No exploration
        print("✅ Loaded trained Q-learning policy")
    else:
        print("Using RANDOM policy (baseline)...")
        policy = RLPolicy()
        policy.epsilon = 1.0  # Pure random
        print("✅ Using random baseline policy")
    
    print_separator()
    
    # Create environment
    config = CivicMindConfig(max_weeks=15, difficulty=3, seed=42)
    env = CivicMindEnv(config)
    obs = env.reset()
    
    # Add a crisis scenario
    print("🚨 SCENARIO: Major Flood Crisis")
    env.city.trust_score = 0.45
    env.city.budget_remaining = 200000
    env.crisis_engine.active_crises = [
        Crisis("Major Flood", 0.7, 1, 5, {"survival_rate": -0.08, "power_grid_health": -0.25}, False)
    ]
    print("  • Initial trust: 45%")
    print("  • Initial budget: $200,000")
    print("  • Crisis: Major Flood (severity 0.7)")
    
    print_separator()
    input("Press ENTER to start simulation...")
    print_separator()
    
    # Run simulation
    total_reward = 0
    
    for step in range(1, n_steps + 1):
        # Show current state
        print_state(env, step)
        
        # Get actions
        actions, _ = policy.get_all_actions(obs, training=False)
        
        # Show actions
        print_actions(actions)
        
        # Execute step
        next_obs, reward, done, info = env.step(actions)
        total_reward += reward
        
        # Show outcome
        print_outcome(reward, info)
        
        print(f"\n💯 Cumulative Reward: {total_reward:+.3f}")
        
        if done:
            print("\n🏁 SIMULATION ENDED")
            break
        
        obs = next_obs
        
        print_separator()
        
        if step < n_steps:
            time.sleep(0.5)  # Brief pause for readability
    
    # Final summary
    print_separator()
    print("📊 FINAL RESULTS:")
    print(f"  • Total Reward: {total_reward:+.3f}")
    print(f"  • Final Trust: {env.city.trust_score:.2%}")
    print(f"  • Final Budget: ${env.city.budget_remaining:,.0f}")
    print(f"  • Final Survival: {env.city.survival_rate:.2%}")
    print(f"  • Steps Completed: {step}")
    print_separator()
    
    return total_reward

def compare_policies():
    """Compare trained vs random policy side-by-side"""
    
    print_separator()
    print("⚔️  TRAINED vs RANDOM POLICY COMPARISON")
    print_separator()
    
    print("Running RANDOM policy...")
    random_reward = run_live_demo("random", n_steps=5)
    
    print("\n\n")
    input("Press ENTER to run TRAINED policy...")
    print("\n\n")
    
    print("Running TRAINED policy...")
    trained_reward = run_live_demo("trained", n_steps=5)
    
    # Comparison
    print_separator()
    print("🏆 COMPARISON RESULTS:")
    print(f"  • Random Policy Reward: {random_reward:+.3f}")
    print(f"  • Trained Policy Reward: {trained_reward:+.3f}")
    improvement = ((trained_reward - random_reward) / abs(random_reward)) * 100 if random_reward != 0 else 0
    print(f"  • Improvement: {improvement:+.1f}%")
    print_separator()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Live RL Agent Demo")
    parser.add_argument("--mode", choices=["trained", "random", "compare"], default="trained",
                       help="Demo mode: trained policy, random policy, or comparison")
    parser.add_argument("--steps", type=int, default=10,
                       help="Number of steps to simulate")
    
    args = parser.parse_args()
    
    if args.mode == "compare":
        compare_policies()
    else:
        run_live_demo(args.mode, args.steps)
