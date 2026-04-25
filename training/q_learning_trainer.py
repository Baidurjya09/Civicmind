"""
Q-Learning Trainer for CivicMind
Implements tabular reinforcement learning for the multi-agent governance system.
"""

import pickle
import time
from typing import Dict, Tuple, Any
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from environment import CivicMindEnv, CivicMindConfig


class QLearningTrainer:
    """
    Q-Learning trainer for CivicMind multi-agent system.
    
    Implements tabular Q-learning with:
    - Epsilon-greedy exploration with linear decay
    - State discretization for continuous observations
    - Multi-agent action coordination
    - Progress tracking and checkpointing
    """
    
    # Action space per agent
    ACTIONS = {
        "mayor": ["hold", "emergency_budget_release", "invest_in_welfare", "reduce_tax"],
        "health_minister": ["hold", "mass_vaccination", "increase_hospital_staff"],
        "finance_officer": ["hold", "issue_bonds", "stimulus_package"],
        "police_chief": ["hold", "community_policing"],
        "infrastructure_head": ["hold", "emergency_repairs"],
        "media_spokesperson": ["hold", "press_conference", "social_media_campaign"]
    }
    
    def __init__(
        self,
        episodes: int = 2000,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.1,
        learning_rate: float = 0.1,
        gamma: float = 0.95
    ):
        """
        Initialize Q-Learning trainer.
        
        Args:
            episodes: Number of training episodes
            epsilon_start: Initial exploration rate
            epsilon_end: Final exploration rate
            learning_rate: Learning rate (alpha) for Q-value updates
            gamma: Discount factor for future rewards
        """
        self.episodes = episodes
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.learning_rate = learning_rate
        self.gamma = gamma
        
        # Q-table: {state_key: {agent_id: {action: q_value}}}
        self.q_table = {}
        
        # Training statistics
        self.episode_rewards = []
        self.episode_lengths = []
        self.q_table_sizes = []
    
    def get_state_key(self, observation: Dict[str, Any]) -> str:
        """
        Convert continuous observation to discrete state key.
        
        Discretizes trust, GDP, and survival into bins for tabular Q-learning.
        Uses mayor's observation as it has access to global state.
        
        Args:
            observation: Environment observation dict
            
        Returns:
            Hashable state key (tuple converted to string)
        """
        mayor_obs = observation["mayor"]
        
        # Discretize continuous values into bins
        trust = round(mayor_obs["trust_score"] * 10) / 10  # 0.0, 0.1, 0.2, ..., 1.0
        gdp = round(mayor_obs["gdp_index"] * 10) / 10  # 0.0, 0.1, 0.2, ..., 2.0+
        survival = round(mayor_obs["survival_rate"] * 10) / 10  # 0.0, 0.1, ..., 1.0
        
        # Additional context
        budget_bin = int(mayor_obs["budget_remaining"] / 100000)  # 100k bins
        crisis_count = len(mayor_obs["active_crises"])
        rebel_active = int(mayor_obs["rebel_active"])
        
        state_tuple = (trust, gdp, survival, budget_bin, crisis_count, rebel_active)
        return str(state_tuple)
    
    def select_action(self, state_key: str, agent_id: str, epsilon: float) -> str:
        """
        Select action using epsilon-greedy policy.
        
        Args:
            state_key: Current state key
            agent_id: Agent identifier
            epsilon: Current exploration rate
            
        Returns:
            Selected action string
        """
        import random
        
        # Initialize Q-values for new state
        if state_key not in self.q_table:
            self.q_table[state_key] = {
                agent: {action: 0.0 for action in self.ACTIONS[agent]}
                for agent in self.ACTIONS.keys()
            }
        
        # Epsilon-greedy selection
        if random.random() < epsilon:
            # Explore: random action
            action = random.choice(self.ACTIONS[agent_id])
        else:
            # Exploit: best known action
            q_values = self.q_table[state_key][agent_id]
            action = max(q_values, key=q_values.get)
        
        return action
    
    def update_q_value(
        self,
        state: str,
        action: str,
        reward: float,
        next_state: str,
        agent_id: str
    ) -> None:
        """
        Update Q-value using Q-learning update rule.
        
        Q(s,a) = Q(s,a) + lr * (r + gamma * max_a' Q(s',a') - Q(s,a))
        
        Args:
            state: Current state key
            action: Action taken
            reward: Reward received
            next_state: Next state key
            agent_id: Agent identifier
        """
        # Initialize Q-values for new states
        if state not in self.q_table:
            self.q_table[state] = {
                agent: {act: 0.0 for act in self.ACTIONS[agent]}
                for agent in self.ACTIONS.keys()
            }
        
        if next_state not in self.q_table:
            self.q_table[next_state] = {
                agent: {act: 0.0 for act in self.ACTIONS[agent]}
                for agent in self.ACTIONS.keys()
            }
        
        # Q-learning update
        current_q = self.q_table[state][agent_id][action]
        max_next_q = max(self.q_table[next_state][agent_id].values())
        
        new_q = current_q + self.learning_rate * (
            reward + self.gamma * max_next_q - current_q
        )
        
        self.q_table[state][agent_id][action] = new_q
    
    def train(self, env: CivicMindEnv = None) -> Dict[str, Any]:
        """
        Run training loop with linear epsilon decay.
        
        Args:
            env: CivicMind environment (creates default if None)
            
        Returns:
            Training statistics dict
        """
        if env is None:
            config = CivicMindConfig(max_weeks=20, difficulty=3)
            env = CivicMindEnv(config)
        
        print("=" * 70)
        print("  Q-Learning Training")
        print("=" * 70)
        print(f"Episodes: {self.episodes}")
        print(f"Epsilon: {self.epsilon_start} → {self.epsilon_end}")
        print(f"Learning rate: {self.learning_rate}")
        print(f"Gamma: {self.gamma}")
        print()
        
        start_time = time.time()
        
        for episode in range(self.episodes):
            # Linear epsilon decay
            epsilon = self.epsilon_start - (self.epsilon_start - self.epsilon_end) * (
                episode / self.episodes
            )
            
            # Reset environment
            obs = env.reset()
            done = False
            episode_reward = 0.0
            step = 0
            
            # Store state-action pairs for updates
            agent_states = {}
            agent_actions = {}
            
            while not done:
                # Select actions for all agents
                actions = {}
                for agent_id in env.AGENT_IDS:
                    state_key = self.get_state_key(obs)
                    action = self.select_action(state_key, agent_id, epsilon)
                    
                    actions[agent_id] = {"policy_decision": action}
                    agent_states[agent_id] = state_key
                    agent_actions[agent_id] = action
                
                # Environment step
                next_obs, reward, done, info = env.step(actions)
                
                # Update Q-values for all agents
                next_state_key = self.get_state_key(next_obs)
                for agent_id in env.AGENT_IDS:
                    self.update_q_value(
                        agent_states[agent_id],
                        agent_actions[agent_id],
                        reward,
                        next_state_key,
                        agent_id
                    )
                
                episode_reward += reward
                obs = next_obs
                step += 1
            
            # Record statistics
            self.episode_rewards.append(episode_reward)
            self.episode_lengths.append(step)
            self.q_table_sizes.append(len(self.q_table))
            
            # Progress updates every 200 episodes
            if (episode + 1) % 200 == 0:
                avg_reward = sum(self.episode_rewards[-200:]) / 200
                print(f"Episode {episode + 1}/{self.episodes}")
                print(f"  Epsilon: {epsilon:.3f}")
                print(f"  States learned: {len(self.q_table)}")
                print(f"  Avg reward (last 200): {avg_reward:.4f}")
                print()
        
        training_time = time.time() - start_time
        
        # Final statistics
        print("=" * 70)
        print("Training Complete!")
        print("=" * 70)
        print(f"Total states learned: {len(self.q_table)}")
        print(f"Final epsilon: {epsilon:.3f}")
        print(f"Training time: {training_time:.2f}s")
        print(f"Final avg reward (last 100): {sum(self.episode_rewards[-100:]) / 100:.4f}")
        print()
        
        return {
            "episodes": self.episodes,
            "states_learned": len(self.q_table),
            "final_epsilon": epsilon,
            "training_time": training_time,
            "episode_rewards": self.episode_rewards,
            "episode_lengths": self.episode_lengths,
            "q_table_sizes": self.q_table_sizes,
        }
    
    def save_checkpoint(self, path: str) -> None:
        """
        Save Q-table to pickle file.
        
        Args:
            path: File path for checkpoint
        """
        import os
        
        # Create directory if needed
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump(self.q_table, f)
        
        print(f"✅ Checkpoint saved: {path}")
        print(f"   States: {len(self.q_table)}")
    
    def load_checkpoint(self, path: str) -> None:
        """
        Load Q-table from pickle file.
        
        Args:
            path: File path for checkpoint
        """
        with open(path, 'rb') as f:
            self.q_table = pickle.load(f)
        
        print(f"✅ Checkpoint loaded: {path}")
        print(f"   States: {len(self.q_table)}")
    
    def get_policy(self, epsilon: float = 0.0):
        """
        Get policy function for evaluation.
        
        Args:
            epsilon: Exploration rate (0.0 for greedy policy)
            
        Returns:
            Policy function that takes (agent_id, agent_obs) and returns action dict
        """
        def policy_fn(agent_id, agent_obs):
            # Extract key state features from agent observation
            # The agent_obs contains the relevant state information
            trust = agent_obs.get("trust_score", 0.75)
            gdp = agent_obs.get("gdp_growth", 0.02)
            survival = agent_obs.get("survival_rate", 0.95)
            budget = agent_obs.get("budget_remaining", 5000)
            crisis_count = len(agent_obs.get("active_crises", []))
            rebel_active = 1 if agent_obs.get("rebel_active", False) else 0
            
            # Create state key from these features
            state_key = (
                int(trust * 10),  # Discretize to 0-10
                int(gdp * 100),   # Discretize to integer percentage
                int(survival * 10),  # Discretize to 0-10
                int(budget / 1000),  # Discretize to thousands
                crisis_count,
                rebel_active
            )
            
            # Select action using Q-table
            action = self.select_action(state_key, agent_id, epsilon)
            return {"policy_decision": action}
        
        return policy_fn
    
    def plot_training_curve(self, save_path: str = None, show: bool = True):
        """
        Generate training curve plot showing reward progression.
        
        Args:
            save_path: Optional path to save plot (e.g., 'evidence/plots/training_curve.png')
            show: Whether to display the plot (set False for notebook/headless environments)
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            print("⚠️  matplotlib not available, skipping plot generation")
            return
        
        if not self.episode_rewards:
            print("⚠️  No training data available for plotting")
            return
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        episodes = list(range(1, len(self.episode_rewards) + 1))
        
        # Plot 1: Reward progression with smoothing
        ax1.plot(episodes, self.episode_rewards, alpha=0.3, color='blue', label='Raw')
        
        # Smooth curve (moving average)
        window = min(100, len(self.episode_rewards) // 10)
        if window > 1:
            smoothed = np.convolve(
                self.episode_rewards,
                np.ones(window) / window,
                mode='valid'
            )
            smooth_episodes = list(range(window, len(self.episode_rewards) + 1))
            ax1.plot(smooth_episodes, smoothed, color='blue', linewidth=2, label=f'Smoothed (window={window})')
        
        ax1.set_xlabel('Episode', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Reward', fontsize=11, fontweight='bold')
        ax1.set_title('Training Reward Progression', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # Plot 2: Q-table growth
        ax2.plot(episodes, self.q_table_sizes, color='purple', linewidth=2)
        ax2.set_xlabel('Episode', fontsize=11, fontweight='bold')
        ax2.set_ylabel('States Learned', fontsize=11, fontweight='bold')
        ax2.set_title('Q-Table Growth (Learning Progress)', fontsize=12, fontweight='bold')
        ax2.grid(alpha=0.3)
        
        # Add annotation
        final_states = self.q_table_sizes[-1]
        ax2.annotate(
            f'{final_states} states',
            xy=(len(episodes), final_states),
            xytext=(len(episodes) * 0.6, final_states * 0.5),
            arrowprops=dict(arrowstyle='->', color='purple', lw=2),
            fontsize=11,
            fontweight='bold'
        )
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            import os
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✅ Training curve saved: {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close()
        
        return fig


if __name__ == "__main__":
    """Quick test of Q-learning trainer"""
    print("Testing Q-Learning Trainer...")
    print()
    
    # Create trainer
    trainer = QLearningTrainer(
        episodes=100,  # Quick test
        epsilon_start=1.0,
        epsilon_end=0.1,
        learning_rate=0.1
    )
    
    # Train
    stats = trainer.train()
    
    # Save checkpoint
    trainer.save_checkpoint("training/checkpoints/test_rl_policy.pkl")
    
    print("\n✅ Test complete!")
