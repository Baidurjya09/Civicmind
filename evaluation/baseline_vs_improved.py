"""
Baseline vs improved policy evaluation on identical scenarios.

Outputs:
1) JSON report with per-episode metrics
2) PNG plots for reward and confidence trends
3) Console table for quick judge-facing comparison
"""

import json
import sys
from pathlib import Path
from typing import Callable, Dict, List

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from environment.civic_env import CivicMindConfig, CivicMindEnv
from environment.crisis_engine import Crisis


AGENTS = [
    "mayor",
    "health_minister",
    "finance_officer",
    "police_chief",
    "infrastructure_head",
    "media_spokesperson",
]


def baseline_policy(obs: Dict) -> Dict:
    """Weak baseline: always hold."""
    return {agent: {"policy_decision": "hold"} for agent in AGENTS}


def improved_policy(obs: Dict) -> Dict:
    """Improved policy: crisis-aware and role-aware actions."""
    active_crises = obs["mayor"].get("active_crises", [])
    trust = obs["mayor"].get("trust_score", 0.6)
    disease = obs["health_minister"].get("disease_prevalence", 0.0)
    crime = obs["police_chief"].get("crime_index", 0.0)
    budget = obs["finance_officer"].get("budget_remaining", 0.0)

    actions = {agent: {"policy_decision": "hold"} for agent in AGENTS}

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


def run_episode(policy_fn: Callable[[Dict], Dict], seed: int) -> Dict:
    config = CivicMindConfig(max_weeks=20, difficulty=3, seed=seed, enable_rebel=True)
    env = CivicMindEnv(config)
    obs = env.reset()

    # Fixed stressor so both policies face identical pressure.
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

    rewards: List[float] = []
    confidence: List[float] = []
    decisions: List[Dict] = []

    while not env.done:
        actions = policy_fn(obs)
        obs, reward, done, info = env.step(actions)
        rewards.append(reward)

        # Confidence proxy: high confidence when reward is high and trust improves.
        conf = min(0.95, max(0.05, 0.55 * reward + 0.45 * env.city.trust_score))
        confidence.append(conf)

        decisions.append(
            {
                "week": info["week"],
                "reward": round(reward, 4),
                "trust": round(env.city.trust_score, 4),
                "actions": {k: v.get("policy_decision", "hold") for k, v in actions.items()},
            }
        )

    return {
        "mean_reward": sum(rewards) / len(rewards),
        "final_reward": rewards[-1],
        "mean_confidence": sum(confidence) / len(confidence),
        "final_confidence": confidence[-1],
        "weeks": len(rewards),
        "rewards": rewards,
        "confidence": confidence,
        "decisions": decisions,
    }


def summarize(name: str, episodes: List[Dict]) -> Dict:
    return {
        "policy": name,
        "episodes": len(episodes),
        "mean_reward": sum(e["mean_reward"] for e in episodes) / len(episodes),
        "final_reward": sum(e["final_reward"] for e in episodes) / len(episodes),
        "mean_confidence": sum(e["mean_confidence"] for e in episodes) / len(episodes),
        "final_confidence": sum(e["final_confidence"] for e in episodes) / len(episodes),
    }


