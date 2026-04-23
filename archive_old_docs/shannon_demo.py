"""
CivicMind — Shannon Loop Demo
Shows AI thinking process: Think → Test → Validate → Report
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.shannon_engine import ShannonLoopEngine
from agents.reasoning_agent import ReasoningAgent
from environment.civic_env import CivicMindEnv, CivicMindConfig

print("=" * 70)
print("  CivicMind — Shannon Loop Intelligence Demo")
print("  Think → Test → Validate → Report")
print("=" * 70)
print()

# Initialize environment
print("Initializing environment...")
config = CivicMindConfig(max_weeks=52, difficulty=5, seed=42)
env = CivicMindEnv(config)
obs = env.reset()

# Initialize Shannon engine
shannon = ShannonLoopEngine(env)
reasoning_agent = ReasoningAgent()

print("✅ Environment ready")
print()

# Create crisis scenario
print("=" * 70)
print("SCENARIO: Low Trust Crisis")
print("=" * 70)
print()

# Simulate low trust scenario
env.city.trust_score = 0.35
env.city.civil_unrest = 0.65
env.city.budget_remaining = 500_000

state = {
    "trust_score": env.city.trust_score,
    "civil_unrest": env.city.civil_unrest,
    "budget_remaining": env.city.budget_remaining,
    "gdp_index": env.city.gdp_index,
    "survival_rate": env.city.survival_rate,
    "crime_index": env.city.crime_index,
    "rebel_strength": env.city.rebel_strength,
}

print("📊 CURRENT STATE:")
print(f"  Trust: {state['trust_score']:.0%}")
print(f"  Unrest: {state['civil_unrest']:.0%}")
print(f"  Budget: ${state['budget_remaining']:,.0f}")
print(f"  GDP: {state['gdp_index']:.2f}")
print()

# Run Shannon Loop
print("🧠 SHANNON LOOP: Analyzing...")
print()

agent_id = "mayor"
available_actions = ["hold", "reduce_tax", "invest_in_welfare", "emergency_budget_release", "increase_tax"]

print("1️⃣ THINK: Generating candidate actions...")
print(f"   Candidates: {', '.join(available_actions)}")
print()

print("2️⃣ TEST: Simulating each action...")
best_result, all_results = shannon.shannon_loop(state, agent_id, available_actions)
print(f"   Simulated {len(all_results)} actions")
print()

print("3️⃣ VALIDATE: Comparing outcomes...")
print()
print("   Results:")
for i, result in enumerate(all_results, 1):
    print(f"   {i}. {result['action']:25s} | Score: {result['score']:.3f} | Impact: {result['impact']:6s} | Risk: {result['risk']:6s} | Confidence: {result['confidence']}%")
print()

print("4️⃣ REPORT: Best decision selected")
print()

# Generate reasoning
print("=" * 70)
print("🧠 AI REASONING")
print("=" * 70)
print()

reasoning = reasoning_agent.generate_reasoning(
    state=state,
    crisis=["Low Trust", "High Unrest"],
    best_result=best_result,
    all_results=all_results
)

print(f"✅ BEST ACTION: {reasoning['best_action']}")
print()
print(f"📊 REASON:")
print(f"   {reasoning['reason']}")
print()
print(f"❌ ALTERNATIVES REJECTED:")
print(f"   {reasoning['rejected_reason']}")
print()
print(f"⚠️ RISK ASSESSMENT:")
print(f"   {reasoning['risk_assessment']}")
print()
print(f"📈 CONFIDENCE: {reasoning['confidence']}%")
print()

# Counterfactual analysis
print("=" * 70)
print("🔍 COUNTERFACTUAL ANALYSIS")
print("=" * 70)
print()

counterfactual = shannon.get_counterfactual_analysis()

if counterfactual:
    print(f"What if we chose '{counterfactual['alternative']}' instead?")
    print()
    print(f"  Trust difference: {counterfactual['trust_difference']}")
    print(f"  Score difference: {counterfactual['score_difference']}")
    print()
    print(f"  💡 {counterfactual['explanation']}")
    print()

# Show decision comparison table
print("=" * 70)
print("📊 DECISION COMPARISON TABLE")
print("=" * 70)
print()
print(f"{'Action':<25s} | {'Score':>6s} | {'Impact':>6s} | {'Risk':>6s} | {'Confidence':>10s}")
print("-" * 70)
for result in all_results:
    print(f"{result['action']:<25s} | {result['score']:>6.3f} | {result['impact']:>6s} | {result['risk']:>6s} | {result['confidence']:>9}%")
print()

# Show state changes
print("=" * 70)
print("📈 PREDICTED STATE CHANGES (Best Action)")
print("=" * 70)
print()

best = all_results[0]
before = best['before']
after = best['after']

print(f"{'Metric':<20s} | {'Before':>10s} | {'After':>10s} | {'Change':>10s}")
print("-" * 70)

for metric in ['trust_score', 'civil_unrest', 'budget_remaining', 'gdp_index']:
    before_val = before.get(metric, 0)
    after_val = after.get(metric, 0)
    
    if metric == 'budget_remaining':
        change = after_val - before_val
        print(f"{metric:<20s} | ${before_val:>9,.0f} | ${after_val:>9,.0f} | ${change:>+9,.0f}")
    else:
        change = (after_val - before_val) * 100
        print(f"{metric:<20s} | {before_val:>9.1%} | {after_val:>9.1%} | {change:>+9.1f}%")

print()
print("=" * 70)
print("✅ Shannon Loop Complete!")
print()
print("This is what makes CivicMind intelligent:")
print("  1. Generates multiple options")
print("  2. Simulates each outcome")
print("  3. Compares results objectively")
print("  4. Explains the choice")
print("  5. Shows counterfactuals")
print()
print("Judges see PROOF of intelligence, not just actions.")
print("=" * 70)
