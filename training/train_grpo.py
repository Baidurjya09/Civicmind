"""
CivicMind — GRPO-Style RL Training
Group Relative Policy Optimization for multi-agent governance
"""

import os
import json
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
import torch.nn.functional as F
from datasets import Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
)
from peft import LoraConfig, get_peft_model, TaskType
from tqdm import tqdm
import numpy as np

from rewards.reward_model import RewardModel

print("=" * 70)
print("  CivicMind — GRPO-Style RL Training")
print("=" * 70)
print()

# Config
parser = argparse.ArgumentParser()
parser.add_argument("--epochs", type=int, default=3)
parser.add_argument("--batch_size", type=int, default=2)
parser.add_argument("--n_samples_per_prompt", type=int, default=4, help="GRPO: samples per prompt")
parser.add_argument("--output_dir", type=str, default="training/checkpoints/civicmind_grpo")
parser.add_argument("--learning_rate", type=float, default=2e-5)
parser.add_argument("--max_length", type=int, default=512)
parser.add_argument("--max_samples", type=int, default=0, help="Use first N samples for quick proof runs (0 = all)")
parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
args = parser.parse_args()

# Reproducibility
np.random.seed(args.seed)
torch.manual_seed(args.seed)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(args.seed)

# Check GPU
print("Checking GPU...")
if torch.cuda.is_available():
    print(f"  ✅ GPU: {torch.cuda.get_device_name(0)}")
    print(f"  ✅ VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    device = "cuda"
else:
    print("  ⚠️  No GPU detected - using CPU (will be slow)")
    device = "cpu"
print()

# Load dataset
print("Loading dataset...")
dataset_path = "training/civicmind_dataset.jsonl"
samples = []
with open(dataset_path) as f:
    for line in f:
        samples.append(json.loads(line))

print(f"  ✅ Loaded {len(samples)} samples")
if args.max_samples and args.max_samples > 0:
    samples = samples[:args.max_samples]
    print(f"  ✅ Using subset for this run: {len(samples)} samples")
print()

# Load model
print("Loading Qwen 2.5 0.5B model...")
model_name = "Qwen/Qwen2.5-0.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    device_map="auto" if device == "cuda" else None,
    trust_remote_code=True,
)

print(f"  ✅ Model loaded: {model_name}")
print()

# Add LoRA
print("Adding LoRA adapters...")
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
print()

# Reward model
reward_model = RewardModel()

# Optimizer
optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)

print("GRPO Training Configuration:")
print(f"  ✅ Epochs: {args.epochs}")
print(f"  ✅ Batch size: {args.batch_size}")
print(f"  ✅ Samples per prompt: {args.n_samples_per_prompt}")
print(f"  ✅ Learning rate: {args.learning_rate}")
print(f"  ✅ Max length: {args.max_length}")
print(f"  ✅ Seed: {args.seed}")
if args.max_samples and args.max_samples > 0:
    print(f"  ✅ Max samples: {args.max_samples}")
print()


def compute_text_reward(response_text: str, agent_id: str, prompt: str) -> float:
    """
    Compute reward based on response quality
    This is the core of GRPO - reward shaping
    """
    reward = 0.5  # Base reward
    
    response_lower = response_text.lower()
    
    # Positive signals
    if "welfare" in response_lower or "invest" in response_lower:
        reward += 0.15
    
    if "trust" in response_lower and "increase" in response_lower:
        reward += 0.1
    
    if "reduce" in response_lower and ("unrest" in response_lower or "crime" in response_lower):
        reward += 0.15
    
    if "emergency" in response_lower and "budget" in prompt.lower():
        reward += 0.1
    
    if "community" in response_lower and "policing" in response_lower:
        reward += 0.2  # Good police strategy
    
    # Negative signals
    if "increase_tax" in response_lower or "raise tax" in response_lower:
        if "trust" in prompt.lower() and "low" in prompt.lower():
            reward -= 0.2  # Bad when trust is low
    
    if "riot_control" in response_lower or "deploy riot" in response_lower:
        reward -= 0.25  # Usually backfires
    
    if "force" in response_lower or "suppress" in response_lower:
        reward -= 0.15
    
    if "hold" in response_lower and ("crisis" in prompt.lower() or "critical" in prompt.lower()):
        reward -= 0.2  # Inaction during crisis
    
    # Context-aware rewards
    if agent_id == "health_minister":
        if "vaccination" in response_lower or "hospital" in response_lower:
            reward += 0.15
    
    if agent_id == "mayor":
        if "coordinate" in response_lower or "emergency" in response_lower:
            reward += 0.1
    
    if agent_id == "finance_officer":
        if "stimulus" in response_lower or "bonds" in response_lower:
            reward += 0.1
    
    # Clamp to [0, 1]
    return max(0.0, min(1.0, reward))


