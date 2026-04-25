#!/usr/bin/env python3
"""
REPRODUCIBLE Q-LEARNING TRAINING
Trains Q-learning policy with fixed seeds for complete reproducibility.

This script ensures:
1. Fixed random seeds (Python, NumPy, environment)
2. Deterministic training
3. Checkpoint saving
4. Evidence logging
5. Training curve generation

Run this for your final training evidence.
"""

import sys
import json
import pickle
import random
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# CRITICAL: Set all random seeds BEFORE any imports that use randomness
SEED = 42

print("=" * 80)
print("REPRODUCIBLE Q-LEARNING TRAINING")
print("=" * 80)
print(f"\n🔒 Setting random seeds: {SEED}\n")

# Set Python random seed
random.seed(SEED)

# Set NumPy seed
try:
    import numpy as np
    np.random.seed(SEED)
    print("✅ NumPy seed set")
except ImportError:
    print("⚠️  NumPy not available")

# Set PyTorch seed (if available)
try:
    import torch
    torch.manual_seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(SEED)
        torch.cuda.manual_seed_all(SEED)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    print("✅ PyTorch seed set")
except ImportError:
    print("⚠️  PyTorch not available")

print()

# Now import training modules
from environment.civic_env import CivicMindEnv, CivicMindConfig
from training.q_learning_trainer import QLearningTrainer


def main():
    """Run reproducible training with fixed seeds"""
    
    # Create environment with fixed seed
    print("📦 Creating environment...")
    config = CivicMindConfig(
        max_weeks=20,
        difficulty=3,
        seed=SEED,  # Environment seed
        enable_rebel=True
    )
    env = CivicMindEnv(config)
    print(f"✅ Environment created (seed={SEED})")
    print()
    
    # Create trainer
    print("🧠 Creating Q-learning trainer...")
    trainer = QLearningTrainer(
        episodes=2000,
        epsilon_start=1.0,
        epsilon_end=0.1,
        learning_rate=0.1,
        gamma=0.95
    )
    print("✅ Trainer created")
    print()
    
    # Train
    print("🚀 Starting training...\n")
    stats = trainer.train(env)
    
    # Save checkpoint
    print("\n💾 Saving checkpoint...")
    checkpoint_path = "training/checkpoints/rl_policy.pkl"
    
    # Save Q-table with metadata
    checkpoint_data = {
        "q_table": trainer.q_table,
        "seed": SEED,
        "episodes": trainer.episodes,
        "states_learned": len(trainer.q_table),
        "training_time": stats["training_time"],
        "config": {
            "epsilon_start": trainer.epsilon_start,
            "epsilon_end": trainer.epsilon_end,
            "learning_rate": trainer.learning_rate,
            "gamma": trainer.gamma,
        }
    }
    
    Path(checkpoint_path).parent.mkdir(parents=True, exist_ok=True)
    with open(checkpoint_path, "wb") as f:
        pickle.dump(checkpoint_data, f)
    
    print(f"✅ Checkpoint saved: {checkpoint_path}")
    print(f"   States: {len(trainer.q_table)}")
    print(f"   Seed: {SEED}")
    print()
    
    # Save training statistics
    print("📊 Saving training statistics...")
    evidence_dir = Path("evidence/eval")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    training_evidence = {
        "seed": SEED,
        "reproducible": True,
        "episodes": stats["episodes"],
        "states_learned": stats["states_learned"],
        "training_time": stats["training_time"],
        "final_avg_reward": sum(trainer.episode_rewards[-100:]) / 100,
        "episode_rewards": trainer.episode_rewards,
        "episode_lengths": trainer.episode_lengths,
        "q_table_sizes": trainer.q_table_sizes,
        "hyperparameters": {
            "epsilon_start": trainer.epsilon_start,
            "epsilon_end": trainer.epsilon_end,
            "learning_rate": trainer.learning_rate,
            "gamma": trainer.gamma,
        }
    }
    
    stats_path = evidence_dir / "training_results.json"
    with open(stats_path, "w") as f:
        json.dump(training_evidence, f, indent=2)
    
    print(f"✅ Statistics saved: {stats_path}")
    print()
    
    # Generate training curve
    print("📈 Generating training curve...")
    plot_path = "evidence/plots/training_curve.png"
    Path(plot_path).parent.mkdir(parents=True, exist_ok=True)
    
    trainer.plot_training_curve(save_path=plot_path, show=False)
    print()
    
    # Summary
    print("=" * 80)
    print("TRAINING COMPLETE ✅")
    print("=" * 80)
    print(f"\n📊 RESULTS:")
    print(f"   Seed: {SEED} (reproducible)")
    print(f"   Episodes: {stats['episodes']}")
    print(f"   States learned: {stats['states_learned']}")
    print(f"   Training time: {stats['training_time']:.2f}s")
    print(f"   Final avg reward: {sum(trainer.episode_rewards[-100:]) / 100:.4f}")
    print()
    print(f"📁 SAVED FILES:")
    print(f"   ✅ {checkpoint_path}")
    print(f"   ✅ {stats_path}")
    print(f"   ✅ {plot_path}")
    print()
    print("🎯 REPRODUCIBILITY:")
    print(f"   To reproduce: python training/train_with_seeds.py")
    print(f"   Same seed ({SEED}) → Same results")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
