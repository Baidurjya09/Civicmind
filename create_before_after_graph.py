#!/usr/bin/env python3
"""
Create clear Before vs After comparison graph
This is THE WINNING GRAPH - shows learning proof
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Load results
with open("evidence/eval/training_results.json") as f:
    results = json.load(f)

before = results["before_after_evaluation"]["before"]
after = results["before_after_evaluation"]["after"]
improvements = results["before_after_evaluation"]["improvements"]

# Create figure
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# LEFT: Before vs After Bars
metrics = ['Reward', 'Trust', 'Survival']
before_vals = [before["avg_reward"], before["avg_trust"], before["avg_survival"]]
after_vals = [after["avg_reward"], after["avg_trust"], after["avg_survival"]]

x = np.arange(len(metrics))
width = 0.35

bars1 = axes[0].bar(x - width/2, before_vals, width, label='Before Training\n(Random Policy)', 
                    color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = axes[0].bar(x + width/2, after_vals, width, label='After Training\n(Learned Policy)', 
                    color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1.5)

# Add improvement percentages
imp_vals = [improvements["reward_pct"], improvements["trust_pct"], improvements["survival_pct"]]

for i, (bar, imp) in enumerate(zip(bars2, imp_vals)):
    height = bar.get_height()
    axes[0].text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{imp:+.1f}%',
                ha='center', va='bottom', fontsize=14, fontweight='bold', 
                color='darkgreen' if imp > 0 else 'darkred')

axes[0].set_ylabel('Value', fontsize=13, fontweight='bold')
axes[0].set_title('PROOF OF LEARNING: Before vs After Training', fontsize=14, fontweight='bold')
axes[0].set_xticks(x)
axes[0].set_xticklabels(metrics, fontsize=12, fontweight='bold')
axes[0].legend(fontsize=11, loc='upper left')
axes[0].grid(alpha=0.3, axis='y', linestyle='--')
axes[0].set_ylim(0, 1.0)

# Add annotation box
textstr = f'Training: 2000 episodes\nStates learned: {results["training"]["q_table_final_size"]}\nAlgorithm: Q-Learning'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
axes[0].text(0.02, 0.98, textstr, transform=axes[0].transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

# RIGHT: Reward Distribution
bp = axes[1].boxplot([before["rewards"], after["rewards"]], 
                     tick_labels=['Before\nTraining', 'After\nTraining'],
                     patch_artist=True, widths=0.6)

# Color the boxes
bp['boxes'][0].set_facecolor('#FF6B6B')
bp['boxes'][0].set_alpha(0.7)
bp['boxes'][0].set_edgecolor('black')
bp['boxes'][0].set_linewidth(1.5)

bp['boxes'][1].set_facecolor('#4ECDC4')
bp['boxes'][1].set_alpha(0.7)
bp['boxes'][1].set_edgecolor('black')
bp['boxes'][1].set_linewidth(1.5)

# Style whiskers and caps
for whisker in bp['whiskers']:
    whisker.set(linewidth=1.5, linestyle='-', color='black')
for cap in bp['caps']:
    cap.set(linewidth=1.5, color='black')
for median in bp['medians']:
    median.set(linewidth=2, color='darkred')

axes[1].set_ylabel('Reward per Step', fontsize=13, fontweight='bold')
axes[1].set_title('Reward Stability & Consistency', fontsize=14, fontweight='bold')
axes[1].grid(alpha=0.3, axis='y', linestyle='--')

# Add median values
median_before = np.median(before["rewards"])
median_after = np.median(after["rewards"])
axes[1].text(1, median_before, f'{median_before:.3f}', 
            ha='right', va='center', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
axes[1].text(2, median_after, f'{median_after:.3f}', 
            ha='left', va='center', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig("evidence/plots/before_after_comparison.png", dpi=150, bbox_inches='tight')
plt.close()

print("=" * 80)
print("✅ CREATED: evidence/plots/before_after_comparison.png")
print("=" * 80)
print("\n🎯 KEY RESULTS:")
print(f"  • Reward improvement: {improvements['reward_pct']:+.1f}%")
print(f"  • Trust improvement: {improvements['trust_pct']:+.1f}%")
print(f"  • Survival improvement: {improvements['survival_pct']:+.1f}%")
print(f"  • States learned: {results['training']['q_table_final_size']}")
print("\n💡 PRESENTATION TIP:")
print("  Show THIS graph FIRST - it's your proof of learning!")
print("=" * 80)
