#!/usr/bin/env python3
"""
REWARD BREAKDOWN LOGGER - Prove Explainability

Logs detailed reward component breakdown for each step.
This proves the reward function is not a black box and shows
exactly how each component contributes to the final reward.

Output:
- JSON report with per-step reward breakdown
- Console table showing component contributions
- Evidence that reward function is explainable and meaningful
"""

import sys
import json
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from environment.civic_env import CivicMindEnv, CivicMindConfig
from environment.crisis_engine import Crisis
from environment.reward_hardening import get_reward_breakdown


ALL_AGENTS = [
    "mayor",
    "health_minister",
    "finance_officer",
    "police_chief",
    "infrastructure_head",
    "media_spokesperson",
]


def improved_policy(obs: Dict) -> Dict:
    """Improved policy for demonstration"""
    active_crises = obs["mayor"].get("active_crises", [])
    trust = obs["mayor"].get("trust_score", 0.6)
    disease = obs["health_minister"].get("disease_prevalence", 0.0)
    crime = obs["police_chief"].get("crime_index", 0.0)
    budget = obs["finance_officer"].get("budget_remaining", 0.0)
    
    actions = {agent: {"policy_decision": "hold"} for agent in ALL_AGENTS}
    
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
    elif trust < 0.55:
        actions["media_spokesperson"] = {"policy_decision": "social_media_campaign"}
        actions["mayor"] = {"policy_decision": "invest_in_welfare"}
    
    if crime > 0.30:
        actions["police_chief"] = {"policy_decision": "community_policing"}
    
    return actions


def run_episode_with_breakdown(seed: int, max_weeks: int = 10) -> Dict:
    """Run episode and log reward breakdown at each step"""
    config = CivicMindConfig(max_weeks=max_weeks, difficulty=3, seed=seed, enable_rebel=True)
    env = CivicMindEnv(config)
    obs = env.reset()
    
    # Add crisis for interesting dynamics
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
    
    step_breakdowns = []
    
    while not env.done:
        # Get actions
        actions = improved_policy(obs)
        
        # Step environment
        obs, reward, done, info = env.step(actions)
        
        # Get reward breakdown
        breakdown = get_reward_breakdown(env)
        
        # Log step
        step_data = {
            "week": info["week"],
            "total_reward": float(reward),
            "breakdown": {k: float(v) for k, v in breakdown.items()},
            "city_state": {
                "trust": float(env.city.trust_score),
                "survival": float(env.city.survival_rate),
                "gdp": float(env.city.gdp_index),
                "budget": float(env.city.budget_remaining),
                "crime": float(env.city.crime_index),
                "disease": float(env.city.disease_prevalence),
            },
            "actions": {k: v.get("policy_decision", "hold") for k, v in actions.items()},
        }
        
        step_breakdowns.append(step_data)
    
    return {
        "seed": seed,
        "total_weeks": len(step_breakdowns),
        "steps": step_breakdowns,
    }


def analyze_breakdown(episode_data: Dict) -> Dict:
    """Analyze reward component contributions"""
    steps = episode_data["steps"]
    
    # Calculate average contribution of each component
    component_sums = {}
    component_counts = {}
    
    for step in steps:
        for component, value in step["breakdown"].items():
            if component != "total":
                if component not in component_sums:
                    component_sums[component] = 0.0
                    component_counts[component] = 0
                component_sums[component] += value
                component_counts[component] += 1
    
    component_averages = {
        comp: component_sums[comp] / component_counts[comp]
        for comp in component_sums
    }
    
    # Calculate total contribution (sum of absolute values)
    total_contribution = sum(abs(v) for v in component_averages.values())
    
    # Calculate percentage contribution
    component_percentages = {
        comp: (abs(value) / total_contribution) * 100 if total_contribution > 0 else 0
        for comp, value in component_averages.items()
    }
    
    return {
        "averages": component_averages,
        "percentages": component_percentages,
        "total_contribution": total_contribution,
    }


