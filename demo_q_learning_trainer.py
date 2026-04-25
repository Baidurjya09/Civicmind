"""
Demonstration of QLearningTrainer for Colab Notebook Integration
Shows how to use the trainer in a notebook cell
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from training.q_learning_trainer import QLearningTrainer
from environment import CivicMindEnv, CivicMindConfig


def demo_notebook_usage():
    """
    Demonstrates how to use QLearningTrainer in a Colab notebook cell.
    This is the code that would go in the notebook.
    """
    
    print("=" * 70)
    print("  CivicMind Q-Learning Training Demo")
    print("  (Notebook Cell Example)")
    print("=" * 70)
    print()
    
    # Step 1: Create trainer with default parameters
    print("Step 1: Creating Q-Learning Trainer...")
    trainer = QLearningTrainer(
        episodes=2000,           # Number of training episodes
        epsilon_start=1.0,       # Start with full exploration
        epsilon_end=0.1,         # End with 10% exploration
        learning_rate=0.1,       # Learning rate (alpha)
        gamma=0.95               # Discount factor
    )
    print("✓ Trainer created")
    print()
    
    # Step 2: Create environment
    print("Step 2: Creating CivicMind Environment...")
    config = CivicMindConfig(
        max_weeks=20,            # 20-week episodes
        difficulty=3,            # Medium difficulty
        enable_rebel=True,       # Enable rebel spawning
        enable_schema_drift=True # Enable schema drift
    )
    env = CivicMindEnv(config)
    print("✓ Environment created")
    print()
    
    # Step 3: Train (this will show progress every 200 episodes)
    print("Step 3: Training...")
    print("(Progress will be shown every 200 episodes)")
    print()
    
    stats = trainer.train(env)
    
    # Step 4: Save checkpoint
    print("\nStep 4: Saving checkpoint...")
    checkpoint_path = "training/checkpoints/rl_policy.pkl"
    trainer.save_checkpoint(checkpoint_path)
    print()
    
    # Step 5: Display summary
    print("=" * 70)
    print("  Training Summary")
    print("=" * 70)
    print(f"Episodes completed: {stats['episodes']}")
    print(f"States learned: {stats['states_learned']}")
    print(f"Training time: {stats['training_time']:.2f}s")
    print(f"Final epsilon: {stats['final_epsilon']:.3f}")
    print(f"Checkpoint saved: {checkpoint_path}")
    print()
    
    # Step 6: Test the trained policy
    print("Step 6: Testing trained policy...")
    policy_fn = trainer.get_policy(epsilon=0.0)  # Greedy policy (no exploration)
    
    # Run a test episode
    obs = env.reset()
    done = False
    test_reward = 0.0
    steps = 0
    
    while not done and steps < 20:
        actions = policy_fn(obs)
        obs, reward, done, info = env.step(actions)
        test_reward += reward
        steps += 1
    
    print(f"✓ Test episode completed")
    print(f"  Steps: {steps}")
    print(f"  Total reward: {test_reward:.4f}")
    print(f"  Avg reward per step: {test_reward / steps:.4f}")
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Next steps for notebook:")
    print("  1. Use this trained policy for evaluation")
    print("  2. Compare against random/heuristic baselines")
    print("  3. Generate training curve plots")
    print("  4. Export results for submission")
    print()


if __name__ == "__main__":
    demo_notebook_usage()
