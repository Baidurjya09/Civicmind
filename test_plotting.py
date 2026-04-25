"""Test plotting functionality"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from training.q_learning_trainer import QLearningTrainer
from environment import CivicMindEnv, CivicMindConfig

# Quick training
trainer = QLearningTrainer(episodes=500)
config = CivicMindConfig(max_weeks=20, difficulty=3)
env = CivicMindEnv(config)

print("Training for 500 episodes...")
stats = trainer.train(env)

print("\nGenerating training curve plot...")
trainer.plot_training_curve(
    save_path="evidence/plots/test_training_curve.png",
    show=False  # Don't show in headless environment
)

print("\n✅ Plot test complete!")
print(f"   Plot saved to: evidence/plots/test_training_curve.png")
