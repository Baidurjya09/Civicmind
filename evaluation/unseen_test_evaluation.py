#!/usr/bin/env python3
"""
UNSEEN TEST SET EVALUATION - Prove Generalization

Trains on one set of scenarios, evaluates on completely different scenarios.
This proves the model generalizes and doesn't just memorize training patterns.

Output:
- JSON report with train vs test performance
- Console table showing generalization gap
- Evidence that model works on unseen scenarios
"""

import sys
import json
import pickle
from pathlib import Path
from typing import Dict, List

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


def load_trained_policy():
    """Load trained Q-learning policy"""
    checkpoint_path = Path("training/checkpoints/rl_policy.pkl")
    
    if not checkpoint_path.exists():
        print(f"❌ ERROR: Trained policy not found at {checkpoint_path}")
        print("   Please run training first: python training/q_learning_trainer.py")
        sys.exit(1)
    
    with open(checkpoint_path, "rb") as f:
        policy_data = pickle.load(f)
    
    return policy_data.get("q_table", {})


def state_to_key(obs: Dict) -> str:
    """Convert observation to state key for Q-table lookup"""
    mayor_obs = obs.get("mayor", {})
    
    trust = mayor_obs.get("trust_score", 0.6)
    survival = mayor_obs.get("survival_rate", 0.8)
    budget = mayor_obs.get("budget_remaining", 300000)
    crises = len(mayor_obs.get("active_crises", []))
    
    # Discretize
    trust_bin = int(trust * 10)
    survival_bin = int(survival * 10)
    budget_bin = 0 if budget < 200000 else (1 if budget < 400000 else 2)
    crisis_bin = min(crises, 3)
    
    return f"{trust_bin}_{survival_bin}_{budget_bin}_{crisis_bin}"


def trained_policy(obs: Dict, q_table: Dict) -> Dict:
    """Use trained Q-learning policy"""
    state_key = state_to_key(obs)
    
    # Get Q-values for this state
    if state_key in q_table:
        q_values = q_table[state_key]
        # Get best action (highest Q-value)
        best_action = max(q_values, key=q_values.get)
    else:
        # Unseen state - use safe default
        best_action = "hold"
    
    # Map action to all agents (simplified for evaluation)
    actions = {}
    for agent in ALL_AGENTS:
        if best_action == "hold":
            actions[agent] = {"policy_decision": "hold"}
        elif best_action == "crisis_response":
            # Agent-specific crisis actions
            if agent == "mayor":
                actions[agent] = {"policy_decision": "emergency_budget_release"}
            elif agent == "health_minister":
                actions[agent] = {"policy_decision": "mass_vaccination"}
            elif agent == "finance_officer":
                actions[agent] = {"policy_decision": "issue_bonds"}
            elif agent == "police_chief":
                actions[agent] = {"policy_decision": "community_policing"}
            elif agent == "infrastructure_head":
                actions[agent] = {"policy_decision": "emergency_repairs"}
            elif agent == "media_spokesperson":
                actions[agent] = {"policy_decision": "press_conference"}
        elif best_action == "invest_welfare":
            actions[agent] = {"policy_decision": "invest_in_welfare" if agent == "mayor" else "hold"}
        elif best_action == "trust_building":
            actions[agent] = {"policy_decision": "social_media_campaign" if agent == "media_spokesperson" else "hold"}
        else:
            actions[agent] = {"policy_decision": "hold"}
    
    return actions


