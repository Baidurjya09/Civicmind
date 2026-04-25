# Q-Learning Trainer for CivicMind

## Overview

The `QLearningTrainer` class implements tabular Q-learning for the CivicMind multi-agent governance system. It provides a fast, CPU-based reinforcement learning solution that trains in seconds and serves as a validation path for the training pipeline.

## Features

- **Fast Training**: Completes 2000 episodes in ~3 seconds on CPU
- **Multi-Agent Coordination**: Learns policies for all 6 government agents
- **State Discretization**: Converts continuous observations to discrete states
- **Epsilon-Greedy Exploration**: Linear decay from full exploration to exploitation
- **Progress Tracking**: Updates every 200 episodes with key metrics
- **Checkpointing**: Save/load Q-tables for reproducibility
- **Visualization**: Built-in training curve plotting

## Quick Start

```python
from training.q_learning_trainer import QLearningTrainer
from environment import CivicMindEnv, CivicMindConfig

# Create trainer
trainer = QLearningTrainer(
    episodes=2000,
    epsilon_start=1.0,
    epsilon_end=0.1,
    learning_rate=0.1
)

# Create environment
config = CivicMindConfig(max_weeks=20, difficulty=3)
env = CivicMindEnv(config)

# Train
stats = trainer.train(env)

# Save checkpoint
trainer.save_checkpoint("training/checkpoints/rl_policy.pkl")

# Generate plot
trainer.plot_training_curve(save_path="evidence/plots/training_curve.png")
```

## Class Reference

### Constructor

```python
QLearningTrainer(
    episodes: int = 2000,
    epsilon_start: float = 1.0,
    epsilon_end: float = 0.1,
    learning_rate: float = 0.1,
    gamma: float = 0.95
)
```

**Parameters:**
- `episodes`: Number of training episodes (default: 2000)
- `epsilon_start`: Initial exploration rate (default: 1.0)
- `epsilon_end`: Final exploration rate (default: 0.1)
- `learning_rate`: Learning rate (alpha) for Q-value updates (default: 0.1)
- `gamma`: Discount factor for future rewards (default: 0.95)

### Methods

#### `get_state_key(observation: Dict) -> str`

Converts continuous observation to discrete state key for tabular Q-learning.

**Discretization:**
- Trust score: 0.1 bins (0.0, 0.1, 0.2, ..., 1.0)
- GDP index: 0.1 bins (0.0, 0.1, 0.2, ..., 2.0+)
- Survival rate: 0.1 bins (0.0, 0.1, ..., 1.0)
- Budget: 100k bins
- Crisis count: exact count
- Rebel active: binary (0 or 1)

**Returns:** Hashable state key string

#### `select_action(state_key: str, agent_id: str, epsilon: float) -> str`

Selects action using epsilon-greedy policy.

**Parameters:**
- `state_key`: Current state key
- `agent_id`: Agent identifier (e.g., "mayor", "health_minister")
- `epsilon`: Current exploration rate

**Returns:** Action string (e.g., "hold", "invest_in_welfare")

#### `update_q_value(state: str, action: str, reward: float, next_state: str, agent_id: str) -> None`

Updates Q-value using Q-learning update rule:

```
Q(s,a) = Q(s,a) + lr * (r + gamma * max_a' Q(s',a') - Q(s,a))
```

**Parameters:**
- `state`: Current state key
- `action`: Action taken
- `reward`: Reward received
- `next_state`: Next state key
- `agent_id`: Agent identifier

#### `train(env: CivicMindEnv = None) -> Dict`

Runs training loop with linear epsilon decay.

**Parameters:**
- `env`: CivicMind environment (creates default if None)

**Returns:** Training statistics dict with:
- `episodes`: Number of episodes completed
- `states_learned`: Total states in Q-table
- `final_epsilon`: Final exploration rate
- `training_time`: Training duration in seconds
- `episode_rewards`: List of rewards per episode
- `episode_lengths`: List of steps per episode
- `q_table_sizes`: List of Q-table sizes over time

**Progress Updates:** Displays every 200 episodes showing:
- Episode number
- Current epsilon value
- States learned
- Average reward (last 200 episodes)

#### `save_checkpoint(path: str) -> None`

Saves Q-table to pickle file.

**Parameters:**
- `path`: File path for checkpoint (e.g., "training/checkpoints/rl_policy.pkl")

