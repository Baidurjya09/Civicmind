#!/usr/bin/env python3
"""
Generate official evidence plots from model_vs_baseline results
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def load_results():
    """Load comparison results"""
    with open("evidence/eval/model_vs_baseline.json") as f:
        main_results = json.load(f)
    
    with open("evidence/eval/detailed_results.json") as f:
        detailed = json.load(f)
    
    return main_results, detailed


def plot_comparison(main_results):
    """Create comparison bar charts"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    baseline = main_results["baseline"]
    trained = main_results["trained"]
    
    # Plot 1: Success Rate
    axes[0, 0].bar(["Baseline", "Trained"], 
                   [baseline["success_rate"], trained["success_rate"]],
                   color=['coral', 'darkgreen'], alpha=0.7)
    axes[0, 0].set_ylabel('Success Rate', fontsize=11, fontweight='bold')
    axes[0, 0].set_title('Success Rate Comparison', fontsize=12, fontweight='bold')
    axes[0, 0].set_ylim(0, 1.1)
    axes[0, 0].grid(alpha=0.3, axis='y')
    
    # Add values on bars
    for i, v in enumerate([baseline["success_rate"], trained["success_rate"]]):
        axes[0, 0].text(i, v + 0.02, f'{v:.1%}', ha='center', fontweight='bold')
    
    # Plot 2: Average Reward
    axes[0, 1].bar(["Baseline", "Trained"],
                   [baseline["avg_reward"], trained["avg_reward"]],
                   color=['coral', 'darkgreen'], alpha=0.7)
    axes[0, 1].set_ylabel('Average Reward', fontsize=11, fontweight='bold')
    axes[0, 1].set_title('Reward Comparison', fontsize=12, fontweight='bold')
    axes[0, 1].grid(alpha=0.3, axis='y')
    
    # Add improvement annotation
    improvement = main_results["improvements"]["reward_improvement_pct"]
    axes[0, 1].annotate(
        f'+{improvement:.1f}%',
        xy=(1, trained["avg_reward"]),
        xytext=(0.5, trained["avg_reward"] + 0.05),
        fontsize=13,
        fontweight='bold',
        color='green',
        arrowprops=dict(arrowstyle='->', color='green', lw=2)
    )
    
    for i, v in enumerate([baseline["avg_reward"], trained["avg_reward"]]):
        axes[0, 1].text(i, v + 0.01, f'{v:.3f}', ha='center', fontweight='bold')
    
    # Plot 3: Final Trust
    axes[1, 0].bar(["Baseline", "Trained"],
                   [baseline["avg_trust"], trained["avg_trust"]],
                   color=['coral', 'darkgreen'], alpha=0.7)
    axes[1, 0].set_ylabel('Final Trust Score', fontsize=11, fontweight='bold')
    axes[1, 0].set_title('Trust Score Comparison', fontsize=12, fontweight='bold')
    axes[1, 0].grid(alpha=0.3, axis='y')
    axes[1, 0].set_ylim(0, 1.0)
    
    # Add improvement annotation
    trust_improvement = main_results["improvements"]["trust_improvement_pct"]
    axes[1, 0].annotate(
        f'+{trust_improvement:.1f}%',
        xy=(1, trained["avg_trust"]),
        xytext=(0.5, 0.65),
        fontsize=13,
        fontweight='bold',
        color='green',
        arrowprops=dict(arrowstyle='->', color='green', lw=2)
    )
    
    for i, v in enumerate([baseline["avg_trust"], trained["avg_trust"]]):
        axes[1, 0].text(i, v + 0.02, f'{v:.3f}', ha='center', fontweight='bold')
    
    # Plot 4: Final Survival
    axes[1, 1].bar(["Baseline", "Trained"],
                   [baseline["avg_survival"], trained["avg_survival"]],
                   color=['coral', 'darkgreen'], alpha=0.7)
    axes[1, 1].set_ylabel('Final Survival Rate', fontsize=11, fontweight='bold')
    axes[1, 1].set_title('Survival Rate Comparison', fontsize=12, fontweight='bold')
    axes[1, 1].grid(alpha=0.3, axis='y')
    axes[1, 1].set_ylim(0.9, 1.0)
    
    for i, v in enumerate([baseline["avg_survival"], trained["avg_survival"]]):
        axes[1, 1].text(i, v + 0.001, f'{v:.3f}', ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig("evidence/plots/model_vs_baseline_comparison.png", dpi=150, bbox_inches='tight')
    plt.close()


def plot_episode_progression(detailed):
    """Plot reward progression across episodes"""
    baseline_rewards = [ep["avg_reward"] for ep in detailed["baseline_episodes"]]
    trained_rewards = [ep["avg_reward"] for ep in detailed["trained_episodes"]]
    
    episodes = list(range(len(baseline_rewards)))
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(episodes, baseline_rewards, marker='o', linewidth=2, markersize=4, 
            color='coral', alpha=0.7, label='Baseline (rule-based)')
    ax.plot(episodes, trained_rewards, marker='o', linewidth=2, markersize=4,
            color='darkgreen', alpha=0.7, label='Trained (crisis-aware)')
    
    # Add average lines
    baseline_avg = np.mean(baseline_rewards)
    trained_avg = np.mean(trained_rewards)
    
    ax.axhline(y=baseline_avg, color='coral', linestyle='--', alpha=0.5, linewidth=2,
               label=f'Baseline avg: {baseline_avg:.3f}')
    ax.axhline(y=trained_avg, color='darkgreen', linestyle='--', alpha=0.5, linewidth=2,
               label=f'Trained avg: {trained_avg:.3f}')
    
    ax.set_xlabel('Episode (Same Seed & Scenario)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Reward per Step', fontsize=12, fontweight='bold')
    ax.set_title('Episode-by-Episode Comparison (Reproducible)', fontsize=13, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("evidence/plots/episode_progression.png", dpi=150, bbox_inches='tight')
    plt.close()


def main():
    print("=" * 80)
    print("GENERATING OFFICIAL EVIDENCE PLOTS")
    print("=" * 80)
    
    # Load results
    main_results, detailed = load_results()
    
    # Create plots directory
    Path("evidence/plots").mkdir(parents=True, exist_ok=True)
    
    # Generate plots
    print("\nGenerating comparison charts...")
    plot_comparison(main_results)
    
    print("Generating episode progression...")
    plot_episode_progression(detailed)
    
    print("\n✅ Saved: evidence/plots/model_vs_baseline_comparison.png")
    print("✅ Saved: evidence/plots/episode_progression.png")
    
    print("\n" + "=" * 80)
    print("🏆 PLOTS GENERATED")
    print("=" * 80)
    print("\nKey Metrics:")
    print(f"  • Reward improvement: +{main_results['improvements']['reward_improvement_pct']:.1f}%")
    print(f"  • Trust improvement: +{main_results['improvements']['trust_improvement_pct']:.1f}%")
    print(f"  • Episodes evaluated: {main_results['episodes']}")
    print("=" * 80)


if __name__ == "__main__":
    main()