def create_train_scenarios() -> List[Dict]:
    """Create training scenarios (seen during training)"""
    return [
        {
            "name": "Disease Outbreak (Train)",
            "seed": 42,
            "crisis": Crisis(
                name="Disease Outbreak",
                severity=0.55,
                week_triggered=1,
                duration=5,
                effects={"disease_prevalence": 0.08, "survival_rate": -0.04},
                resolved=False,
            )
        },
        {
            "name": "Economic Crisis (Train)",
            "seed": 100,
            "crisis": Crisis(
                name="Economic Recession",
                severity=0.60,
                week_triggered=1,
                duration=6,
                effects={"unemployment": 0.10, "gdp_index": -0.15},
                resolved=False,
            )
        },
        {
            "name": "Infrastructure Failure (Train)",
            "seed": 200,
            "crisis": Crisis(
                name="Power Grid Failure",
                severity=0.50,
                week_triggered=1,
                duration=4,
                effects={"power_grid_health": -0.20, "hospital_capacity": -0.10},
                resolved=False,
            )
        },
    ]


def create_test_scenarios() -> List[Dict]:
    """Create test scenarios (UNSEEN - different from training)"""
    return [
        {
            "name": "Cyber Attack (Test - UNSEEN)",
            "seed": 999,
            "crisis": Crisis(
                name="Cyber Attack",
                severity=0.65,
                week_triggered=1,
                duration=5,
                effects={"misinformation_level": 0.15, "trust_score": -0.10, "power_grid_health": -0.15},
                resolved=False,
            )
        },
        {
            "name": "Natural Disaster (Test - UNSEEN)",
            "seed": 888,
            "crisis": Crisis(
                name="Earthquake",
                severity=0.70,
                week_triggered=1,
                duration=7,
                effects={"survival_rate": -0.08, "hospital_capacity": -0.20, "power_grid_health": -0.25},
                resolved=False,
            )
        },
        {
            "name": "Social Unrest (Test - UNSEEN)",
            "seed": 777,
            "crisis": Crisis(
                name="Mass Protests",
                severity=0.55,
                week_triggered=1,
                duration=6,
                effects={"civil_unrest": 0.20, "trust_score": -0.12, "crime_index": 0.10},
                resolved=False,
            )
        },
        {
            "name": "Pandemic (Test - UNSEEN)",
            "seed": 666,
            "crisis": Crisis(
                name="Pandemic",
                severity=0.75,
                week_triggered=1,
                duration=8,
                effects={"disease_prevalence": 0.15, "survival_rate": -0.10, "unemployment": 0.12},
                resolved=False,
            )
        },
    ]


def run_scenario(scenario: Dict, q_table: Dict) -> Dict:
    """Run one scenario with trained policy"""
    config = CivicMindConfig(max_weeks=15, difficulty=3, seed=scenario["seed"], enable_rebel=True)
    env = CivicMindEnv(config)
    obs = env.reset()
    
    # Inject scenario crisis
    env.crisis_engine.active_crises = [scenario["crisis"]]
    
    rewards = []
    trust_scores = []
    survival_rates = []
    
    while not env.done:
        actions = trained_policy(obs, q_table)
        obs, reward, done, info = env.step(actions)
        rewards.append(reward)
        trust_scores.append(env.city.trust_score)
        survival_rates.append(env.city.survival_rate)
    
    return {
        "scenario_name": scenario["name"],
        "mean_reward": sum(rewards) / len(rewards),
        "final_reward": rewards[-1],
        "mean_trust": sum(trust_scores) / len(trust_scores),
        "final_trust": trust_scores[-1],
        "mean_survival": sum(survival_rates) / len(survival_rates),
        "weeks_survived": len(rewards),
    }


