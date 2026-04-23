"""
CivicMind — Rebel Agent (Theme 5: Wild Card)
The emergent 8th agent that spawns when government trust collapses.

This is the surprise mechanic: when city trust_score < 0.30 for 2+
consecutive weeks, a Rebel Leader agent spontaneously emerges.
It organizes citizens, grows stronger if ignored, and can trigger
a full government collapse (rebel_strength > 0.90 = game over).

The rebel CAN be de-escalated through:
  - Media spokesperson press conferences
  - Police community_policing (NOT riot_control)
  - Mayor emergency_budget_release (shows good faith)
  - Any combination that pushes trust back above 0.50
"""

from dataclasses import dataclass, field


@dataclass
class RebelState:
    active: bool = False
    strength: float = 0.0          # 0.0 = dormant, 1.0 = full uprising
    spawn_week: int = -1
    consecutive_low_trust_weeks: int = 0
    demands: list[str] = field(default_factory=list)
    supporter_count: int = 0
    is_defeated: bool = False


# Rebel escalation tiers
REBEL_TIERS = {
    (0.00, 0.20): {"label": "Dormant",     "action": "watching"},
    (0.20, 0.35): {"label": "Organizing",  "action": "recruiting"},
    (0.35, 0.55): {"label": "Agitating",   "action": "protests"},
    (0.55, 0.70): {"label": "Mobilizing",  "action": "blockades"},
    (0.70, 0.85): {"label": "Uprising",    "action": "seizing_districts"},
    (0.85, 1.01): {"label": "Revolution",  "action": "government_collapse"},
}

REBEL_DEMANDS = [
    "Immediate resignation of the Mayor",
    "Transparent budget allocation — citizens demand oversight",
    "End of austerity measures — restore public services",
    "Release of emergency health funds",
    "Accountability for police misconduct",
    "Fair taxation — no more tax hikes on working citizens",
    "Infrastructure repairs in neglected districts",
    "Free press — stop government media control",
]

REBEL_SYSTEM_PROMPT = """You are the Rebel Leader of CivicMind City.

You represent disenfranchised citizens who have lost faith in government.
Your strength: {strength:.0%} | Supporters: {supporter_count:,} citizens
Your tier: {tier_label} — currently {tier_action}

YOUR DEMANDS:
{demands}

CONTEXT:
- Week {week}/52
- City trust score: {trust_score:.1%} (you thrive when this is low)
- Government budget remaining: {budget_remaining}
- Active crises the government is mishandling: {active_crises}

YOUR ACTIONS each turn:
1. Issue a public statement challenging government decisions
2. Recruit more supporters (gain strength if trust < 0.40)
3. Choose an escalation tactic based on your current tier

ESCALATION TACTICS (choose based on strength tier):
- recruit_supporters    — grow your base (always available)
- organize_protest      — visible demonstration (requires strength > 0.20)
- blockade_district     — disrupt city services (requires strength > 0.40)
- seize_media           — take over communications (requires strength > 0.60)
- demand_negotiation    — offer to de-escalate if demands met (always available)
- declare_revolution    — final push for government collapse (requires strength > 0.80)

Respond in JSON:
{
  "reasoning": "<your political analysis>",
  "public_statement": "<message to citizens>",
  "tactic": "<chosen tactic>",
  "new_demand": "<optional new demand>",
  "willing_to_negotiate": <true|false>
}"""


