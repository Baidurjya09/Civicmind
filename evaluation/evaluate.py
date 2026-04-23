"""
CivicMind — Evaluation Script
Runs before/after comparison to prove training improvement.
Produces reward curves, agent behavior diffs, and a summary report.

Usage:
  python evaluation/evaluate.py --mode baseline    # random policy
  python evaluation/evaluate.py --mode trained     # trained policy
  python evaluation/evaluate.py --mode compare     # both + diff chart
"""

import sys
import os
import json
import argparse
import random
from pathlib import Path
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment.civic_env import CivicMindEnv, CivicMindConfig
from agents.agent_definitions import ALL_AGENTS
from rewards.reward_model import RewardModel


# ─────────────────────────────────────────────────────────────────────────────
# Policy implementations
# ─────────────────────────────────────────────────────────────────────────────

def random_policy(agent_id: str, observation: dict) -> dict:
    """Baseline: random valid decision, no reasoning."""
    agent = ALL_AGENTS[agent_id]
    decision = random.choice(agent.valid_decisions)
    return {
        "reasoning": "Random baseline policy.",
        "tool_calls": [],
        "policy_decision": decision,
    }


def heuristic_policy(agent_id: str, observation: dict) -> dict:
    """Smart heuristic: rule-based without LLM."""
    week = observation.get("week", 1)
    active_crises = observation.get("active_crises", [])
    rebel = observation.get("rebel_active", False)
    trust = observation.get("trust_score", 0.7)

    rules = {
        "mayor": lambda o: (
            "emergency_budget_release"
            if o.get("budget_remaining", 1e6) < 200_000 or active_crises
            else "hold"
        ),
        "health_minister": lambda o: (
            "mass_vaccination"
            if o.get("disease_prevalence", 0) > 0.08
            else "increase_hospital_staff"
            if o.get("hospital_capacity", 1) < 0.60
            else "hold"
        ),
        "finance_officer": lambda o: (
            "issue_bonds"
            if o.get("budget_remaining", 1e6) < 150_000
            else "stimulus_package"
            if o.get("gdp_index", 1) < 0.70
            else "hold"
        ),
        "police_chief": lambda o: (
            "community_policing"    # Never use riot_control (trust penalty)
            if o.get("crime_index", 0) > 0.30 or rebel
            else "hold"
        ),
        "infrastructure_head": lambda o: (
            "emergency_repairs"
            if o.get("power_grid_health", 1) < 0.55
            else "hold"
        ),
        "media_spokesperson": lambda o: (
            "press_conference"
            if o.get("misinformation_level", 0) > 0.30 or rebel
            else "social_media_campaign"
            if trust < 0.55
            else "hold"
        ),
    }
    fn = rules.get(agent_id, lambda o: "hold")
    decision = fn(observation)

    tool_calls = []
    if active_crises and agent_id in ["mayor", "health_minister"]:
        tool_calls = [{"name": "get_budget_status", "params": {}}]

    return {
        "reasoning": f"Heuristic: crisis={bool(active_crises)}, rebel={rebel}, trust={trust:.2f}",
        "tool_calls": tool_calls,
        "policy_decision": decision,
    }


def llm_policy(agent_id: str, observation: dict, model, tokenizer, cfg) -> dict:
    """Trained LLM policy."""
    from agents.agent_definitions import build_agent_prompt
    from training.train_grpo import _generate_action, _parse_completion
    prompt = build_agent_prompt(agent_id, observation)
    completion = _generate_action(model, tokenizer, prompt, cfg)
    return _parse_completion(completion)


# ─────────────────────────────────────────────────────────────────────────────
# Episode runner
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class EpisodeResult:
    policy_name: str
    rewards: list[float] = field(default_factory=list)
    survival_rates: list[float] = field(default_factory=list)
    trust_scores: list[float] = field(default_factory=list)
    gdp_indices: list[float] = field(default_factory=list)
    rebel_spawned: bool = False
    rebel_defeated: bool = False
    weeks_survived: int = 0
    city_collapsed: bool = False

    @property
    def mean_reward(self) -> float:
        return sum(self.rewards) / len(self.rewards) if self.rewards else 0.0

    @property
    def final_reward(self) -> float:
        return self.rewards[-1] if self.rewards else 0.0

    @property
    def reward_improvement(self) -> float:
        if len(self.rewards) < 2:
            return 0.0
        return self.rewards[-1] - self.rewards[0]

    def summary(self) -> dict:
        return {
            "policy":           self.policy_name,
            "mean_reward":      round(self.mean_reward, 4),
            "final_reward":     round(self.final_reward, 4),
            "reward_delta":     round(self.reward_improvement, 4),
            "final_survival":   round(self.survival_rates[-1] if self.survival_rates else 0, 4),
            "final_trust":      round(self.trust_scores[-1] if self.trust_scores else 0, 4),
            "final_gdp":        round(self.gdp_indices[-1] if self.gdp_indices else 0, 4),
            "rebel_spawned":    self.rebel_spawned,
            "rebel_defeated":   self.rebel_defeated,
            "weeks_survived":   self.weeks_survived,
            "city_collapsed":   self.city_collapsed,
        }


