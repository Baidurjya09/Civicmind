"""
Generate comprehensive training report with curves and analysis
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Load training state
with open("../training/checkpoints/llm_agent/checkpoint-3912/trainer_state.json", "r") as f:
    trainer_state = json.load(f)

# Extract training metrics
log_history = trainer_state["log_history"]

steps = []
losses = []
learning_rates = []
grad_norms = []

for entry in log_history:
    if "loss" in entry:
        steps.append(entry["step"])
        losses.append(entry["loss"])
        learning_rates.append(entry["learning_rate"])
        grad_norms.append(entry["grad_norm"])

# Create output directory
Path("plots").mkdir(exist_ok=True)
Path("metrics").mkdir(exist_ok=True)

# 1. Loss Curve
plt.figure(figsize=(12, 6))
plt.plot(steps, losses, linewidth=2, color='#2E86AB')
plt.xlabel('Training Steps', fontsize=12)
plt.ylabel('Loss', fontsize=12)
plt.title('Training Loss Curve - LLM Agent', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('plots/loss_curve.png', dpi=300)
print("✓ Loss curve saved")

# 2. Learning Rate Schedule
plt.figure(figsize=(12, 6))
plt.plot(steps, learning_rates, linewidth=2, color='#A23B72')
plt.xlabel('Training Steps', fontsize=12)
plt.ylabel('Learning Rate', fontsize=12)
plt.title('Learning Rate Schedule', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('plots/learning_rate.png', dpi=300)
print("✓ Learning rate curve saved")

# 3. Gradient Norm
plt.figure(figsize=(12, 6))
plt.plot(steps, grad_norms, linewidth=1, alpha=0.7, color='#F18F01')
plt.xlabel('Training Steps', fontsize=12)
plt.ylabel('Gradient Norm', fontsize=12)
plt.title('Gradient Norm During Training', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('plots/gradient_norm.png', dpi=300)
print("✓ Gradient norm curve saved")

# 4. Combined Overview
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Loss
axes[0, 0].plot(steps, losses, linewidth=2, color='#2E86AB')
axes[0, 0].set_xlabel('Steps')
axes[0, 0].set_ylabel('Loss')
axes[0, 0].set_title('Training Loss')
axes[0, 0].grid(True, alpha=0.3)

# Learning Rate
axes[0, 1].plot(steps, learning_rates, linewidth=2, color='#A23B72')
axes[0, 1].set_xlabel('Steps')
axes[0, 1].set_ylabel('Learning Rate')
axes[0, 1].set_title('Learning Rate Schedule')
axes[0, 1].grid(True, alpha=0.3)

# Gradient Norm
axes[1, 0].plot(steps, grad_norms, linewidth=1, alpha=0.7, color='#F18F01')
axes[1, 0].set_xlabel('Steps')
axes[1, 0].set_ylabel('Gradient Norm')
axes[1, 0].set_title('Gradient Norm')
axes[1, 0].grid(True, alpha=0.3)

# Loss smoothed (moving average)
window = 50
smoothed_loss = np.convolve(losses, np.ones(window)/window, mode='valid')
smoothed_steps = steps[window-1:]
axes[1, 1].plot(smoothed_steps, smoothed_loss, linewidth=2, color='#06A77D')
axes[1, 1].set_xlabel('Steps')
axes[1, 1].set_ylabel('Smoothed Loss')
axes[1, 1].set_title(f'Smoothed Loss (window={window})')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('plots/training_overview.png', dpi=300)
print("✓ Training overview saved")

# 5. Save metrics summary
metrics_summary = {
    "total_steps": len(steps),
    "final_step": steps[-1],
    "initial_loss": losses[0],
    "final_loss": losses[-1],
    "min_loss": min(losses),
    "max_loss": max(losses),
    "loss_reduction_percent": ((losses[0] - losses[-1]) / losses[0] * 100),
    "initial_lr": learning_rates[0],
    "final_lr": learning_rates[-1],
    "mean_grad_norm": np.mean(grad_norms),
    "max_grad_norm": max(grad_norms),
    "epochs": trainer_state["epoch"],
    "training_time_estimate": "55 minutes 11 seconds"
}

with open("metrics/training_summary.json", "w") as f:
    json.dump(metrics_summary, f, indent=2)

print("\n" + "="*60)
print("  TRAINING METRICS SUMMARY")
print("="*60)
for key, value in metrics_summary.items():
    if isinstance(value, float):
        print(f"{key:30s}: {value:.4f}")
    else:
        print(f"{key:30s}: {value}")
print("="*60)

print("\n✅ All training reports generated successfully!")
print(f"   - Plots saved in: train_result/plots/")
print(f"   - Metrics saved in: train_result/metrics/")