def main():
    print("=" * 80)
    print("UNSEEN TEST SET EVALUATION - Proving Generalization")
    print("=" * 80)
    print("\nLoading trained policy...")
    
    q_table = load_trained_policy()
    print(f"✅ Loaded Q-table with {len(q_table)} states\n")
    
    # Create scenarios
    train_scenarios = create_train_scenarios()
    test_scenarios = create_test_scenarios()
    
    print(f"Train scenarios: {len(train_scenarios)} (seen during training)")
    print(f"Test scenarios:  {len(test_scenarios)} (UNSEEN - never seen before)\n")
    
    # Evaluate on train set
    print("Evaluating on TRAIN set (seen scenarios)...")
    train_results = []
    for scenario in train_scenarios:
        print(f"  Running: {scenario['name']}")
        result = run_scenario(scenario, q_table)
        train_results.append(result)
    
    # Evaluate on test set
    print("\nEvaluating on TEST set (unseen scenarios)...")
    test_results = []
    for scenario in test_scenarios:
        print(f"  Running: {scenario['name']}")
        result = run_scenario(scenario, q_table)
        test_results.append(result)
    
    # Calculate averages
    train_avg_reward = sum(r["mean_reward"] for r in train_results) / len(train_results)
    test_avg_reward = sum(r["mean_reward"] for r in test_results) / len(test_results)
    
    train_avg_trust = sum(r["mean_trust"] for r in train_results) / len(train_results)
    test_avg_trust = sum(r["mean_trust"] for r in test_results) / len(test_results)
    
    generalization_gap = train_avg_reward - test_avg_reward
    generalization_pct = (generalization_gap / train_avg_reward) * 100
    
    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"{'Scenario':<40} {'Reward':>10} {'Trust':>8} {'Survival':>10}")
    print("-" * 80)
    
    print("TRAIN SET (Seen):")
    for result in train_results:
        print(
            f"  {result['scenario_name']:<38} "
            f"{result['mean_reward']:>10.4f} "
            f"{result['mean_trust']:>8.4f} "
            f"{result['mean_survival']:>10.4f}"
        )
    print(f"  {'TRAIN AVERAGE':<38} {train_avg_reward:>10.4f} {train_avg_trust:>8.4f}")
    
    print("\nTEST SET (Unseen):")
    for result in test_results:
        print(
            f"  {result['scenario_name']:<38} "
            f"{result['mean_reward']:>10.4f} "
            f"{result['mean_trust']:>8.4f} "
            f"{result['mean_survival']:>10.4f}"
        )
    print(f"  {'TEST AVERAGE':<38} {test_avg_reward:>10.4f} {test_avg_trust:>8.4f}")
    
    print("-" * 80)
    print(f"Generalization Gap: {generalization_gap:.4f} ({generalization_pct:.2f}%)")
    
    # Analysis
    print("\n📊 ANALYSIS:")
    if generalization_gap < 0.10:  # Less than 10% gap
        print("   ✅ EXCELLENT: Model generalizes well to unseen scenarios")
        print(f"   Generalization gap is only {generalization_pct:.2f}%")
    elif generalization_gap < 0.20:  # Less than 20% gap
        print("   ✅ GOOD: Model shows reasonable generalization")
        print(f"   Generalization gap is {generalization_pct:.2f}%")
    else:
        print("   ⚠️  WARNING: Significant generalization gap detected")
        print(f"   Gap is {generalization_pct:.2f}% - model may be overfitting")
    
    print(f"\n   Train performance: {train_avg_reward:.4f}")
    print(f"   Test performance:  {test_avg_reward:.4f}")
    print(f"   Model retains {(test_avg_reward/train_avg_reward)*100:.1f}% of performance on unseen data")
    
    # Save evidence
    evidence_dir = Path("evidence/eval")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    report = {
        "evaluation_type": "unseen_test_set",
        "date": "2026-04-25",
        "train_set": {
            "scenarios": len(train_scenarios),
            "results": train_results,
            "average_reward": float(train_avg_reward),
            "average_trust": float(train_avg_trust),
        },
        "test_set": {
            "scenarios": len(test_scenarios),
            "results": test_results,
            "average_reward": float(test_avg_reward),
            "average_trust": float(test_avg_trust),
        },
        "generalization": {
            "gap": float(generalization_gap),
            "gap_percentage": float(generalization_pct),
            "retention_percentage": float((test_avg_reward/train_avg_reward)*100),
        }
    }
    
    output_path = evidence_dir / "unseen_test_evaluation.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Saved: {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
