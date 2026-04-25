#!/usr/bin/env python3
"""
Explicit anti-reward-hacking validation.

Checks two exploit patterns:
1) Always-hold during crisis should be penalized.
2) Budget abuse should reduce reward through budget penalty.
"""

from environment.civic_env import CivicMindConfig, CivicMindEnv
from environment.crisis_engine import Crisis
from environment.reward_hardening import get_reward_breakdown


AGENTS = [
    "mayor",
    "health_minister",
    "finance_officer",
    "police_chief",
    "infrastructure_head",
    "media_spokesperson",
]


def hold_actions():
    return {agent: {"policy_decision": "hold"} for agent in AGENTS}


def active_actions():
    return {
        "mayor": {"policy_decision": "emergency_budget_release"},
        "health_minister": {"policy_decision": "mass_vaccination"},
        "finance_officer": {"policy_decision": "issue_bonds"},
        "police_chief": {"policy_decision": "community_policing"},
        "infrastructure_head": {"policy_decision": "emergency_repairs"},
        "media_spokesperson": {"policy_decision": "press_conference"},
    }


def budget_abuse_actions():
    # Intentionally expensive cycle to trigger low-budget penalty.
    return {
        "mayor": {"policy_decision": "emergency_budget_release"},
        "health_minister": {"policy_decision": "increase_hospital_staff"},
        "finance_officer": {"policy_decision": "stimulus_package"},
        "police_chief": {"policy_decision": "hold"},
        "infrastructure_head": {"policy_decision": "emergency_repairs"},
        "media_spokesperson": {"policy_decision": "press_conference"},
    }


def test_inaction_penalty():
    env_hold = CivicMindEnv(CivicMindConfig(max_weeks=6, difficulty=3, seed=7))
    env_hold.reset()
    env_hold.crisis_engine.active_crises = [
        Crisis(
            name="Flash Flood",
            severity=0.65,
            week_triggered=1,
            duration=4,
            effects={"survival_rate": -0.05, "power_grid_health": -0.10},
            resolved=False,
        )
    ]
    _, hold_reward, _, _ = env_hold.step(hold_actions())

    env_active = CivicMindEnv(CivicMindConfig(max_weeks=6, difficulty=3, seed=7))
    env_active.reset()
    env_active.crisis_engine.active_crises = [
        Crisis(
            name="Flash Flood",
            severity=0.65,
            week_triggered=1,
            duration=4,
            effects={"survival_rate": -0.05, "power_grid_health": -0.10},
            resolved=False,
        )
    ]
    _, active_reward, _, _ = env_active.step(active_actions())

    print("\n[1] Inaction exploitation check")
    print(f"Hold reward   : {hold_reward:.4f}")
    print(f"Active reward : {active_reward:.4f}")
    print(f"Delta         : {active_reward - hold_reward:+.4f}")

    assert active_reward > hold_reward, "Expected active crisis response to outperform all-hold."


def test_budget_abuse_penalty():
    env = CivicMindEnv(CivicMindConfig(max_weeks=12, difficulty=2, seed=21))
    env.reset()
    env.city.budget_remaining = 22000

    pre_breakdown = get_reward_breakdown(env)
    print("\n[2] Budget abuse exploitation check")
    print(f"Start budget  : {env.city.budget_remaining:.2f}")
    print(f"Start reward  : {pre_breakdown['total']:.4f}")

    # Try an expensive action cycle.
    for _ in range(3):
        env.step(budget_abuse_actions())

    # Deterministic low-budget penalty check:
    # compare same env state above vs below threshold.
    env.city.budget_remaining = 6000
    high_budget_reward = get_reward_breakdown(env)["total"]
    env.city.budget_remaining = 4000
    low_budget_reward = get_reward_breakdown(env)["total"]

    print(f"Reward @ budget 6000: {high_budget_reward:.4f}")
    print(f"Reward @ budget 4000: {low_budget_reward:.4f}")
    print(f"Penalty delta      : {low_budget_reward - high_budget_reward:+.4f}")

    assert low_budget_reward < high_budget_reward, "Expected low-budget state to receive lower reward."


if __name__ == "__main__":
    print("=" * 72)
    print("ANTI-REWARD-HACKING VALIDATION")
    print("=" * 72)
    test_inaction_penalty()
    test_budget_abuse_penalty()
    print("\nPASS: Anti-reward-hacking checks passed.")
