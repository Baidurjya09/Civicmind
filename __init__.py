"""
CivicMind — Utils
Logging, metrics tracking, reward curve plotting, and episode summaries.
Used by training loop and evaluation scripts.
"""

import json
import time
from pathlib import Path
from dataclasses import dataclass, field


# ─────────────────────────────────────────────────────────────────────────────
# Episode Tracker — accumulates metrics across one full episode
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class EpisodeTracker:
    episode_id: int = 0
    difficulty: int = 1
    rewards: list[float] = field(default_factory=list)
    trust_scores: list[float] = field(default_factory=list)
    survival_rates: list[float] = field(default_factory=list)
    gdp_indices: list[float] = field(default_factory=list)
    rebel_weeks: list[int] = field(default_factory=list)
    crisis_events: list[dict] = field(default_factory=list)
    agent_decisions: dict[str, list[str]] = field(default_factory=dict)

    def record_step(self, reward: float, info: dict, city_metrics: dict):
        self.rewards.append(round(reward, 4))
        self.trust_scores.append(round(city_metrics.get("trust_score", 0), 4))
        self.survival_rates.append(round(city_metrics.get("survival_rate", 1), 4))
        self.gdp_indices.append(round(city_metrics.get("gdp_index", 1), 4))
        if info.get("rebel_active"):
            self.rebel_weeks.append(info.get("week", 0))

    def record_decisions(self, actions: dict):
        for agent_id, action in actions.items():
            if agent_id not in self.agent_decisions:
                self.agent_decisions[agent_id] = []
            self.agent_decisions[agent_id].append(
                action.get("policy_decision", "hold")
            )

    def summary(self) -> dict:
        if not self.rewards:
            return {}
        return {
            "episode_id":      self.episode_id,
            "difficulty":      self.difficulty,
            "total_steps":     len(self.rewards),
            "mean_reward":     round(sum(self.rewards) / len(self.rewards), 4),
            "final_reward":    round(self.rewards[-1], 4),
            "max_reward":      round(max(self.rewards), 4),
            "min_reward":      round(min(self.rewards), 4),
            "reward_delta":    round(self.rewards[-1] - self.rewards[0], 4),
            "final_trust":     round(self.trust_scores[-1], 4) if self.trust_scores else 0,
            "final_survival":  round(self.survival_rates[-1], 4) if self.survival_rates else 1,
            "final_gdp":       round(self.gdp_indices[-1], 4) if self.gdp_indices else 1,
            "rebel_spawned":   len(self.rebel_weeks) > 0,
            "rebel_spawn_week":self.rebel_weeks[0] if self.rebel_weeks else None,
        }

    def hold_rate(self, agent_id: str) -> float:
        decisions = self.agent_decisions.get(agent_id, [])
        if not decisions:
            return 0.0
        return round(decisions.count("hold") / len(decisions), 3)


# ─────────────────────────────────────────────────────────────────────────────
# Training Logger — writes JSONL log, tracks improvement across iterations
# ─────────────────────────────────────────────────────────────────────────────
class TrainingLogger:
    def __init__(self, log_dir: str = "training/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / f"run_{int(time.time())}.jsonl"
        self.entries: list[dict] = []
        self._start_time = time.time()

    def log_step(self, iteration: int, reward: float, metrics: dict = None):
        entry = {
            "iteration":  iteration,
            "reward":     round(reward, 4),
            "elapsed_s":  round(time.time() - self._start_time, 1),
            **(metrics or {}),
        }
        self.entries.append(entry)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def log_episode(self, tracker: EpisodeTracker):
        s = tracker.summary()
        self.log_step(iteration=s.get("episode_id", 0), reward=s.get("mean_reward", 0), metrics=s)

    def print_progress(self, window: int = 5):
        if not self.entries:
            return
        recent = self.entries[-window:]
        rewards = [e["reward"] for e in recent]
        mean = sum(rewards) / len(rewards)
        trend = rewards[-1] - rewards[0] if len(rewards) > 1 else 0
        print(
            f"  [Iter {self.entries[-1]['iteration']:03d}] "
            f"Reward={mean:.4f}  Trend={trend:+.4f}  "
            f"Elapsed={self.entries[-1]['elapsed_s']:.0f}s"
        )

    def improvement_summary(self) -> dict:
        if len(self.entries) < 2:
            return {}
        first = self.entries[0]["reward"]
        last  = self.entries[-1]["reward"]
        best  = max(e["reward"] for e in self.entries)
        return {
            "iterations":   len(self.entries),
            "start_reward": round(first, 4),
            "final_reward": round(last, 4),
            "best_reward":  round(best, 4),
            "total_gain":   round(last - first, 4),
            "pct_gain":     round((last - first) / max(first, 0.001) * 100, 1),
        }

    def ascii_curve(self, metric: str = "reward", height: int = 10):
        vals = [e.get(metric, e.get("reward", 0)) for e in self.entries]
        if len(vals) < 2:
            return
        mn, mx = min(vals), max(vals)
        rng = mx - mn if mx > mn else 0.001
        print(f"\n  ── {metric} curve ({'▲' if vals[-1] > vals[0] else '▼'}) ─────────────────")
        for row in range(height, -1, -1):
            threshold = mn + (row / height) * rng
            bar = "".join("█" if v >= threshold else " " for v in vals)
            print(f"  {threshold:.3f} │{bar}")
        print(f"         └{'─' * len(vals)}")
        print(f"           Step 1 → {len(vals)}  |  Δ = {vals[-1]-vals[0]:+.4f}")


# ─────────────────────────────────────────────────────────────────────────────
# Metrics Formatter — pretty-prints city state dicts for agent prompts
# ─────────────────────────────────────────────────────────────────────────────
def format_city_status(metrics: dict) -> str:
    """Human-readable city status for agent prompts and logs."""
    lines = [
        f"Week {metrics.get('week','?')} City Status:",
        f"  Survival   : {metrics.get('survival_rate', 1):.1%}",
        f"  Trust      : {metrics.get('trust_score', 0.7):.1%}",
        f"  GDP        : {metrics.get('gdp_index', 1):.3f}",
        f"  Hospital   : {metrics.get('hospital_capacity', 0.8):.1%} capacity",
        f"  Disease    : {metrics.get('disease_prevalence', 0.02):.1%} prevalence",
        f"  Crime      : {metrics.get('crime_index', 0.15):.1%}",
        f"  Power Grid : {metrics.get('power_grid_health', 0.95):.1%}",
        f"  Budget     : {metrics.get('budget_remaining', 1e6):,.0f}",
        f"  Rebel Str. : {metrics.get('rebel_strength', 0):.1%}",
    ]
    return "\n".join(lines)


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Ensure a value is strictly within [lo, hi]."""
    return max(lo, min(hi, float(value)))


def safe_divide(num: float, denom: float, default: float = 0.0) -> float:
    """Division that returns default instead of ZeroDivisionError."""
    return num / denom if abs(denom) > 1e-10 else default


def weighted_mean(values: list[float], weights: list[float]) -> float:
    """Weighted mean, returns 0.0 on empty input."""
    if not values or not weights:
        return 0.0
    total_w = sum(weights)
    if total_w <= 0:
        return 0.0
    return sum(v * w for v, w in zip(values, weights)) / total_w
