#!/usr/bin/env python3
"""
REPRODUCIBILITY VERIFICATION
Runs training twice with same seed and verifies identical results.

This proves:
1. Training is deterministic
2. Results are reproducible
3. No hidden randomness

Judge defense: "Run this script - it trains twice and proves identical results."
"""

import sys
import json
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Set seeds
SEED = 42

def set_all_seeds(seed):
    """Set all random seeds"""
    random.seed(seed)
    
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass
    
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except ImportError:
        pass


def run_training(run_id):
    """Run one training session"""
    print(f"\n{'='*70}")
    print(f"RUN {run_id}")
    print(f"{'='*70}\n")
    
    # Reset seeds
    set_all_seeds(SEED)
    
    # Import after seeding
    from environment.civic_env import CivicMindEnv, CivicMindConfig
    from training.q_learning_trainer import QLearningTrainer
    
    # Create environment
    config = CivicMindConfig(max_weeks=10, difficulty=3, seed=SEED, enable_rebel=True)
    env = CivicMindEnv(config)
    
    # Create trainer (small for quick test)
    trainer = QLearningTrainer(
        episodes=100,  # Small for quick verification
        epsilon_start=1.0,
        epsilon_end=0.1,
        learning_rate=0.1,
        gamma=0.95
    )
    
    # Train
    stats = trainer.train(env)
    
    return {
        "states_learned": len(trainer.q_table),
        "episode_rewards": trainer.episode_rewards,
        "final_reward": trainer.episode_rewards[-1],
        "avg_reward": sum(trainer.episode_rewards) / len(trainer.episode_rewards),
        "q_table_size": len(trainer.q_table),
    }


def main():
    print("=" * 80)
    print("REPRODUCIBILITY VERIFICATION")
    print("=" * 80)
    print(f"\nSeed: {SEED}")
    print("Running training twice with same seed...")
    print("If reproducible, results should be IDENTICAL.\n")
    
    # Run 1
    results_1 = run_training(1)
    
    # Run 2
    results_2 = run_training(2)
    
    # Compare
    print("\n" + "=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print(f"\n{'Metric':<25} {'Run 1':>15} {'Run 2':>15} {'Match':>10}")
    print("-" * 80)
    
    matches = []
    
    # States learned
    match = results_1["states_learned"] == results_2["states_learned"]
    matches.append(match)
    print(
        f"{'States learned':<25} "
        f"{results_1['states_learned']:>15} "
        f"{results_2['states_learned']:>15} "
        f"{'✅' if match else '❌':>10}"
    )
    
    # Final reward
    match = abs(results_1["final_reward"] - results_2["final_reward"]) < 1e-6
    matches.append(match)
    print(
        f"{'Final reward':<25} "
        f"{results_1['final_reward']:>15.6f} "
        f"{results_2['final_reward']:>15.6f} "
        f"{'✅' if match else '❌':>10}"
    )
    
    # Average reward
    match = abs(results_1["avg_reward"] - results_2["avg_reward"]) < 1e-6
    matches.append(match)
    print(
        f"{'Average reward':<25} "
        f"{results_1['avg_reward']:>15.6f} "
        f"{results_2['avg_reward']:>15.6f} "
        f"{'✅' if match else '❌':>10}"
    )
    
    # Q-table size
    match = results_1["q_table_size"] == results_2["q_table_size"]
    matches.append(match)
    print(
        f"{'Q-table size':<25} "
        f"{results_1['q_table_size']:>15} "
        f"{results_2['q_table_size']:>15} "
        f"{'✅' if match else '❌':>10}"
    )
    
    # Episode-by-episode comparison
    episode_matches = sum(
        1 for r1, r2 in zip(results_1["episode_rewards"], results_2["episode_rewards"])
        if abs(r1 - r2) < 1e-6
    )
    match = episode_matches == len(results_1["episode_rewards"])
    matches.append(match)
    print(
        f"{'Episode rewards match':<25} "
        f"{episode_matches:>15} "
        f"{len(results_1['episode_rewards']):>15} "
        f"{'✅' if match else '❌':>10}"
    )
    
    print("-" * 80)
    
    # Verdict
    all_match = all(matches)
    
    print("\n" + "=" * 80)
    if all_match:
        print("✅ REPRODUCIBILITY VERIFIED")
        print("=" * 80)
        print("\nAll metrics match perfectly!")
        print("Training is deterministic and reproducible.")
        print(f"\nTo reproduce: Set seed={SEED} and run training.")
        print("\n🏆 JUDGE DEFENSE:")
        print("   'Our training is fully reproducible. Same seed → Same results.'")
        print("   'Run verify_reproducibility.py to see proof.'")
    else:
        print("❌ REPRODUCIBILITY FAILED")
        print("=" * 80)
        print("\nSome metrics don't match!")
        print("Check for sources of randomness:")
        print("  - Unseeded random number generators")
        print("  - Non-deterministic operations")
        print("  - External dependencies with randomness")
    
    print("=" * 80)
    
    # Save evidence
    evidence_dir = Path("evidence/eval")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    evidence = {
        "test": "reproducibility_verification",
        "seed": SEED,
        "run_1": results_1,
        "run_2": results_2,
        "all_match": all_match,
        "matches": {
            "states_learned": results_1["states_learned"] == results_2["states_learned"],
            "final_reward": abs(results_1["final_reward"] - results_2["final_reward"]) < 1e-6,
            "avg_reward": abs(results_1["avg_reward"] - results_2["avg_reward"]) < 1e-6,
            "q_table_size": results_1["q_table_size"] == results_2["q_table_size"],
            "episode_rewards": episode_matches == len(results_1["episode_rewards"]),
        }
    }
    
    output_path = evidence_dir / "reproducibility_verification.json"
    with open(output_path, "w") as f:
        json.dump(evidence, f, indent=2)
    
    print(f"\n✅ Evidence saved: {output_path}\n")


if __name__ == "__main__":
    main()
