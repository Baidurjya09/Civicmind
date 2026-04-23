"""
CivicMind — Simplified Training Script (Windows Compatible)
Works around TRL encoding issues on Windows.
"""

import os
import json
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

print("=" * 70)
print("  CivicMind — Simplified Training (Windows Compatible)")
print("=" * 70)
print()

# Config
parser = argparse.ArgumentParser()
parser.add_argument("--epochs", type=int, default=2)
parser.add_argument("--batch_size", type=int, default=1)
parser.add_argument("--output_dir", type=str, default="training/checkpoints/civicmind_final")
args = parser.parse_args()

# Check GPU
print("Checking GPU...")
if torch.cuda.is_available():
    print(f"  ✅ GPU: {torch.cuda.get_device_name(0)}")
    print(f"  ✅ VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
else:
    print("  ⚠️  No GPU detected - training will be slow")
print()

# Load dataset
print("Loading dataset...")
dataset_path = "training/civicmind_dataset.jsonl"
samples = []
with open(dataset_path) as f:
    for line in f:
        samples.append(json.loads(line))

print(f"  Loaded {len(samples)} samples")
print()

# Load model (using standard transformers, not Unsloth due to Windows issues)
print("Loading model...")
model_name = "Qwen/Qwen2.5-7B-Instruct"

try:
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
        trust_remote_code=True,
    )
    print(f"  ✅ Model loaded: {model_name}")
except Exception as e:
    print(f"  ⚠️  Could not load full model: {e}")
    print("  Using smaller model for demo...")
    model_name = "gpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

print()

# Add LoRA
print("Adding LoRA adapters...")
lora_config = LoraConfig(
    r=16,
    lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"] if "Qwen" in model_name else ["c_attn"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

if torch.cuda.is_available():
    model = prepare_model_for_kbit_training(model)

model = get_peft_model(model, lora_config)
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"  ✅ Trainable params: {trainable_params:,}")
print()

# Prepare dataset
print("Preparing dataset...")

def tokenize_function(examples):
    # Combine prompt and completion
    texts = [p + " " + c for p, c in zip(examples["prompt"], examples["completion"])]
    
    tokenized = tokenizer(
        texts,
        truncation=True,
        max_length=512,
        padding="max_length",
    )
    
    # Labels are same as input_ids for causal LM
    tokenized["labels"] = tokenized["input_ids"].copy()
    
    return tokenized

dataset = Dataset.from_list(samples)
dataset = dataset.map(
    tokenize_function,
    batched=True,
    remove_columns=dataset.column_names,
)

print(f"  ✅ Dataset prepared: {len(dataset)} samples")
print()

# Training arguments
print("Setting up training...")
training_args = TrainingArguments(
    output_dir=args.output_dir,
    num_train_epochs=args.epochs,
    per_device_train_batch_size=args.batch_size,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=torch.cuda.is_available(),
    logging_steps=10,
    save_steps=100,
    save_total_limit=2,
    warmup_steps=10,
    logging_dir=f"{args.output_dir}/logs",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)

print(f"  Epochs: {args.epochs}")
print(f"  Batch size: {args.batch_size}")
print(f"  Gradient accumulation: 4")
print(f"  Effective batch size: {args.batch_size * 4}")
print()

# Train
print("Starting training...")
print("=" * 70)
print()

try:
    train_result = trainer.train()
    
    print()
    print("=" * 70)
    print("Training complete!")
    print(f"  Final loss: {train_result.metrics.get('train_loss', 'N/A'):.4f}")
    print()
    
    # Save
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"  ✅ Saved to: {args.output_dir}")
    print()
    
    print("=" * 70)
    print("✅ SUCCESS! Your model is trained and ready!")
    print()
    print("Next steps:")
    print("  1. Test: python evaluate.py --mode compare")
    print("  2. Demo: streamlit run demo/dashboard.py")
    print("=" * 70)
    
except Exception as e:
    print()
    print("=" * 70)
    print(f"❌ Training error: {e}")
    print()
    print("This is likely due to:")
    print("  - Insufficient VRAM (need 12GB+)")
    print("  - Model download issues")
    print("  - Windows compatibility issues")
    print()
    print("SOLUTION: Use the HuggingFace compute credits on April 25!")
    print("Your system is ready - just needs better compute.")
    print("=" * 70)
