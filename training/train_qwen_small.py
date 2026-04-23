"""
CivicMind — Qwen 2.5 0.5B Training Script
Uses smallest Qwen model (500M params) - perfect for 12GB GPU.
"""

import os
import json
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType

print("=" * 70)
print("  CivicMind — Qwen 2.5 0.5B Training")
print("=" * 70)
print()

# Config
parser = argparse.ArgumentParser()
parser.add_argument("--epochs", type=int, default=2)
parser.add_argument("--batch_size", type=int, default=4)
parser.add_argument("--output_dir", type=str, default="training/checkpoints/civicmind_qwen")
args = parser.parse_args()

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
print()

# Use Qwen 2.5 0.5B - smallest Qwen model
print("Loading Qwen 2.5 0.5B model...")
model_name = "Qwen/Qwen2.5-0.5B-Instruct"

try:
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    
    # Set padding token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model in fp16 to save memory
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    
    print(f"  ✅ Model loaded: {model_name}")
    print(f"  ✅ Model size: 500M parameters")
    print(f"  ✅ Perfect for 12GB VRAM!")
    
except Exception as e:
    print(f"  ❌ Error loading model: {e}")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Add LoRA for efficient training
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

# Prepare dataset
print("Preparing dataset...")

def tokenize_function(examples):
    # Combine prompt and completion
    texts = []
    for p, c in zip(examples["prompt"], examples["completion"]):
        # Truncate prompt if too long
        text = p[:1500] + " " + c
        texts.append(text)
    
    tokenized = tokenizer(
        texts,
        truncation=True,
        max_length=1024,
        padding="max_length",
        return_tensors=None,
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
    gradient_accumulation_steps=2,
    learning_rate=2e-4,
    fp16=device == "cuda",
    logging_steps=10,
    save_steps=50,
    save_total_limit=2,
    warmup_steps=20,
    logging_dir=f"{args.output_dir}/logs",
    report_to="none",
    remove_unused_columns=False,
    gradient_checkpointing=True,
)

# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    data_collator=data_collator,
)

print(f"  ✅ Model: Qwen 2.5 0.5B")
print(f"  ✅ Epochs: {args.epochs}")
print(f"  ✅ Batch size: {args.batch_size}")
print(f"  ✅ Gradient accumulation: 2")
print(f"  ✅ Effective batch size: {args.batch_size * 2}")
print(f"  ✅ Max sequence length: 1024")
print()

# Train
print("Starting training...")
print("=" * 70)
print()

try:
    train_result = trainer.train()
    
    print()
    print("=" * 70)
    print("🎉 Training complete!")
    print(f"  Final loss: {train_result.metrics.get('train_loss', 'N/A'):.4f}")
    print()
    
    # Save
    print("Saving model...")
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"  ✅ Saved to: {args.output_dir}")
    print()
    
    print("=" * 70)
    print("✅ SUCCESS! Your Qwen model is trained and ready!")
    print()
    print("Next steps:")
    print("  1. Test: python evaluate.py --mode compare")
    print("  2. Demo: streamlit run demo/dashboard.py")
    print("=" * 70)
    
except KeyboardInterrupt:
    print()
    print("=" * 70)
    print("⚠️  Training interrupted by user")
    print("=" * 70)
    
except Exception as e:
    print()
    print("=" * 70)
    print(f"❌ Training error: {e}")
    print()
    import traceback
    traceback.print_exc()
    print()
    print("Possible solutions:")
    print("  1. Reduce batch size: --batch_size 2")
    print("  2. Close other GPU applications")
    print("  3. Restart and try again")
    print("=" * 70)