def run_episode(
    policy_fn,
    policy_name: str,
    difficulty: int = 3,
    max_weeks: int = 20,
    seed: int = 42,
    verbose: bool = True,
) -> EpisodeResult:
    """Run one full episode with a given policy function."""
    env = CivicMindEnv(CivicMindConfig(
        max_weeks=max_weeks,
        difficulty=difficulty,
        seed=seed,
        enable_rebel=True,
        enable_schema_drift=True,
    ))
    obs = env.reset()
    result = EpisodeResult(policy_name=policy_name)

    if verbose:
        print(f"\n{'─'*55}")
        print(f"  Policy: {policy_name} | Difficulty: {difficulty} | Seed: {seed}")
        print(f"{'─'*55}")

    while not env.done:
        actions = {}
        for agent_id in env.AGENT_IDS:
            actions[agent_id] = policy_fn(agent_id, obs[agent_id])

        obs, reward, done, info = env.step(actions)
        result.rewards.append(reward)
        result.survival_rates.append(env.city.survival_rate)
        result.trust_scores.append(env.city.trust_score)
        result.gdp_indices.append(env.city.gdp_index)

        if env.rebel_active:
            result.rebel_spawned = True
        if not env.rebel_active and result.rebel_spawned:
            result.rebel_defeated = True

        result.weeks_survived = info["week"]
        result.city_collapsed = env.city.survival_rate < 0.5 or env.city.rebel_strength > 0.9

        if verbose and info["week"] % 4 == 0:
            print(
                f"  W{info['week']:02d} | R={reward:.4f} | "
                f"Trust={env.city.trust_score:.2f} | "
                f"GDP={env.city.gdp_index:.2f} | "
                f"Survival={env.city.survival_rate:.2f} | "
                f"Rebel={'⚡' if env.rebel_active else '·'}"
            )

    if verbose:
        s = result.summary()
        print(f"\n  RESULT: mean_reward={s['mean_reward']:.4f} | "
              f"final_reward={s['final_reward']:.4f} | "
              f"rebel={'spawned+defeated' if s['rebel_defeated'] else 'spawned' if s['rebel_spawned'] else 'none'} | "
              f"collapsed={s['city_collapsed']}")

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Multi-episode evaluation
# ─────────────────────────────────────────────────────────────────────────────
def evaluate_policy(
    policy_fn,
    policy_name: str,
    n_episodes: int = 5,
    difficulty: int = 3,
    max_weeks: int = 20,
) -> dict:
    """Run N episodes, return aggregate stats."""
    results = []
    for i in range(n_episodes):
        r = run_episode(
            policy_fn, policy_name,
            difficulty=difficulty,
            max_weeks=max_weeks,
            seed=42 + i,
            verbose=(i == 0),  # verbose only first episode
        )
        results.append(r)

    mean_rewards = [r.mean_reward for r in results]
    final_rewards = [r.final_reward for r in results]
    survivals = [r.survival_rates[-1] if r.survival_rates else 0 for r in results]
    rebels = sum(1 for r in results if r.rebel_spawned)
    collapses = sum(1 for r in results if r.city_collapsed)

    return {
        "policy":           policy_name,
        "n_episodes":       n_episodes,
        "mean_reward_avg":  round(sum(mean_rewards) / n_episodes, 4),
        "final_reward_avg": round(sum(final_rewards) / n_episodes, 4),
        "survival_avg":     round(sum(survivals) / n_episodes, 4),
        "rebel_rate":       round(rebels / n_episodes, 3),
        "collapse_rate":    round(collapses / n_episodes, 3),
        "episode_results":  [r.summary() for r in results],
    }


