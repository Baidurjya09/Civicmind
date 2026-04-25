#!/usr/bin/env python3
"""
ABLATION STUDY - Prove Each Agent Matters

Tests system performance with each agent removed one at a time.
This proves the multi-agent architecture is meaningful, not over-engineered.

Output:
- JSON report with per-agent ablation results
- Console table showing performance degradation
- Evidence that each agent contributes to overall performance
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Callable

sys.path.insert(0, str(Path(__file__).parent.parent))

from environment.civic_env import CivicMindEnv, CivicMindConfig
from environment.crisis_engine import Crisis


ALL_AGENTS = [
    "mayor",
    "health_minister",
    "finance_officer",
    "police_chief",
    "infrastructure_head",
    "media_spokesperson",
]


def full_policy(obs: Dict) -> Dict:
    """Full system policy - all agents active"""
    active_crises = obs["mayor"].get("active_crises", [])
    trust = obs["mayor"].get("trust_score", 0.6)
    disease = obs["health_minister"].get("disease_prevalence", 0.0)
    crime = obs["police_chief"].get("crime_index", 0.0)
    budget = obs["finance_officer"].get("budget_remaining", 0.0)
    
    actions = {agent: {"policy_decision": "hold"} for agent in ALL_AGENTS}
    
    # Crisis response
    if active_crises:
        actions["mayor"] = {"policy_decision": "emergency_budget_release"}
        actions["health_minister"] = {
            "policy_decision": "mass_vaccination" if disease > 0.06 else "increase_hospital_staff"
        }
        actions["finance_officer"] = {
            "policy_decision": "issue_bonds" if budget < 250000 else "stimulus_package"
        }
        actions["police_chief"] = {"policy_decision": "community_policing"}
        actions["infrastructure_head"] = {"policy_decision": "emergency_repairs"}
        actions["media_spokesperson"] = {"policy_decision": "press_conference"}
    
    # Trust recovery
    elif trust < 0.55:
        actions["media_spokesperson"] = {"policy_decision": "social_media_campaign"}
        actions["mayor"] = {"policy_decision": "invest_in_welfare"}
    
    # Crime control
    if crime > 0.30:
        actions["police_chief"] = {"policy_decision": "community_policing"}
    
    return actions


def ablated_policy(obs: Dict, removed_agent: str) -> Dict:
    """Policy with one agent removed (forced to hold)"""
    actions = full_policy(obs)
    # Force removed agent to hold (simulate removal)
    actions[removed_agent] = {"policy_decision": "hold"}
    return actions


def run_episode(policy_fn: Callable[[Dict], Dict], seed: int, removed_agent: str = None) -> Dict:
    """Run one episode with given policy"""
    config = CivicMindConfig(max_weeks=15, difficulty=3, seed=seed, enable_rebel=True)
    env = CivicMindEnv(config)
    obs = env.reset()
    
    # Add fixed crisis for consistency
    env.crisis_engine.active_crises = [
        Crisis(
            name="Disease Outbreak",
            severity=0.55,
            week_triggered=1,
            duration=5,
            effects={"disease_prevalence": 0.08, "survival_rate": -0.04},
            resolved=False,
        )
    ]
    
    rewards = []
    trust_scores = []
    survival_rates = []
    
    while not env.done:
        if removed_agent:
            actions = ablated_policy(obs, removed_agent)
        else:
            actions = policy_fn(obs)
        
        obs, reward, done, info = env.step(actions)
        rewards.append(reward)
        trust_scores.append(env.city.trust_score)
        survival_rates.append(env.city.survival_rate)
    
    return {
        "mean_reward": sum(rewards) / len(rewards),
        "final_reward": rewards[-1],
        "mean_trust": sum(trust_scores) / len(trust_scores),
        "final_trust": trust_scores[-1],
        "mean_survival": sum(survival_rates) / len(survival_rates),
        "final_survival": survival_rates[-1],
        "weeks_survived": len(rewards),
    }


def run_ablation_test(agent_to_remove: str, seeds: List[int]) -> Dict:
    """Run ablation test for one agent across multiple seeds"""
    results = []
    
    for seed in seeds:
        result = run_episode(full_policy, seed, removed_agent=agent_to_remove)
        results.append(result)
    
    # Average across seeds
    return {
        "agent_removed": agent_to_remove,
        "episodes": len(results),
        "mean_reward": sum(r["mean_reward"] for r in results) / len(results),
        "mean_trust": sum(r["mean_trust"] for r in results) / len(results),
        "mean_survival": sum(r["mean_survival"] for r in results) / len(results),
        "weeks_survived": sum(r["weeks_survived"] for r in results) / len(results),
    }


def main():
    print("=" * 80)
    print("ABLATION STUDY - Proving Each Agent Matters")
    print("=" * 80)
    print("\nTesting system performance with each agent removed...")
    print("(Removed agents are forced to 'hold' - no actions)\n")
    
    # Test parameters
    n_episodes = 5
    seeds = [100 + i * 10 for i in range(n_episodes)]
    
    # Baseline: Full system (all agents active)
    print("Running baseline (full system)...")
    baseline_results = []
    for seed in seeds:
        result = run_episode(full_policy, seed, removed_agent=None)
        baseline_results.append(result)
    
    baseline = {
        "agent_removed": "none (full system)",
        "episodes": len(baseline_results),
        "mean_reward": sum(r["mean_reward"] for r in baseline_results) / len(baseline_results),
        "mean_trust": sum(r["mean_trust"] for r in baseline_results) / len(baseline_results),
        "mean_survival": sum(r["mean_survival"] for r in baseline_results) / len(baseline_results),
        "weeks_survived": sum(r["weeks_survived"] for r in baseline_results) / len(baseline_results),
    }
    
    # Ablation tests: Remove each agent one at a time
    ablation_results = []
    
    for agent in ALL_AGENTS:
        print(f"Testing without {agent}...")
        result = run_ablation_test(agent, seeds)
        ablation_results.append(result)
    
    # Calculate deltas
    for result in ablation_results:
        result["reward_delta"] = result["mean_reward"] - baseline["mean_reward"]
        result["reward_pct"] = (result["reward_delta"] / baseline["mean_reward"]) * 100
        result["trust_delta"] = result["mean_trust"] - baseline["mean_trust"]
        result["survival_delta"] = result["mean_survival"] - baseline["mean_survival"]
    
    # Display results
    print("\n" + "=" * 80)
    print("ABLATION RESULTS")
    print("=" * 80)
    print(f"{'Configuration':<25} {'Reward':>10} {'Δ Reward':>12} {'% Change':>10} {'Trust':>8} {'Survival':>10}")
    print("-" * 80)
    
    # Baseline
    print(
        f"{'Full System (baseline)':<25} "
        f"{baseline['mean_reward']:>10.4f} "
        f"{'—':>12} "
        f"{'—':>10} "
        f"{baseline['mean_trust']:>8.4f} "
        f"{baseline['mean_survival']:>10.4f}"
    )
    
    # Ablations
    for result in ablation_results:
        print(
            f"{'Without ' + result['agent_removed']:<25} "
            f"{result['mean_reward']:>10.4f} "
            f"{result['reward_delta']:>12.4f} "
            f"{result['reward_pct']:>9.2f}% "
            f"{result['mean_trust']:>8.4f} "
            f"{result['mean_survival']:>10.4f}"
        )
    
    print("-" * 80)
    
    # Analysis
    print("\n📊 ANALYSIS:")
    print(f"   Baseline (full system): {baseline['mean_reward']:.4f} reward")
    
    worst_ablation = min(ablation_results, key=lambda x: x["mean_reward"])
    print(f"   Worst ablation: Without {worst_ablation['agent_removed']}")
    print(f"   Performance drop: {worst_ablation['reward_delta']:.4f} ({worst_ablation['reward_pct']:.2f}%)")
    
    avg_degradation = sum(r["reward_delta"] for r in ablation_results) / len(ablation_results)
    avg_pct = (avg_degradation / baseline["mean_reward"]) * 100
    print(f"   Average degradation: {avg_degradation:.4f} ({avg_pct:.2f}%)")
    
    # Check if all agents contribute
    all_negative = all(r["reward_delta"] < 0 for r in ablation_results)
    if all_negative:
        print("\n✅ VERDICT: All agents contribute positively to system performance")
        print("   Removing any agent degrades performance → Multi-agent architecture is justified")
    else:
        print("\n⚠️  WARNING: Some agents may not contribute significantly")
        non_contributors = [r["agent_removed"] for r in ablation_results if r["reward_delta"] >= 0]
        print(f"   Non-contributing agents: {', '.join(non_contributors)}")
    
    # Save evidence
    evidence_dir = Path("evidence/eval")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    report = {
        "study_type": "ablation",
        "date": "2026-04-25",
        "baseline": baseline,
        "ablations": ablation_results,
        "analysis": {
            "worst_agent_to_remove": worst_ablation["agent_removed"],
            "worst_degradation": float(worst_ablation["reward_delta"]),
            "worst_degradation_pct": float(worst_ablation["reward_pct"]),
            "average_degradation": float(avg_degradation),
            "average_degradation_pct": float(avg_pct),
            "all_agents_contribute": all_negative,
        }
    }
    
    output_path = evidence_dir / "ablation_study.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Saved: {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