def grpo_step(prompts_batch, agent_ids_batch):
    """
    GRPO training step:
    1. Generate N samples per prompt
    2. Compute rewards for each
    3. Select best samples (group relative)
    4. Update policy to favor high-reward samples
    """
    model.eval()
    
    all_rewards = []
    all_log_probs = []
    all_responses = []
    
    with torch.no_grad():
        for prompt, agent_id in zip(prompts_batch, agent_ids_batch):
            # Generate multiple samples per prompt
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=args.max_length).to(device)
            
            prompt_rewards = []
            prompt_responses = []
            
            for _ in range(args.n_samples_per_prompt):
                # Generate response
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=100,
                    do_sample=True,
                    temperature=0.8,
                    top_p=0.9,
                    pad_token_id=tokenizer.pad_token_id,
                )
                
                response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Compute reward
                reward = compute_text_reward(response, agent_id, prompt)
                
                prompt_rewards.append(reward)
                prompt_responses.append(response)
            
            all_rewards.append(prompt_rewards)
            all_responses.append(prompt_responses)
    
    # Now train on high-reward samples
    model.train()
    
    total_loss = 0.0
    n_updates = 0
    
    for prompt, agent_id, rewards, responses in zip(prompts_batch, agent_ids_batch, all_rewards, all_responses):
        # Get best sample (GRPO: group relative)
        best_idx = np.argmax(rewards)
        best_reward = rewards[best_idx]
        best_response = responses[best_idx]
        
        # Only train if reward is good enough
        if best_reward < 0.4:
            continue
        
        # Tokenize best response
        full_text = prompt + " " + best_response
        inputs = tokenizer(full_text, return_tensors="pt", truncation=True, max_length=args.max_length).to(device)
        
        # Forward pass
        outputs = model(**inputs, labels=inputs["input_ids"])
        loss = outputs.loss
        
        # Weight loss by reward (higher reward = more weight)
        weighted_loss = loss * (1.0 - best_reward)  # Lower loss for high reward
        
        # Backward
        weighted_loss.backward()
        
        total_loss += weighted_loss.item()
        n_updates += 1
    
    # Update weights
    if n_updates > 0:
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        optimizer.zero_grad()
        
        return total_loss / n_updates
    else:
        return 0.0


# Training loop
print("Starting GRPO training...")
print("=" * 70)
print()

Path(args.output_dir).mkdir(parents=True, exist_ok=True)

for epoch in range(args.epochs):
    print(f"Epoch {epoch + 1}/{args.epochs}")
    
    # Shuffle samples
    np.random.shuffle(samples)
    
    epoch_loss = 0.0
    n_batches = 0
    
    # Process in batches
    for i in tqdm(range(0, len(samples), args.batch_size), desc=f"Epoch {epoch+1}"):
        batch = samples[i:i+args.batch_size]
        
        prompts = [s["prompt"] for s in batch]
        agent_ids = [s.get("agent_id", "mayor") for s in batch]
        
        # GRPO step
        loss = grpo_step(prompts, agent_ids)
        
        if loss > 0:
            epoch_loss += loss
            n_batches += 1
    
    avg_loss = epoch_loss / n_batches if n_batches > 0 else 0.0
    print(f"  Average loss: {avg_loss:.4f}")
    print()

print("=" * 70)
print("🎉 GRPO Training complete!")
print()

# Save model
print("Saving model...")
model.save_pretrained(args.output_dir)
tokenizer.save_pretrained(args.output_dir)
print(f"  ✅ Saved to: {args.output_dir}")
print()

print("=" * 70)
print("✅ SUCCESS! Your GRPO-trained model is ready!")
print()
print("Next steps:")
print("  1. Test: python training/test_grpo_model.py")
print("  2. Compare: python evaluate.py --mode compare")
print("  3. Demo: streamlit run demo/dashboard.py")
print("=" * 70)
