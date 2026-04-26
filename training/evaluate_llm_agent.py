"""
Evaluate trained LLM agent vs untrained baseline
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

from environment import CivicMindEnv, CivicMindConfig
from training.llm_agent_wrapper import LLMAgentWrapper


def load_model(model_path: str, base_model: str = "Qwen/Qwen2.5-0.5B-Instruct"):
    """Load trained model"""
    print(f"Loading model from {model_path}...")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load base model
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True
        )
        
        # Load LoRA weights
        model = PeftModel.from_pretrained(model, model_path)
        model = model.merge_and_unload()  # Merge LoRA weights
        
        print("  ✅ Model loaded")
        return model, tokenizer
        
    except Exception as e:
        print(f"  ❌ Failed to load model: {e}")
        return None, None


def evaluate_agent(env: CivicMindEnv, wrapper: LLMAgentWrapper, 
                  n_episodes: int = 10, name: str = "Agent") -> dict:
    """
    Evaluate agent performance.
    
    Args:
        env: Environment
        wrapper: LLM wrapper (with or without model)
        n_episodes: Number of episodes
        name: Agent name for display
        
    Returns:
        Results dict
    """
    print(f"\nEvaluating {name}...")
    
    episode_rewards = []
    episode_lengths = []
    final_trusts = []
    final_survivals = []
    
    for episode in range(n_episodes):
        obs = env.reset()
        done = False
        episode_reward = 0.0
        step = 0
        
        while not done and step < 20:
            actions = {}
            
            for agent_id in env.AGENT_IDS:
                agent_obs = obs[agent_id]
                
                # Generate action using LLM
                action = wrapper.generate_action(agent_id, agent_obs, temperature=0.7)
                actions[agent_id] = {"policy_decision": action}
            
            obs, reward, done, info = env.step(actions)
            episode_reward += reward
            step += 1
        
        episode_rewards.append(episode_reward)
        episode_lengths.append(step)
        final_trusts.append(obs["mayor"]["trust_score"])
        final_survivals.append(obs["mayor"]["survival_rate"])
        
        if (episode + 1) % 5 == 0:
            print(f"  Episode {episode + 1}/{n_episodes} - Reward: {episode_reward:.4f}")
    
    results = {
        "mean_reward": sum(episode_rewards) / len(episode_rewards),
        "mean_length": sum(episode_lengths) / len(episode_lengths),
        "mean_trust": sum(final_trusts) / len(final_trusts),
        "mean_survival": sum(final_survivals) / len(final_survivals),
        "episode_rewards": episode_rewards
    }
    
    print(f"\n{name} Results:")
    print(f"  Mean reward: {results['mean_reward']:.4f}")
    print(f"  Mean trust: {results['mean_trust']:.2%}")
    print(f"  Mean survival: {results['mean_survival']:.2%}")
    
    return results


def main():
    print("\n" + "=" * 80)
    print("  LLM AGENT EVALUATION")
    print("=" * 80)
    print()
    
    # Configuration
    MODEL_PATH = "training/checkpoints/llm_agent"
    BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
    N_EPISODES = 10
    
    print(f"Configuration:")
    print(f"  Model path: {MODEL_PATH}")
    print(f"  Base model: {BASE_MODEL}")
    print(f"  Episodes: {N_EPISODES}")
    print()
    
    # Create environment
    config = CivicMindConfig(
        max_weeks=20,
        difficulty=3,
        enable_rebel=True,
        enable_schema_drift=True
    )
    env = CivicMindEnv(config)
    
    # Evaluate untrained baseline
    print("=" * 80)
    print("  BASELINE (Untrained LLM)")
    print("=" * 80)
    
    baseline_wrapper = LLMAgentWrapper()  # No model = random actions
    baseline_results = evaluate_agent(env, baseline_wrapper, N_EPISODES, "Baseline (Random)")
    
    # Load and evaluate trained model
    print("\n" + "=" * 80)
    print("  TRAINED LLM AGENT")
    print("=" * 80)
    
    if not Path(MODEL_PATH).exists():
        print(f"\n❌ Model not found: {MODEL_PATH}")
        print("Run: python training/train_llm_sft.py")
        return
    
    model, tokenizer = load_model(MODEL_PATH, BASE_MODEL)
    
    if model is None:
        print("\n❌ Failed to load model")
        return
    
    trained_wrapper = LLMAgentWrapper(model=model, tokenizer=tokenizer)
    trained_results = evaluate_agent(env, trained_wrapper, N_EPISODES, "Trained LLM")
    
    # Compare results
    print("\n" + "=" * 80)
    print("  COMPARISON")
    print("=" * 80)
    print()
    
    reward_improvement = ((trained_results["mean_reward"] - baseline_results["mean_reward"]) 
                         / baseline_results["mean_reward"] * 100)
    trust_improvement = ((trained_results["mean_trust"] - baseline_results["mean_trust"]) 
                        / baseline_results["mean_trust"] * 100)
    
    print(f"Metric              Baseline    Trained     Improvement")
    print(f"─" * 60)
    print(f"Mean Reward         {baseline_results['mean_reward']:.4f}      {trained_results['mean_reward']:.4f}      {reward_improvement:+.1f}%")
    print(f"Mean Trust          {baseline_results['mean_trust']:.2%}       {trained_results['mean_trust']:.2%}       {trust_improvement:+.1f}%")
    print(f"Mean Survival       {baseline_results['mean_survival']:.2%}       {trained_results['mean_survival']:.2%}")
    print()
    
    # Verdict
    if reward_improvement > 10:
        print("✅ STRONG IMPROVEMENT - LLM learned effective policies!")
    elif reward_improvement > 5:
        print("✅ MODERATE IMPROVEMENT - LLM shows learning")
    elif reward_improvement > 0:
        print("⚠️  WEAK IMPROVEMENT - May need more training data or epochs")
    else:
        print("❌ NO IMPROVEMENT - Check training data quality")
    
    print()
    print("=" * 80)
    print("✅ EVALUATION COMPLETE")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