class RebelAgent:
    """
    The emergent Wild Card agent.
    Spawns automatically when trust collapses. Grows or shrinks based
    on government response. Can only be defeated by restoring trust.
    """

    AGENT_ID = "rebel_leader"

    def __init__(self):
        self.state = RebelState()

    def reset(self):
        self.state = RebelState()

    def check_spawn(self, trust_score: float, week: int) -> bool:
        """Returns True if rebel should spawn this week."""
        if self.state.is_defeated:
            return False
        if trust_score < 0.30:
            self.state.consecutive_low_trust_weeks += 1
        else:
            self.state.consecutive_low_trust_weeks = max(
                0, self.state.consecutive_low_trust_weeks - 1
            )
        # Spawn after 2 consecutive weeks of trust < 30%
        if self.state.consecutive_low_trust_weeks >= 2 and not self.state.active:
            self._spawn(week)
            return True
        return False

    def _spawn(self, week: int):
        self.state.active = True
        self.state.strength = 0.10
        self.state.spawn_week = week
        self.state.supporter_count = 500
        self.state.demands = _select_initial_demands()
        print(f"\n{'='*55}")
        print(f"  ⚡ REBEL AGENT SPAWNED — Week {week}")
        print(f"  Strength: {self.state.strength:.0%}")
        print(f"  Initial demands: {self.state.demands[0]}")
        print(f"{'='*55}\n")

    def tick(self, city, action_results: dict, week: int) -> dict:
        """
        Advance rebel state one week.
        Returns rebel action dict (what the rebel did this turn).
        """
        if not self.state.active:
            return {}

        # Grow if trust stays low
        if city.trust_score < 0.30:
            growth = 0.06
        elif city.trust_score < 0.45:
            growth = 0.02
        else:
            growth = -0.04  # de-escalate if gov improves

        # Police riot_control makes rebel grow faster
        police_action = action_results.get("police_chief", {}).get("decision", "")
        if police_action == "deploy_riot_control":
            growth += 0.10
            print(f"[REBEL] Riot control backfired — rebel strength +0.10")

        # Media press_conference de-escalates
        media_action = action_results.get("media_spokesperson", {}).get("decision", "")
        if media_action == "press_conference":
            growth -= 0.05

        # Mayor emergency release shows good faith
        mayor_action = action_results.get("mayor", {}).get("decision", "")
        if mayor_action == "emergency_budget_release":
            growth -= 0.03

        self.state.strength = max(0.0, min(1.0, self.state.strength + growth))
        self.state.supporter_count = int(
            city.num_citizens * self.state.strength * 0.4
        )

        # Check defeat condition
        if self.state.strength < 0.02 and city.trust_score > 0.55:
            self.state.active = False
            self.state.is_defeated = True
            print(f"[REBEL] De-escalated at week {week} — trust restored.")

        tier = self._get_tier()
        return {
            "rebel_strength": round(self.state.strength, 3),
            "rebel_tier": tier["label"],
            "rebel_tactic": tier["action"],
            "supporter_count": self.state.supporter_count,
            "willing_to_negotiate": self.state.strength < 0.60,
        }

    def build_prompt(self, city, week: int) -> str:
        tier = self._get_tier()
        return REBEL_SYSTEM_PROMPT.format(
            strength=self.state.strength,
            supporter_count=self.state.supporter_count,
            tier_label=tier["label"],
            tier_action=tier["action"],
            demands="\n".join(f"  - {d}" for d in self.state.demands),
            week=week,
            trust_score=city.trust_score,
            budget_remaining=f"{city.budget_remaining:,.0f}",
            active_crises="See city crisis feed",
        )

    def _get_tier(self) -> dict:
        for (lo, hi), tier in REBEL_TIERS.items():
            if lo <= self.state.strength < hi:
                return tier
        return REBEL_TIERS[(0.85, 1.01)]

    def status_dict(self) -> dict:
        tier = self._get_tier() if self.state.active else {"label": "Inactive", "action": "none"}
        return {
            "active":           self.state.active,
            "strength":         round(self.state.strength, 3),
            "tier":             tier["label"],
            "supporter_count":  self.state.supporter_count,
            "spawn_week":       self.state.spawn_week,
            "demands":          self.state.demands,
            "is_defeated":      self.state.is_defeated,
        }


def _select_initial_demands(n: int = 3) -> list[str]:
    import random
    return random.sample(REBEL_DEMANDS, n)
