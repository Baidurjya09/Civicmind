"""
Test Final Polish - Verify ALL improvements including failure warning fix
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.shannon_engine import ShannonLoopEngine
from agents.reasoning_agent import ReasoningAgent
from environment.civic_env import CivicMindEnv, CivicMindConfig

def test_failure_warning_always_present():
    """
    CRITICAL TEST: Failure warning must ALWAYS be present
    Tests both crisis and stable scenarios
    """
    print("=" * 70)
    print("CRITICAL TEST: FAILURE WARNING ALWAYS PRESENT")
    print("=" * 70)
    
    # Test 1: Crisis scenario
    print("\n📊 TEST 1: Crisis Scenario (Trust 35%, Unrest 65%)")
    print("-" * 70)
    
    config = CivicMindConfig(max_weeks=52, difficulty=5, seed=42)
    env = CivicMindEnv(config)
    env.reset()
    
    env.city.trust_score = 0.35
    env.city.civil_unrest = 0.65
    env.city.budget_remaining = 500_000
    
    shannon = ShannonLoopEngine(env)
    reasoning = ReasoningAgent()
    
    state = {
        "trust_score": env.city.trust_score,
        "civil_unrest": env.city.civil_unrest,
        "budget_remaining": env.city.budget_remaining,
        "gdp_index": env.city.gdp_index,
        "survival_rate": env.city.survival_rate,
        "crime_index": env.city.crime_index,
        "disease_prevalence": env.city.disease_prevalence,
        "hospital_capacity": env.city.hospital_capacity,
        "rebel_strength": env.city.rebel_strength,
    }
    
    best_result, all_results = shannon.shannon_loop(
        state=state,
        agent_id="mayor",
        available_actions=["hold", "reduce_tax", "invest_in_welfare", "emergency_budget_release"]
    )
    
    reasoning_result = reasoning.generate_reasoning(
        state=state,
        crisis=["Low Trust", "High Unrest"],
        best_result=best_result,
        all_results=all_results
    )
    
    failure_warning_crisis = reasoning_result.get("failure_warning", "")
    print(f"⚠️ Failure Warning:\n{failure_warning_crisis}")
    
    has_warning_crisis = len(failure_warning_crisis) > 0
    has_risk_details_crisis = "FAILURE RISK" in failure_warning_crisis
    
    print(f"\n✅ Has warning: {has_warning_crisis}")
    print(f"✅ Has risk details: {has_risk_details_crisis}")
    
    # Test 2: Stable scenario
    print("\n📊 TEST 2: Stable Scenario (Trust 80%, Unrest 10%)")
    print("-" * 70)
    
    env2 = CivicMindEnv(config)
    env2.reset()
    
    env2.city.trust_score = 0.80
    env2.city.civil_unrest = 0.10
    env2.city.budget_remaining = 1_000_000
    
    shannon2 = ShannonLoopEngine(env2)
    reasoning2 = ReasoningAgent()
    
    state2 = {
        "trust_score": env2.city.trust_score,
        "civil_unrest": env2.city.civil_unrest,
        "budget_remaining": env2.city.budget_remaining,
        "gdp_index": env2.city.gdp_index,
        "survival_rate": env2.city.survival_rate,
        "crime_index": env2.city.crime_index,
        "disease_prevalence": env2.city.disease_prevalence,
        "hospital_capacity": env2.city.hospital_capacity,
        "rebel_strength": env2.city.rebel_strength,
    }
    
    best_result2, all_results2 = shannon2.shannon_loop(
        state=state2,
        agent_id="mayor",
        available_actions=["hold", "reduce_tax", "invest_in_welfare", "emergency_budget_release"]
    )
    
    reasoning_result2 = reasoning2.generate_reasoning(
        state=state2,
        crisis=[],
        best_result=best_result2,
        all_results=all_results2
    )
    
    failure_warning_stable = reasoning_result2.get("failure_warning", "")
    print(f"⚠️ Failure Warning:\n{failure_warning_stable}")
    
    has_warning_stable = len(failure_warning_stable) > 0
    has_risk_details_stable = "FAILURE RISK" in failure_warning_stable
    
    print(f"\n✅ Has warning: {has_warning_stable}")
    print(f"✅ Has risk details: {has_risk_details_stable}")
    
    # Final verdict
    print("\n" + "=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)
    
    if has_warning_crisis and has_warning_stable:
        print("✅ PASS: Failure warning ALWAYS present (crisis AND stable)")
        print("🏆 CRITICAL GAP FIXED!")
        return True
    else:
        print("❌ FAIL: Failure warning missing in some scenarios")
        if not has_warning_crisis:
            print("  - Missing in crisis scenario")
        if not has_warning_stable:
            print("  - Missing in stable scenario")
        return False


def test_score_gap_visibility():
    """Test that score gap is visible"""
    print("\n" + "=" * 70)
    print("TEST: SCORE GAP VISIBILITY")
    print("=" * 70)
    
    config = CivicMindConfig(max_weeks=52, difficulty=5, seed=42)
    env = CivicMindEnv(config)
    env.reset()
    
    env.city.trust_score = 0.35
    env.city.civil_unrest = 0.65
    env.city.budget_remaining = 500_000
    
    shannon = ShannonLoopEngine(env)
    reasoning = ReasoningAgent()
    
    state = {
        "trust_score": env.city.trust_score,
        "civil_unrest": env.city.civil_unrest,
        "budget_remaining": env.city.budget_remaining,
        "gdp_index": env.city.gdp_index,
        "survival_rate": env.city.survival_rate,
        "crime_index": env.city.crime_index,
        "disease_prevalence": env.city.disease_prevalence,
        "hospital_capacity": env.city.hospital_capacity,
        "rebel_strength": env.city.rebel_strength,
    }
    
    best_result, all_results = shannon.shannon_loop(
        state=state,
        agent_id="mayor",
        available_actions=["hold", "reduce_tax", "invest_in_welfare", "emergency_budget_release"]
    )
    
    reasoning_result = reasoning.generate_reasoning(
        state=state,
        crisis=["Low Trust", "High Unrest"],
        best_result=best_result,
        all_results=all_results
    )
    
    score_gap = reasoning_result.get("score_gap", "")
    print(f"\n📊 Score Gap: {score_gap}")
    
    has_score_gap = len(score_gap) > 0
    has_percentage = "%" in score_gap
    
    print(f"\n✅ Has score gap: {has_score_gap}")
    print(f"✅ Has percentage: {has_percentage}")
    
    if has_score_gap and has_percentage:
        print("✅ PASS: Score gap is visible")
        return True
    else:
        print("❌ FAIL: Score gap missing or incomplete")
        return False


def test_validation_statement():
    """Test that validation statement is present"""
    print("\n" + "=" * 70)
    print("TEST: VALIDATION STATEMENT")
    print("=" * 70)
    
    config = CivicMindConfig(max_weeks=52, difficulty=5, seed=42)
    env = CivicMindEnv(config)
    env.reset()
    
    env.city.trust_score = 0.35
    env.city.civil_unrest = 0.65
    env.city.budget_remaining = 500_000
    
    shannon = ShannonLoopEngine(env)
    reasoning = ReasoningAgent()
    
    state = {
        "trust_score": env.city.trust_score,
        "civil_unrest": env.city.civil_unrest,
        "budget_remaining": env.city.budget_remaining,
        "gdp_index": env.city.gdp_index,
        "survival_rate": env.city.survival_rate,
        "crime_index": env.city.crime_index,
        "disease_prevalence": env.city.disease_prevalence,
        "hospital_capacity": env.city.hospital_capacity,
        "rebel_strength": env.city.rebel_strength,
    }
    
    best_result, all_results = shannon.shannon_loop(
        state=state,
        agent_id="mayor",
        available_actions=["hold", "reduce_tax", "invest_in_welfare", "emergency_budget_release"]
    )
    
    reasoning_result = reasoning.generate_reasoning(
        state=state,
        crisis=["Low Trust", "High Unrest"],
        best_result=best_result,
        all_results=all_results
    )
    
    validation = reasoning_result.get("validation", "")
    print(f"\n✅ Validation: {validation}")
    
    has_validation = len(validation) > 0
    has_checkmark = "✅" in validation
    mentions_validation = "validated" in validation.lower()
    
    print(f"\n✅ Has validation: {has_validation}")
    print(f"✅ Has checkmark: {has_checkmark}")
    print(f"✅ Mentions validation: {mentions_validation}")
    
    if has_validation and mentions_validation:
        print("✅ PASS: Validation statement present")
        return True
    else:
        print("❌ FAIL: Validation statement missing")
        return False


def test_complete_output():
    """Test complete formatted output"""
    print("\n" + "=" * 70)
    print("TEST: COMPLETE FORMATTED OUTPUT")
    print("=" * 70)
    
    config = CivicMindConfig(max_weeks=52, difficulty=5, seed=42)
    env = CivicMindEnv(config)
    env.reset()
    
    env.city.trust_score = 0.35
    env.city.civil_unrest = 0.65
    env.city.budget_remaining = 500_000
    
    shannon = ShannonLoopEngine(env)
    reasoning = ReasoningAgent()
    
    state = {
        "trust_score": env.city.trust_score,
        "civil_unrest": env.city.civil_unrest,
        "budget_remaining": env.city.budget_remaining,
        "gdp_index": env.city.gdp_index,
        "survival_rate": env.city.survival_rate,
        "crime_index": env.city.crime_index,
        "disease_prevalence": env.city.disease_prevalence,
        "hospital_capacity": env.city.hospital_capacity,
        "rebel_strength": env.city.rebel_strength,
    }
    
    best_result, all_results = shannon.shannon_loop(
        state=state,
        agent_id="mayor",
        available_actions=["hold", "reduce_tax", "invest_in_welfare", "emergency_budget_release"]
    )
    
    reasoning_result = reasoning.generate_reasoning(
        state=state,
        crisis=["Low Trust", "High Unrest"],
        best_result=best_result,
        all_results=all_results
    )
    
    formatted = reasoning.format_for_ui(reasoning_result)
    print("\n" + "=" * 70)
    print("FORMATTED OUTPUT:")
    print("=" * 70)
    print(formatted)
    print("=" * 70)
    
    has_title = "CIVICMIND DECISION INTELLIGENCE REPORT" in formatted
    has_confidence = "CONFIDENCE" in formatted
    has_score_gap = "Score Gap" in formatted
    has_validation = "validated" in formatted.lower()
    
    print(f"\n✅ Has title: {has_title}")
    print(f"✅ Has confidence: {has_confidence}")
    print(f"✅ Has score gap: {has_score_gap}")
    print(f"✅ Has validation: {has_validation}")
    
    if has_title and has_confidence and has_score_gap and has_validation:
        print("✅ PASS: Complete formatted output")
        return True
    else:
        print("❌ FAIL: Formatted output incomplete")
        return False


def main():
    """Run all final polish tests"""
    print("\n" + "=" * 70)
    print("FINAL POLISH TEST SUITE")
    print("Testing: Failure Warning Fix + Score Gap + Validation")
    print("=" * 70)
    
    results = []
    
    results.append(("Failure Warning Always Present", test_failure_warning_always_present()))
    results.append(("Score Gap Visibility", test_score_gap_visibility()))
    results.append(("Validation Statement", test_validation_statement()))
    results.append(("Complete Formatted Output", test_complete_output()))
    
    print("\n" + "=" * 70)
    print("FINAL POLISH TEST RESULTS")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🏆 ALL FINAL POLISH TESTS PASSED!")
        print("💀 THERE IS NOTHING OBVIOUS LEFT TO CRITICIZE")
        print("🏆 SYSTEM IS WINNING CONTENDER!")
    else:
        print("\n⚠️ Some tests failed. Review needed.")


if __name__ == "__main__":
    main()