def plot_curves(baseline_episodes: List[Dict], improved_episodes: List[Dict], out_dir: Path) -> None:
    baseline_reward_curve = [e["mean_reward"] for e in baseline_episodes]
    improved_reward_curve = [e["mean_reward"] for e in improved_episodes]
    baseline_conf_curve = [e["mean_confidence"] for e in baseline_episodes]
    improved_conf_curve = [e["mean_confidence"] for e in improved_episodes]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Reward plot with annotations
    axes[0].plot(baseline_reward_curve, label="Baseline (always hold)", marker="o", 
                 linewidth=2, markersize=6, color='coral', alpha=0.8)
    axes[0].plot(improved_reward_curve, label="Improved policy", marker="o", 
                 linewidth=2, markersize=6, color='darkgreen', alpha=0.8)
    
    # Add improvement annotation
    baseline_avg = sum(baseline_reward_curve) / len(baseline_reward_curve)
    improved_avg = sum(improved_reward_curve) / len(improved_reward_curve)
    improvement_pct = ((improved_avg - baseline_avg) / baseline_avg) * 100
    
    axes[0].annotate(
        f'+{improvement_pct:.1f}%',
        xy=(6, improved_avg),
        xytext=(5, 0.85),
        fontsize=14,
        fontweight='bold',
        color='darkgreen',
        arrowprops=dict(arrowstyle='->', color='darkgreen', lw=2)
    )
    
    axes[0].set_title("Same Seed Evaluation - Reward Comparison", fontsize=13, fontweight='bold')
    axes[0].set_xlabel("Episode", fontsize=11, fontweight='bold')
    axes[0].set_ylabel("Mean Reward", fontsize=11, fontweight='bold')
    axes[0].legend(loc='lower right', fontsize=10)
    axes[0].grid(alpha=0.3, linestyle='--')
    axes[0].set_ylim(0.7, 1.0)

    # Confidence plot with annotations
    axes[1].plot(baseline_conf_curve, label="Baseline confidence", marker="o", 
                 linewidth=2, markersize=6, color='coral', alpha=0.8)
    axes[1].plot(improved_conf_curve, label="Improved confidence", marker="o", 
                 linewidth=2, markersize=6, color='darkgreen', alpha=0.8)
    
    axes[1].set_title("Policy Confidence Over Time", fontsize=13, fontweight='bold')
    axes[1].set_xlabel("Episode", fontsize=11, fontweight='bold')
    axes[1].set_ylabel("Mean Confidence", fontsize=11, fontweight='bold')
    axes[1].legend(loc='lower right', fontsize=10)
    axes[1].grid(alpha=0.3, linestyle='--')
    axes[1].set_ylim(0.6, 1.0)

    fig.tight_layout()
    fig.savefig(out_dir / "baseline_vs_improved.png", dpi=150, bbox_inches='tight')
    plt.close(fig)


def main() -> None:
    out_dir = Path("evaluation/artifacts")
    out_dir.mkdir(parents=True, exist_ok=True)

    n_episodes = 8
    seeds = [42 + i for i in range(n_episodes)]

    baseline_episodes = [run_episode(baseline_policy, seed) for seed in seeds]
    improved_episodes = [run_episode(improved_policy, seed) for seed in seeds]

    baseline_summary = summarize("baseline", baseline_episodes)
    improved_summary = summarize("improved", improved_episodes)

    reward_delta = improved_summary["mean_reward"] - baseline_summary["mean_reward"]
    reward_pct = (reward_delta / max(1e-6, baseline_summary["mean_reward"])) * 100.0
    conf_delta = improved_summary["mean_confidence"] - baseline_summary["mean_confidence"]

    report = {
        "baseline": baseline_summary,
        "improved": improved_summary,
        "deltas": {
            "mean_reward_delta": reward_delta,
            "mean_reward_pct": reward_pct,
            "mean_confidence_delta": conf_delta,
        },
        "episodes": {
            "baseline": baseline_episodes,
            "improved": improved_episodes,
        },
    }

    with open(out_dir / "baseline_vs_improved.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    plot_curves(baseline_episodes, improved_episodes, out_dir)

    print("=" * 80)
    print("BASELINE vs IMPROVED (identical eval harness)")
    print("=" * 80)
    print(f"{'Policy':<14} {'MeanReward':>12} {'FinalReward':>12} {'MeanConf':>10} {'FinalConf':>10}")
    print("-" * 80)
    print(
        f"{'Baseline':<14} {baseline_summary['mean_reward']:>12.4f} {baseline_summary['final_reward']:>12.4f} "
        f"{baseline_summary['mean_confidence']:>10.4f} {baseline_summary['final_confidence']:>10.4f}"
    )
    print(
        f"{'Improved':<14} {improved_summary['mean_reward']:>12.4f} {improved_summary['final_reward']:>12.4f} "
        f"{improved_summary['mean_confidence']:>10.4f} {improved_summary['final_confidence']:>10.4f}"
    )
    print("-" * 80)
    print(f"Reward improvement: {reward_delta:+.4f} ({reward_pct:+.2f}%)")
    print(f"Confidence delta : {conf_delta:+.4f}")
    print(f"Saved JSON report: {out_dir / 'baseline_vs_improved.json'}")
    print(f"Saved plot       : {out_dir / 'baseline_vs_improved.png'}")
    print("=" * 80)


if __name__ == "__main__":
    main()
