"""
Test GRPO-trained model
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

print("=" * 70)
print("  Testing GRPO-Trained Model")
print("=" * 70)
print()

# Load model
model_path = "training/checkpoints/civicmind_grpo"

print(f"Loading model from: {model_path}")

try:
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    
    base_model = AutoModelForCausalLM.from_pretrained(
        "Qwen/Qwen2.5-0.5B-Instruct",
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    
    model = PeftModel.from_pretrained(base_model, model_path)
    model.eval()
    
    print("  ✅ Model loaded successfully!")
    print()
    
except Exception as e:
    print(f"  ❌ Error loading model: {e}")
    print()
    print("Make sure you've trained the model first:")
    print("  python training/train_grpo.py --epochs 3")
    sys.exit(1)

# Test scenarios
test_scenarios = [
    {
        "name": "Low Trust Crisis",
        "prompt": """State: GDP=0.6, Trust=0.35, Unrest=0.65, Week=8
Agent: Mayor
Active crises: ['Economic Recession']
What should you do?
Answer:""",
    },
    {
        "name": "Health Emergency",
        "prompt": """State: Disease=0.12, Hospital Capacity=0.45, Survival=0.92, Week=5
Agent: Health Minister
Active crises: ['Disease Outbreak']
What should you do?
Answer:""",
    },
    {
        "name": "High Crime",
        "prompt": """State: Crime=0.45, Unrest=0.55, Trust=0.50, Week=10
Agent: Police Chief
Active crises: []
What should you do?
Answer:""",
    },
    {
        "name": "Budget Crisis",
        "prompt": """State: Budget=$150,000, GDP=0.65, Unemployment=0.15, Week=12
Agent: Finance Officer
Active crises: ['Budget Deficit']
What should you do?
Answer:""",
    },
]

print("Testing model on scenarios...")
print("=" * 70)
print()

for scenario in test_scenarios:
    print(f"📋 Scenario: {scenario['name']}")
    print(f"Prompt: {scenario['prompt'][:100]}...")
    print()
    
    inputs = tokenizer(scenario['prompt'], return_tensors="pt").to("cuda")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=80,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.pad_token_id,
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract just the answer part
    if "Answer:" in response:
        answer = response.split("Answer:")[-1].strip()
    else:
        answer = response[len(scenario['prompt']):].strip()
    
    print(f"🤖 Model Response:")
    print(f"   {answer[:200]}")
    print()
    print("-" * 70)
    print()

print("=" * 70)
print("✅ Testing complete!")
print()
print("The model should show:")
print("  - Context-aware decisions")
print("  - Appropriate actions for each scenario")
print("  - Reasoning based on state")
print()
print("If responses look good, your GRPO training worked!")
print("=" * 70)
