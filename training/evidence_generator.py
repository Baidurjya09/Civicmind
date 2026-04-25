"""
Evidence Package Generator for CivicMind Training Pipeline

This module generates comprehensive evidence packages including:
- Training curve plots
- Before/after comparison plots
- Summary reports
- Validation results
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Colab compatibility
import matplotlib.pyplot as plt
import numpy as np


class EvidenceGenerator:
    """
    Generates evidence packages for training results.
    
    Creates plots, reports, and validation artifacts for submission.
    """
    
    def __init__(self):
        """Initialize Evidence Generator."""
        self.evidence_dirs = {
            'eval': Path('evidence/eval'),
            'plots': Path('evidence/plots'),
            'artifacts': Path('evaluation/artifacts')
        }
    
    def create_directories(self) -> None:
        """Create all required evidence directories."""
        print("📁 Creating evidence directories...")
        
        for name, path in self.evidence_dirs.items():
            path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ {path}")
        
        print()
    
    def generate_training_curve(
        self,
        episode_rewards: List[float],
        save_path: Optional[str] = None,
        title: str = "Training Curve",
        window_size: int = 100
    ) -> str:
        """
        Generate training curve plot with moving average.
        
        Args:
            episode_rewards: List of rewards per episode
            save_path: Path to save plot (default: evidence/plots/training_results.png)
            title: Plot title
            window_size: Window size for moving average
            
        Returns:
            Path to saved plot
        """
        if save_path is None:
            save_path = self.evidence_dirs['plots'] / 'training_results.png'
        else:
            save_path = Path(save_path)
        
        print(f"📊 Generating training curve: {save_path}")
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        episodes = list(range(len(episode_rewards)))
        
        # Plot raw rewards
        ax.plot(episodes, episode_rewards, alpha=0.3, color='blue', label='Episode Reward')
        
        # Plot moving average
        if len(episode_rewards) >= window_size:
            moving_avg = np.convolve(
                episode_rewards,
                np.ones(window_size) / window_size,
                mode='valid'
            )
            moving_avg_episodes = list(range(window_size - 1, len(episode_rewards)))
            ax.plot(moving_avg_episodes, moving_avg, color='red', linewidth=2, label=f'{window_size}-Episode Moving Average')
        
        ax.set_xlabel('Episode', fontsize=12)
        ax.set_ylabel('Reward', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Saved: {save_path}")
        
        return str(save_path)
    
    def generate_comparison_plot(
        self,
        results: Dict[str, Dict[str, float]],
        save_path: Optional[str] = None,
        title: str = "Policy Comparison"
    ) -> str:
        """
        Generate grouped bar chart comparing policies.
        
        Args:
            results: Dictionary mapping policy names to metrics
            save_path: Path to save plot (default: evidence/plots/before_after_comparison.png)
            title: Plot title
            
        Returns:
            Path to saved plot
        """
        if save_path is None:
            save_path = self.evidence_dirs['plots'] / 'before_after_comparison.png'
        else:
            save_path = Path(save_path)
        
        print(f"📊 Generating comparison plot: {save_path}")
        
        # Extract metrics
        policy_names = list(results.keys())
        metrics = ['mean_reward_avg', 'final_reward_avg', 'trust_avg', 'survival_avg']
        metric_labels = ['Mean Reward', 'Final Reward', 'Trust Score', 'Survival Rate']
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        for idx, (metric, label) in enumerate(zip(metrics, metric_labels)):
            ax = axes[idx]
            
            # Get values for this metric
            values = [results[policy].get(metric, 0) for policy in policy_names]
            
            # Create bar chart
            x_pos = np.arange(len(policy_names))
            bars = ax.bar(x_pos, values, alpha=0.8)
            
            # Color bars (baseline vs trained)
            colors = ['#ff7f0e' if 'Baseline' in name else '#2ca02c' for name in policy_names]
            for bar, color in zip(bars, colors):
                bar.set_color(color)
            
            ax.set_xlabel('Policy', fontsize=11)
            ax.set_ylabel(label, fontsize=11)
            ax.set_title(label, fontsize=12, fontweight='bold')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(policy_names, rotation=15, ha='right', fontsize=9)
            ax.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for i, v in enumerate(values):
                ax.text(i, v, f'{v:.3f}', ha='center', va='bottom', fontsize=9)
        
        plt.suptitle(title, fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Saved: {save_path}")
        
        return str(save_path)
    
    def generate_loss_curve(
        self,
        losses: List[float],
        rewards: Optional[List[float]] = None,
        save_path: Optional[str] = None,
        title: str = "GRPO Training Curves"
    ) -> str:
        """
        Generate loss and reward curves for GRPO training.
        
        Args:
            losses: List of training losses
            rewards: List of training rewards (optional)
            save_path: Path to save plot (default: evidence/plots/loss_curve.png)
            title: Plot title
            
        Returns:
            Path to saved plot
        """
        if save_path is None:
            save_path = self.evidence_dirs['plots'] / 'loss_curve.png'
        else:
            save_path = Path(save_path)
        
        print(f"📊 Generating loss curve: {save_path}")
        
        # Create figure
        if rewards is not None:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        else:
            fig, ax1 = plt.subplots(1, 1, figsize=(10, 5))
        
        steps = list(range(len(losses)))
        
        # Plot loss
        ax1.plot(steps, losses, color='red', alpha=0.7, label='Loss')
        ax1.set_xlabel('Training Step', fontsize=12)
        ax1.set_ylabel('Loss', fontsize=12)
        ax1.set_title('Training Loss', fontsize=13, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot reward if provided
        if rewards is not None:
            ax2.plot(steps, rewards, color='green', alpha=0.7, label='Reward')
            ax2.set_xlabel('Training Step', fontsize=12)
            ax2.set_ylabel('Reward', fontsize=12)
            ax2.set_title('Training Reward', fontsize=13, fontweight='bold')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        plt.suptitle(title, fontsize=15, fontweight='bold')
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Saved: {save_path}")
        
        return str(save_path)
    
    def generate_summary_report(
        self,
        training_stats: Dict[str, Any],
        evaluation_results: Dict[str, Dict[str, float]],
        validation_results: Optional[Dict[str, Any]] = None,
        save_path: Optional[str] = None
    ) -> str:
        """
        Generate markdown summary report.
        
        Args:
            training_stats: Training statistics
            evaluation_results: Evaluation results
            validation_results: Validation results (optional)
            save_path: Path to save report (default: evidence/SUMMARY.md)
            
        Returns:
            Path to saved report
        """
        if save_path is None:
            save_path = Path('evidence/SUMMARY.md')
        else:
            save_path = Path(save_path)
        
        print(f"📝 Generating summary report: {save_path}")
        
        # Build report content
        lines = []
        lines.append("# CivicMind Training Summary Report")
        lines.append("")
        lines.append("## Training Statistics")
        lines.append("")
        
        if 'training_time' in training_stats:
            lines.append(f"- **Training Time**: {training_stats['training_time']:.2f}s ({training_stats['training_time']/60:.2f} min)")
        if 'episodes' in training_stats:
            lines.append(f"- **Episodes**: {training_stats['episodes']}")
        if 'states_learned' in training_stats:
            lines.append(f"- **States Learned**: {training_stats['states_learned']}")
        if 'final_epsilon' in training_stats:
            lines.append(f"- **Final Epsilon**: {training_stats['final_epsilon']:.3f}")
        
        lines.append("")
        lines.append("## Evaluation Results")
        lines.append("")
        lines.append("| Policy | Mean Reward | Final Reward | Trust Score | Survival Rate |")
        lines.append("|--------|-------------|--------------|-------------|---------------|")
        
        for policy_name, stats in evaluation_results.items():
            lines.append(
                f"| {policy_name} | "
                f"{stats.get('mean_reward_avg', 0):.4f} | "
                f"{stats.get('final_reward_avg', 0):.4f} | "
                f"{stats.get('trust_avg', 0):.4f} | "
                f"{stats.get('survival_avg', 0):.2%} |"
            )
        
        # Calculate improvements
        if 'Random Baseline' in evaluation_results and 'Trained Q-Learning' in evaluation_results:
            lines.append("")
            lines.append("## Improvement Analysis")
            lines.append("")
            
            random_reward = evaluation_results['Random Baseline']['mean_reward_avg']
            trained_reward = evaluation_results['Trained Q-Learning']['mean_reward_avg']
            improvement = ((trained_reward - random_reward) / max(random_reward, 0.001)) * 100
            
            lines.append(f"- **Reward Improvement**: {improvement:+.1f}% over random baseline")
            
            random_trust = evaluation_results['Random Baseline']['trust_avg']
            trained_trust = evaluation_results['Trained Q-Learning']['trust_avg']
            trust_improvement = ((trained_trust - random_trust) / max(random_trust, 0.001)) * 100
            
            lines.append(f"- **Trust Improvement**: {trust_improvement:+.1f}% over random baseline")
        
        # Add validation results if provided
        if validation_results:
            lines.append("")
            lines.append("## Validation Results")
            lines.append("")
            
            if 'passed_tests' in validation_results and 'total_tests' in validation_results:
                lines.append(f"- **Tests Passed**: {validation_results['passed_tests']}/{validation_results['total_tests']}")
            
            if 'tests' in validation_results:
                lines.append("")
                lines.append("### Anti-Hacking Tests")
                lines.append("")
                for test in validation_results['tests']:
                    status = "✅ PASS" if test.get('passed', False) else "❌ FAIL"
                    lines.append(f"- {status} - {test.get('test', 'Unknown')}")
        
        lines.append("")
        lines.append("## Generated Files")
        lines.append("")
        lines.append("- `evidence/plots/training_results.png` - Training curve")
        lines.append("- `evidence/plots/before_after_comparison.png` - Policy comparison")
        lines.append("- `evidence/eval/training_results.json` - Evaluation metrics")
        lines.append("- `evidence/eval/anti_hacking_validation.json` - Validation results")
        lines.append("- `training/checkpoints/rl_policy.pkl` - Trained model checkpoint")
        lines.append("")
        
        # Write report
        with open(save_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"   ✅ Saved: {save_path}")
        
        return str(save_path)
    
    def generate_all(
        self,
        training_stats: Dict[str, Any],
        evaluation_results: Dict[str, Dict[str, float]],
        validation_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Generate all evidence artifacts.
        
        Args:
            training_stats: Training statistics
            evaluation_results: Evaluation results
            validation_results: Validation results (optional)
            
        Returns:
            Dictionary mapping artifact names to file paths
        """
        print("=" * 70)
        print("📦 Generating Evidence Package")
        print("=" * 70)
        print()
        
        # Create directories
        self.create_directories()
        
        artifacts = {}
        
        # Generate training curve if episode rewards available
        if 'episode_rewards' in training_stats:
            artifacts['training_curve'] = self.generate_training_curve(
                training_stats['episode_rewards']
            )
        
        # Generate comparison plot
        artifacts['comparison_plot'] = self.generate_comparison_plot(
            evaluation_results
        )
        
        # Generate loss curve if GRPO stats available
        if 'losses' in training_stats:
            artifacts['loss_curve'] = self.generate_loss_curve(
                training_stats['losses'],
                training_stats.get('rewards')
            )
        
        # Generate summary report
        artifacts['summary_report'] = self.generate_summary_report(
            training_stats,
            evaluation_results,
            validation_results
        )
        
        print()
        print("=" * 70)
        print("✅ Evidence Package Complete!")
        print("=" * 70)
        print()
        print("Generated artifacts:")
        for name, path in artifacts.items():
            print(f"  - {name}: {path}")
        print()
        
        return artifacts