def main():
    print("=" * 80)
    print("REWARD BREAKDOWN LOGGER - Proving Explainability")
    print("=" * 80)
    print("\nRunning episode with detailed reward logging...\n")
    
    # Run episode
    seed = 42
    episode_data = run_episode_with_breakdown(seed, max_weeks=10)
    
    # Analyze
    analysis = analyze_breakdown(episode_data)
    
    # Display step-by-step breakdown
    print("STEP-BY-STEP REWARD BREAKDOWN:")
    print("-" * 80)
    print(f"{'Week':>4} {'Total':>8} {'Survival':>10} {'Trust':>10} {'Economy':>10} {'Security':>10} {'Penalties':>10}")
    print("-" * 80)
    
    for step in episode_data["steps"][:10]:  # Show first 10 steps
        breakdown = step["breakdown"]
        print(
            f"{step['week']:>4} "
            f"{breakdown.get('total', 0):>8.4f} "
            f"{breakdown.get('survival', 0):>10.4f} "
            f"{breakdown.get('trust', 0):>10.4f} "
            f"{breakdown.get('economy', 0):>10.4f} "
            f"{breakdown.get('security', 0):>10.4f} "
            f"{breakdown.get('penalties', 0):>10.4f}"
        )
    
    if len(episode_data["steps"]) > 10:
        print(f"... ({len(episode_data['steps']) - 10} more steps)")
    
    # Display component analysis
    print("\n" + "=" * 80)
    print("COMPONENT CONTRIBUTION ANALYSIS")
    print("=" * 80)
    print(f"{'Component':<20} {'Avg Value':>12} {'% of Total':>12} {'Impact':>10}")
    print("-" * 80)
    
    # Sort by absolute contribution
    sorted_components = sorted(
        analysis["averages"].items(),
        key=lambda x: abs(x[1]),
        reverse=True
    )
    
    for component, avg_value in sorted_components:
        if component != "total":
            pct = analysis["percentages"].get(component, 0)
            impact = "Positive" if avg_value > 0 else "Negative" if avg_value < 0 else "Neutral"
            print(
                f"{component:<20} "
                f"{avg_value:>12.4f} "
                f"{pct:>11.2f}% "
                f"{impact:>10}"
            )
    
    print("-" * 80)
    
    # Key insights
    print("\n📊 KEY INSIGHTS:")
    
    # Find dominant component
    dominant = max(analysis["percentages"].items(), key=lambda x: x[1])
    print(f"   Dominant component: {dominant[0]} ({dominant[1]:.1f}% of total)")
    
    # Find most variable component
    component_vars = {}
    for comp in analysis["averages"].keys():
        if comp != "total":
            values = [step["breakdown"].get(comp, 0) for step in episode_data["steps"]]
            variance = sum((v - analysis["averages"][comp])**2 for v in values) / len(values)
            component_vars[comp] = variance
    
    most_variable = max(component_vars.items(), key=lambda x: x[1])
    print(f"   Most variable: {most_variable[0]} (variance: {most_variable[1]:.4f})")
    
    # Check balance
    positive_components = [c for c, v in analysis["averages"].items() if v > 0 and c != "total"]
    negative_components = [c for c, v in analysis["averages"].items() if v < 0 and c != "total"]
    
    print(f"   Positive components: {len(positive_components)}")
    print(f"   Negative components: {len(negative_components)}")
    
    if len(positive_components) > 0 and len(negative_components) > 0:
        print("   ✅ Reward function is balanced (has both rewards and penalties)")
    else:
        print("   ⚠️  Reward function may be unbalanced")
    
    # Example breakdown for one step
    print("\n📋 EXAMPLE BREAKDOWN (Week 5):")
    if len(episode_data["steps"]) >= 5:
        example_step = episode_data["steps"][4]  # Week 5
        print(f"   Total Reward: {example_step['breakdown']['total']:.4f}")
        print("   Components:")
        for comp, value in example_step["breakdown"].items():
            if comp != "total":
                print(f"     {comp:15s}: {value:+.4f}")
        print(f"   City State:")
        print(f"     Trust:    {example_step['city_state']['trust']:.4f}")
        print(f"     Survival: {example_step['city_state']['survival']:.4f}")
        print(f"     GDP:      {example_step['city_state']['gdp']:.4f}")
    
    # Save evidence
    evidence_dir = Path("evidence/eval")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    report = {
        "evaluation_type": "reward_breakdown",
        "date": "2026-04-25",
        "episode": episode_data,
        "analysis": {
            "component_averages": {k: float(v) for k, v in analysis["averages"].items()},
            "component_percentages": {k: float(v) for k, v in analysis["percentages"].items()},
            "dominant_component": dominant[0],
            "dominant_percentage": float(dominant[1]),
            "positive_components": positive_components,
            "negative_components": negative_components,
        }
    }
    
    output_path = evidence_dir / "reward_breakdown.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Saved: {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