# ─────────────────────────────────────────────────────────────────────────────
# ASCII charts (for Colab / terminal output)
# ─────────────────────────────────────────────────────────────────────────────
def ascii_reward_chart(results: list[EpisodeResult], title: str = "Reward Curves"):
    """Print side-by-side ASCII reward curves."""
    print(f"\n{'═'*60}")
    print(f"  {title}")
    print(f"{'═'*60}")

    height = 12
    for result in results:
        rewards = result.rewards
        if not rewards:
            continue
        mn, mx = min(rewards), max(rewards)
        rng = mx - mn if mx > mn else 0.01
        print(f"\n  {result.policy_name}  (mean={result.mean_reward:.4f})")
        for row in range(height, -1, -1):
            threshold = mn + (row / height) * rng
            line = f"  {threshold:.3f} │"
            for r in rewards:
                line += "█" if r >= threshold else " "
            print(line)
        print(f"         └{'─' * len(rewards)}")
        print(f"           Week 1 → {len(rewards)}")


def comparison_table(results_dict: dict[str, dict]):
    """Print a formatted comparison table of all policies."""
    print(f"\n{'═'*65}")
    print(f"  {'POLICY':<22} {'MEAN R':>8} {'FINAL R':>8} {'SURVIVAL':>10} {'REBEL%':>8} {'COLLAPSE%':>10}")
    print(f"  {'─'*22} {'─'*8} {'─'*8} {'─'*10} {'─'*8} {'─'*10}")
    for name, stats in results_dict.items():
        print(
            f"  {name:<22} "
            f"{stats['mean_reward_avg']:>8.4f} "
            f"{stats['final_reward_avg']:>8.4f} "
            f"{stats['survival_avg']:>10.1%} "
            f"{stats['rebel_rate']:>8.1%} "
            f"{stats['collapse_rate']:>10.1%}"
        )
    print(f"{'═'*65}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="CivicMind Evaluation")
    parser.add_argument("--mode", choices=["baseline", "heuristic", "compare", "full"],
                        default="compare")
    parser.add_argument("--n_episodes", type=int, default=3)
    parser.add_argument("--difficulty", type=int, default=3)
    parser.add_argument("--max_weeks", type=int, default=20)
    parser.add_argument("--model_path", type=str, default=None)
    parser.add_argument("--output", type=str, default="evaluation/results.json")
    args = parser.parse_args()

    Path("evaluation").mkdir(exist_ok=True)
    all_results = {}

    if args.mode in ("baseline", "compare", "full"):
        print("\n[1] Evaluating RANDOM baseline policy...")
        stats = evaluate_policy(
            random_policy, "Random Baseline",
            n_episodes=args.n_episodes,
            difficulty=args.difficulty,
            max_weeks=args.max_weeks,
        )
        all_results["random"] = stats
        print(f"  Random baseline: mean_reward={stats['mean_reward_avg']:.4f}")

    if args.mode in ("heuristic", "compare", "full"):
        print("\n[2] Evaluating HEURISTIC policy...")
        stats = evaluate_policy(
            heuristic_policy, "Heuristic Policy",
            n_episodes=args.n_episodes,
            difficulty=args.difficulty,
            max_weeks=args.max_weeks,
        )
        all_results["heuristic"] = stats
        print(f"  Heuristic: mean_reward={stats['mean_reward_avg']:.4f}")

    if args.mode == "full" and args.model_path:
        print("\n[3] Evaluating TRAINED LLM policy...")
        from training.train_grpo import load_model, TrainingConfig
        cfg = TrainingConfig()
        model, tokenizer = load_model(cfg)
        trained_fn = lambda aid, obs: llm_policy(aid, obs, model, tokenizer, cfg)
        stats = evaluate_policy(
            trained_fn, "Trained LLM (GRPO)",
            n_episodes=args.n_episodes,
            difficulty=args.difficulty,
            max_weeks=args.max_weeks,
        )
        all_results["trained"] = stats
        print(f"  Trained LLM: mean_reward={stats['mean_reward_avg']:.4f}")

    # Print comparison
    if len(all_results) > 1:
        comparison_table(all_results)

        # Improvement calculation
        if "random" in all_results and "heuristic" in all_results:
            delta = (all_results["heuristic"]["mean_reward_avg"]
                     - all_results["random"]["mean_reward_avg"])
            pct = delta / max(all_results["random"]["mean_reward_avg"], 0.001) * 100
            print(f"\n  Heuristic vs Random: {delta:+.4f} ({pct:+.1f}% improvement)")

        if "random" in all_results and "trained" in all_results:
            delta = (all_results["trained"]["mean_reward_avg"]
                     - all_results["random"]["mean_reward_avg"])
            pct = delta / max(all_results["random"]["mean_reward_avg"], 0.001) * 100
            print(f"  Trained vs Random:   {delta:+.4f} ({pct:+.1f}% improvement)")

    # Save results
    with open(args.output, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n  Results saved → {args.output}")

    return all_results


if __name__ == "__main__":
    main()
