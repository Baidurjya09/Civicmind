"""
CivicMind — Fast GRPO Training (Optimized for Demo)
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
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
)
from peft import LoraConfig, get_peft_model, TaskType
from tqdm import tqdm
import numpy as np
import time

print("=" * 70)
print("  CivicMind — Fast GRPO Training")
print("=" * 70)
print()

# Config
parser = argparse.ArgumentParser()
parser.add_argument("--epochs", type=int, default=2)
parser.add_argument("--batch_size", type=int, default=4)
parser.add_argument("--n_samples_per_prompt", type=int, default=2, help="GRPO: samples per prompt (reduced for speed)")
parser.add_argument("--output_dir", type=str, default="training/checkpoints/civicmind_grpo")
parser.add_argument("--learning_rate", type=float, default=2e-5)
parser.add_argument("--max_length", type=int, default=256)
parser.add_argument("--max_samples", type=int, default=100, help="Use first N samples for quick proof runs")
parser.add_argument("--seed", type=int, default=42)
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
dataset_path = "training/llm_training_data.jsonl"
samples = []
with open(dataset_path) as f:
    for line in f:
        data = json.loads(line)
        samples.append(data)

print(f"  ✅ Loaded {len(samples)} samples")
samples = samples[:args.max_samples]
print(f"  ✅ Using subset: {len(samples)} samples for fast training")
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
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
all_params = sum(p.numel() for p in model.parameters())
print(f"  ✅ Trainable params: {trainable_params:,} / {all_params:,} ({100 * trainable_params / all_params:.2f}%)")
print()

# Optimizer
optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)

print("GRPO Training Configuration:")
print(f"  ✅ Epochs: {args.epochs}")
print(f"  ✅ Batch size: {args.batch_size}")
print(f"  ✅ Samples per prompt: {args.n_samples_per_prompt}")
print(f"  ✅ Learning rate: {args.learning_rate}")
print(f"  ✅ Max length: {args.max_length}")
print(f"  ✅ Training samples: {len(samples)}")
print()


def compute_reward(response_text: str, agent_id: str, prompt: str) -> float:
    """Compute reward based on response quality"""
    reward = 0.5
    response_lower = response_text.lower()
    
    # Positive signals
    if "welfare" in response_lower or "invest" in response_lower:
        reward += 0.15
    if "trust" in response_lower:
        reward += 0.1
    if "emergency" in response_lower and "crisis" in prompt.lower():
        reward += 0.15
    if "community" in response_lower:
        reward += 0.1
    
    # Negative signals
    if "hold" in response_lower and "crisis" in prompt.lower():
        reward -= 0.2
    if "riot_control" in response_lower:
        reward -= 0.2
    
    return max(0.0, min(1.0, reward))


# Training metrics
training_stats = {
    "losses": [],
    "rewards": [],
    "steps": [],
    "epoch_times": []
}

start_time = time.time()

print("Starting GRPO training...")
print("=" * 70)
print()

Path(args.output_dir).mkdir(parents=True, exist_ok=True)

global_step = 0

for epoch in range(args.epochs):
    epoch_start = time.time()
    print(f"Epoch {epoch + 1}/{args.epochs}")
    
    np.random.shuffle(samples)
    
    epoch_loss = 0.0
    epoch_reward = 0.0
    n_batches = 0
    
    for i in tqdm(range(0, len(samples), args.batch_size), desc=f"Epoch {epoch+1}"):
        batch = samples[i:i+args.batch_size]
        
        # Extract prompts and agent IDs
        prompts = []
        agent_ids = []
        for s in batch:
            if "prompt" in s:
                prompts.append(s["prompt"])
                agent_ids.append(s.get("agent_id", "mayor"))
            elif "text" in s:
                # Handle different format
                text = s["text"]
                if "Action:" in text:
                    prompt = text.split("Action:")[0] + "Action:"
                    prompts.append(prompt)
                    agent_ids.append(s.get("agent_id", "mayor"))
        
        if not prompts:
            continue
        
        # GRPO Step: Generate multiple samples and train on best
        model.eval()
        batch_rewards = []
        best_responses = []
        
        with torch.no_grad():
            for prompt, agent_id in zip(prompts, agent_ids):
                inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=args.max_length).to(device)
                
                sample_rewards = []
                sample_responses = []
                
                # Generate N samples
                for _ in range(args.n_samples_per_prompt):
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=50,
                        do_sample=True,
                        temperature=0.8,
                        top_p=0.9,
                        pad_token_id=tokenizer.pad_token_id,
                    )
                    
                    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    reward = compute_reward(response, agent_id, prompt)
                    
                    sample_rewards.append(reward)
                    sample_responses.append(response)
                
                # Select best sample
                best_idx = np.argmax(sample_rewards)
                batch_rewards.append(sample_rewards[best_idx])
                best_responses.append(sample_responses[best_idx])
        
        # Train on best samples
        model.train()
        batch_loss = 0.0
        
        for prompt, response, reward in zip(prompts, best_responses, batch_rewards):
            if reward < 0.4:  # Only train on good samples
                continue
            
            full_text = prompt + " " + response
            inputs = tokenizer(full_text, return_tensors="pt", truncation=True, max_length=args.max_length).to(device)
            
            outputs = model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss
            
            # Weight by reward
            weighted_loss = loss * (1.0 - reward)
            weighted_loss.backward()
            
            batch_loss += weighted_loss.item()
        
        # Update
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        optimizer.zero_grad()
        
        # Track metrics
        if batch_loss > 0:
            epoch_loss += batch_loss
            epoch_reward += np.mean(batch_rewards)
            n_batches += 1
            
            training_stats["losses"].append(batch_loss)
            training_stats["rewards"].append(np.mean(batch_rewards))
            training_stats["steps"].append(global_step)
            
            global_step += 1
    
    epoch_time = time.time() - epoch_start
    training_stats["epoch_times"].append(epoch_time)
    
    avg_loss = epoch_loss / n_batches if n_batches > 0 else 0.0
    avg_reward = epoch_reward / n_batches if n_batches > 0 else 0.0
    
    print(f"  Loss: {avg_loss:.4f} | Reward: {avg_reward:.4f} | Time: {epoch_time:.1f}s")
    print()

total_time = time.time() - start_time

print("=" * 70)
print("🎉 GRPO Training complete!")
print()
print(f"Training Summary:")
print(f"  Total time: {total_time/60:.1f} minutes")
print(f"  Final loss: {training_stats['losses'][-1]:.4f}")
print(f"  Final reward: {training_stats['rewards'][-1]:.4f}")
print(f"  Total steps: {global_step}")
print()

# Save model
print("Saving model...")
model.save_pretrained(args.output_dir)
tokenizer.save_pretrained(args.output_dir)
print(f"  ✅ Saved to: {args.output_dir}")
print()

# Save training stats
stats_path = Path(args.output_dir) / "training_stats.json"
with open(stats_path, "w") as f:
    json.dump(training_stats, f, indent=2)
print(f"  ✅ Training stats saved to: {stats_path}")
print()

print("=" * 70)
print("✅ SUCCESS! Your GRPO-trained model is ready!")
print()
print("Next steps:")
print("  1. Test: python training/test_grpo_model.py")
print("  2. View results in: training/checkpoints/civicmind_grpo/")
print("=" * 70)
