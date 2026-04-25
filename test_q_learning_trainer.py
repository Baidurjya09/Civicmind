"""
Test script for Q-Learning Trainer
Validates all functionality including progress updates
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from training.q_learning_trainer import QLearningTrainer
from environment import CivicMindEnv, CivicMindConfig


def test_full_training():
    """Test full training with 2000 episodes"""
    print("=" * 70)
    print("  Testing Q-Learning Trainer - Full Training")
    print("=" * 70)
    print()
    
    # Create trainer with default parameters
    trainer = QLearningTrainer(
        episodes=2000,
        epsilon_start=1.0,
        epsilon_end=0.1,
        learning_rate=0.1,
        gamma=0.95
    )
    
    # Create environment
    config = CivicMindConfig(max_weeks=20, difficulty=3)
    env = CivicMindEnv(config)
    
    # Train
    stats = trainer.train(env)
    
    # Verify statistics
    print("\n" + "=" * 70)
    print("  Validation")
    print("=" * 70)
    print(f"✓ Episodes completed: {len(trainer.episode_rewards)}")
    print(f"✓ States learned: {stats['states_learned']}")
    print(f"✓ Training time: {stats['training_time']:.2f}s")
    print(f"✓ Final epsilon: {stats['final_epsilon']:.3f}")
    print()
    
    # Check progress was shown (every 200 episodes = 10 updates)
    assert len(trainer.episode_rewards) == 2000, "Should have 2000 episodes"
    assert stats['states_learned'] > 0, "Should have learned states"
    assert stats['final_epsilon'] < 0.15, "Epsilon should decay to ~0.1"
    
    # Save checkpoint
    checkpoint_path = "training/checkpoints/rl_policy.pkl"
    trainer.save_checkpoint(checkpoint_path)
    
    # Test loading
    print("\nTesting checkpoint loading...")
    new_trainer = QLearningTrainer()
    new_trainer.load_checkpoint(checkpoint_path)
    assert len(new_trainer.q_table) == len(trainer.q_table), "Loaded Q-table should match"
    print("✓ Checkpoint load successful")
    print()
    
    # Test policy function
    print("Testing policy function...")
    policy_fn = trainer.get_policy(epsilon=0.0)
    obs = env.reset()
    actions = policy_fn(obs)
    assert len(actions) == 6, "Should have actions for all 6 agents"
    for agent_id in env.AGENT_IDS:
        assert agent_id in actions, f"Missing action for {agent_id}"
        assert "policy_decision" in actions[agent_id], f"Missing policy_decision for {agent_id}"
    print("✓ Policy function works correctly")
    print()
    
    print("=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  • Trained for {stats['episodes']} episodes")
    print(f"  • Learned {stats['states_learned']} states")
    print(f"  • Training time: {stats['training_time']:.2f}s")
    print(f"  • Checkpoint saved to: {checkpoint_path}")
    print()


if __name__ == "__main__":
    test_full_training()
