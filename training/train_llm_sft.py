"""
Train LLM agent using Supervised Fine-Tuning (SFT)
Trains on high-reward (state, action) pairs
"""

import sys
import json
from pathlib import Path

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
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training


def load_training_data(data_file: str):
    """Load training data from JSONL file"""
    examples = []
    with open(data_file) as f:
        for line in f:
            examples.append(json.loads(line))
    return examples


def format_example(example):
    """Format example for training"""
    prompt = example["prompt"]
    completion = example["completion"]
    
    # Combine prompt and completion
    text = f"{prompt} {completion}"
    
    return {"text": text}


def main():
    print("\n" + "=" * 80)
    print("  LLM AGENT TRAINING (SFT)")
    print("=" * 80)
    print()
    
    # Configuration
    DATA_FILE = "training/llm_training_data.jsonl"
    MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"  # Small model for speed
    OUTPUT_DIR = "training/checkpoints/llm_agent"
    EPOCHS = 3
    BATCH_SIZE = 4
    
    print(f"Configuration:")
    print(f"  Data file: {DATA_FILE}")
    print(f"  Model: {MODEL_NAME}")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"  Epochs: {EPOCHS}")
    print(f"  Batch size: {BATCH_SIZE}")
    print()
    
    # Check GPU
    print("Checking GPU...")
    if torch.cuda.is_available():
        print(f"  ✅ GPU: {torch.cuda.get_device_name(0)}")
        print(f"  ✅ VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        device = "cuda"
    else:
        print("  ⚠️  No GPU detected - training will be slow")
        device = "cpu"
    print()
    
    # Load data
    print("Loading training data...")
    if not Path(DATA_FILE).exists():
        print(f"❌ Data file not found: {DATA_FILE}")
        print("Run: python training/collect_llm_data.py")
        return
    
    examples = load_training_data(DATA_FILE)
    print(f"  ✅ Loaded {len(examples)} examples")
    print()
    
    # Load model and tokenizer
    print(f"Loading model: {MODEL_NAME}...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None,
            trust_remote_code=True
        )
        print(f"  ✅ Model loaded")
    except Exception as e:
        print(f"  ❌ Failed to load model: {e}")
        print("  Falling back to GPT-2...")
        MODEL_NAME = "gpt2"
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        tokenizer.pad_token = tokenizer.eos_token
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        )
    print()
    
    # Add LoRA for efficient training
    print("Adding LoRA adapters...")
    lora_config = LoraConfig(
        r=16,
        lora_alpha=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"] if "Qwen" in MODEL_NAME else ["c_attn"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    if device == "cuda":
        model = prepare_model_for_kbit_training(model)
    
    model = get_peft_model(model, lora_config)
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  ✅ Trainable params: {trainable_params:,}")
    print()
    
    # Prepare dataset
    print("Preparing dataset...")
    
    # Format examples
    formatted_examples = [format_example(ex) for ex in examples]
    
    # Create dataset
    dataset = Dataset.from_list(formatted_examples)
    
    # Tokenize
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=512,
            padding="max_length"
        )
    
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names
    )
    
    # Add labels
    tokenized_dataset = tokenized_dataset.map(
        lambda x: {"labels": x["input_ids"].copy()}
    )
    
    print(f"  ✅ Dataset prepared: {len(tokenized_dataset)} examples")
    print()
    
    # Training arguments
    print("Setting up training...")
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=2,
        learning_rate=2e-4,
        fp16=device == "cuda",
        logging_steps=10,
        save_steps=100,
        save_total_limit=2,
        warmup_steps=10,
        logging_dir=f"{OUTPUT_DIR}/logs",
        report_to="none"
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator
    )
    
    print(f"  Epochs: {EPOCHS}")
    print(f"  Batch size: {BATCH_SIZE}")
    print(f"  Gradient accumulation: 2")
    print(f"  Effective batch size: {BATCH_SIZE * 2}")
    print()
    
    # Train
    print("Starting training...")
    print("=" * 80)
    print()
    
    try:
        train_result = trainer.train()
        
        print()
        print("=" * 80)
        print("✅ TRAINING COMPLETE")
        print("=" * 80)
        print(f"  Final loss: {train_result.metrics.get('train_loss', 'N/A'):.4f}")
        print()
        
        # Save
        print("Saving model...")
        trainer.save_model(OUTPUT_DIR)
        tokenizer.save_pretrained(OUTPUT_DIR)
        print(f"  ✅ Saved to: {OUTPUT_DIR}")
        print()
        
        print("=" * 80)
        print("✅ SUCCESS! LLM agent trained!")
        print("=" * 80)
        print()
        print("Next steps:")
        print("  1. Evaluate: python training/evaluate_llm_agent.py")
        print("  2. Compare to Q-learning: python evaluate.py --mode compare")
        print()
        
    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ Training error: {e}")
        print("=" * 80)
        print()
        print("This might be due to:")
        print("  - Insufficient VRAM (need 8GB+ for Qwen)")
        print("  - Model download issues")
        print("  - Data format issues")
        print()
        print("Try:")
        print("  - Reduce batch_size to 1")
        print("  - Use smaller model (GPT-2)")
        print("  - Check data file exists")
        print()


if __name__ == "__main__":
    main()