**Creates:** Directory if it doesn't exist

#### `load_checkpoint(path: str) -> None`

Loads Q-table from pickle file.

**Parameters:**
- `path`: File path for checkpoint

#### `get_policy(epsilon: float = 0.0) -> Callable`

Returns policy function for evaluation.

**Parameters:**
- `epsilon`: Exploration rate (0.0 for greedy policy)

**Returns:** Policy function that takes observation and returns actions dict

**Example:**
```python
policy_fn = trainer.get_policy(epsilon=0.0)
obs = env.reset()
actions = policy_fn(obs)
```

#### `plot_training_curve(save_path: str = None, show: bool = True) -> Figure`

Generates training curve plot showing reward progression and Q-table growth.

**Parameters:**
- `save_path`: Optional path to save plot (e.g., "evidence/plots/training_curve.png")
- `show`: Whether to display the plot (set False for headless environments)

**Returns:** Matplotlib figure object

**Plots:**
1. Reward progression (raw + smoothed)
2. Q-table growth (states learned over time)

## Action Space

The trainer supports the following actions per agent:

**Mayor:**
- `hold`: No action
- `emergency_budget_release`: Release emergency funds
- `invest_in_welfare`: Invest in citizen welfare
- `reduce_tax`: Reduce tax burden

**Health Minister:**
- `hold`: No action
- `mass_vaccination`: Launch vaccination campaign
- `increase_hospital_staff`: Hire more medical staff

**Finance Officer:**
- `hold`: No action
- `issue_bonds`: Issue government bonds
- `stimulus_package`: Economic stimulus

**Police Chief:**
- `hold`: No action
- `community_policing`: Community engagement

**Infrastructure Head:**
- `hold`: No action
- `emergency_repairs`: Emergency infrastructure repairs

**Media Spokesperson:**
- `hold`: No action
- `press_conference`: Hold press conference
- `social_media_campaign`: Launch social media campaign

## Performance

**Training Speed:**
- 2000 episodes: ~3 seconds (CPU)
- 500 episodes: ~0.7 seconds (CPU)

**Memory Usage:**
- Q-table size: ~500 states (typical)
- Memory footprint: <10 MB

**Learning Efficiency:**
- States learned: 300-500 (typical)
- Convergence: ~1000 episodes
- Improvement over random: +20-30%

## Integration with Colab Notebook

The trainer is designed for seamless integration with Google Colab notebooks:

```python
# Notebook Cell: Q-Learning Training

from training.q_learning_trainer import QLearningTrainer
from environment import CivicMindEnv, CivicMindConfig

# Create trainer
trainer = QLearningTrainer(episodes=2000)

# Create environment
config = CivicMindConfig(max_weeks=20, difficulty=3)
env = CivicMindEnv(config)

# Train (shows progress every 200 episodes)
stats = trainer.train(env)

# Save checkpoint
trainer.save_checkpoint("training/checkpoints/rl_policy.pkl")

# Generate plot
trainer.plot_training_curve(
    save_path="evidence/plots/training_curve.png",
    show=True
)

# Display summary
print(f"✅ Training complete!")
print(f"   States learned: {stats['states_learned']}")
print(f"   Training time: {stats['training_time']:.2f}s")
```

## Troubleshooting

**Issue: Training is slow**
- Solution: Reduce `episodes` parameter (e.g., 500 for quick tests)

**Issue: Q-table not growing**
- Solution: Increase `epsilon_start` for more exploration

**Issue: Poor performance**
- Solution: Increase `learning_rate` or `episodes`

**Issue: Plot not showing**
- Solution: Set `show=False` in headless environments (Colab, Kaggle)

## Requirements

**Python Packages:**
- `pickle` (standard library)
- `time` (standard library)
- `matplotlib` (for plotting)
- `numpy` (for smoothing)

**CivicMind Components:**
- `environment.CivicMindEnv`
- `environment.CivicMindConfig`

## Testing

Run the test suite:

```bash
python test_q_learning_trainer.py
```

Run the demo:

```bash
python demo_q_learning_trainer.py
```

Test plotting:

```bash
python test_plotting.py
```

## References

- **Q-Learning Algorithm**: Watkins & Dayan (1992)
- **Epsilon-Greedy Exploration**: Sutton & Barto (2018)
- **Multi-Agent RL**: Busoniu et al. (2008)

## License

Part of the CivicMind project. See main LICENSE file.
