"""
Compare different training approaches
Shows: Random vs Heuristic vs Supervised vs GRPO
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from environment.civic_env import CivicMindEnv, CivicMindConfig
from agents.agent_definitions import ALL_AGENTS
from training.enhanced_rewards import EnhancedRewardModel

print("=" * 70)
print("  CivicMind — Model Comparison")
print("=" * 70)
print()

# Test scenarios
scenarios = [
    {
        "name": "Low Trust Crisis",
        "state": {
            "trust_score": 0.35,
            "civil_unrest": 0.65,
            "gdp_index": 0.60,
            "budget_remaining": 500_000,
        },
        "agent": "mayor",
    },
    {
        "name": "Health Emergency",
        "state": {
            "disease_prevalence": 0.12,
            "hospital_capacity": 0.45,
            "survival_rate": 0.92,
            "budget_remaining": 600_000,
        },
        "agent": "health_minister",
    },
    {
        "name": "High Crime",
        "state": {
            "crime_index": 0.45,
            "civil_unrest": 0.55,
            "trust_score": 0.50,
            "budget_remaining": 700_000,
        },
        "agent": "police_chief",
    },
    {
        "name": "Budget Crisis",
        "state": {
            "budget_remaining": 150_000,
            "gdp_index": 0.65,
            "unemployment": 0.15,
            "trust_score": 0.55,
        },
        "agent": "finance_officer",
    },
]

reward_model = EnhancedRewardModel()

def random_policy(agent_id, state):
    """Random decision"""
    agent = ALL_AGENTS[agent_id]
    decision = np.random.choice(agent.valid_decisions)
    return decision

def heuristic_policy(agent_id, state):
    """Simple rule-based policy"""
    trust = state.get("trust_score", 0.75)
    budget = state.get("budget_remaining", 1_000_000)
    disease = state.get("disease_prevalence", 0.02)
    crime = state.get("crime_index", 0.15)
    unrest = state.get("civil_unrest", 0.10)
    
    if agent_id == "mayor":
        if trust < 0.40:
            return "reduce_tax"
        elif budget < 200_000:
            return "emergency_budget_release"
        else:
            return "hold"
    
    elif agent_id == "health_minister":
        if disease > 0.08:
            return "mass_vaccination"
        elif state.get("hospital_capacity", 1) < 0.60:
            return "increase_hospital_staff"
        else:
            return "hold"
    
    elif agent_id == "finance_officer":
        if budget < 200_000:
            return "issue_bonds"
        elif state.get("gdp_index", 1) < 0.70:
            return "stimulus_package"
        else:
            return "hold"
    
    elif agent_id == "police_chief":
        if crime > 0.30:
            return "community_policing"
        else:
            return "hold"
    
    else:
        return "hold"

def optimal_policy(agent_id, state):
    """What GRPO should learn"""
    trust = state.get("trust_score", 0.75)
    budget = state.get("budget_remaining", 1_000_000)
    disease = state.get("disease_prevalence", 0.02)
    crime = state.get("crime_index", 0.15)
    unrest = state.get("civil_unrest", 0.10)
    
    if agent_id == "mayor":
        if trust < 0.40 and unrest > 0.50:
            return "invest_in_welfare"  # Best for low trust + high unrest
        elif trust < 0.40:
            return "reduce_tax"
        elif budget < 200_000:
            return "emergency_budget_release"
        else:
            return "hold"
    
    elif agent_id == "health_minister":
        if disease > 0.10:
            return "mass_vaccination"  # Critical
        elif disease > 0.05:
            return "increase_hospital_staff"
        else:
            return "hold"
    
    elif agent_id == "finance_officer":
        if budget < 150_000:
            return "issue_bonds"  # Emergency
        elif state.get("gdp_index", 1) < 0.70 and budget > 300_000:
            return "stimulus_package"  # Can afford it
        else:
            return "hold"
    
    elif agent_id == "police_chief":
        # NEVER use riot control unless extreme
        if crime > 0.40 or unrest > 0.50:
            return "community_policing"  # Always better
        else:
            return "hold"
    
    else:
        return "hold"

# Run comparison
print("Testing policies on scenarios...")
print()

results = {
    "Random": [],
    "Heuristic": [],
    "Optimal (GRPO Target)": [],
}

for scenario in scenarios:
    print(f"📋 Scenario: {scenario['name']}")
    print(f"   Agent: {scenario['agent']}")
    print(f"   State: Trust={scenario['state'].get('trust_score', 'N/A')}, "
          f"Unrest={scenario['state'].get('civil_unrest', 'N/A')}")
    print()
    
    # Test each policy
    for policy_name, policy_func in [
        ("Random", random_policy),
        ("Heuristic", heuristic_policy),
        ("Optimal (GRPO Target)", optimal_policy),
    ]:
        decision = policy_func(scenario['agent'], scenario['state'])
        reward = reward_model.compute_decision_reward(
            decision,
            scenario['agent'],
            scenario['state']
        )
        
        results[policy_name].append(reward)
        
        print(f"   {policy_name:25s} → {decision:25s} | Reward: {reward:.3f}")
    
    print()
    print("-" * 70)
    print()

# Summary
print("=" * 70)
print("📊 SUMMARY")
print("=" * 70)
print()

for policy_name in results:
    avg_reward = np.mean(results[policy_name])
    std_reward = np.std(results[policy_name])
    
    print(f"{policy_name:25s} | Avg Reward: {avg_reward:.3f} ± {std_reward:.3f}")

print()
print("=" * 70)
print()
print("🎯 INTERPRETATION:")
print()
print("Random Policy:")
print("  - Baseline performance")
print("  - No learning, just guessing")
print("  - Expected: ~0.40-0.50 reward")
print()
print("Heuristic Policy:")
print("  - Simple rules")
print("  - Better than random")
print("  - Expected: ~0.55-0.65 reward")
print()
print("Optimal Policy (GRPO Target):")
print("  - What GRPO should learn")
print("  - Context-aware decisions")
print("  - Expected: ~0.70-0.80 reward")
print()
print("🚀 GRPO Training Goal:")
print("   Train model to match or exceed Optimal policy performance")
print()
print("=" * 70)
