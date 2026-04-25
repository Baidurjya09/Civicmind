#!/usr/bin/env python3
"""
Script to add missing cells to the Colab training pipeline notebook.
Adds GRPO training, anti-hacking validation, and evidence generation cells.
"""

import json
from pathlib import Path

def main():
    # Read the existing notebook
    notebook_path = Path('notebooks/colab_training_pipeline.ipynb')
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Find the index of the final markdown cell (Pipeline Complete!)
    final_cell_idx = len(notebook['cells']) - 1
    
    # New cells to insert (before the final cell)
    new_cells = []
    
    # ========== GRPO TRAINING CELLS ==========
    
    # GRPO Training Markdown
    new_cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\\n",
            "\\n",
            "## 🤖 GRPO Training (Optional - GPU Required)\\n",
            "\\n",
            "This section implements LLM-based reinforcement learning using GRPO (Group Relative Policy Optimization).\\n",
            "\\n",
            "**⚠️ WARNING**: This cell requires a GPU and will take approximately 45 minutes to complete.\\n",
            "\\n",
            "**Skip this cell if**:\\n",
            "- You don't have GPU access\\n",
            "- You want to complete the pipeline quickly\\n",
            "- You only need Q-learning results\\n",
            "\\n",
            "**Expected Runtime**: ~45 minutes on T4 GPU, 10+ hours on CPU (NOT RECOMMENDED)"
        ]
    })
    
    # GRPO Training Code
    grpo_code = '''# Skip GRPO training if no GPU or if user wants quick pipeline
SKIP_GRPO = not HAS_GPU or TRAINING_MODE == "Quick Q-Learning"

if SKIP_GRPO:
    print("⏭️  Skipping GRPO training (no GPU or Quick Q-Learning mode selected)")
    print("   The pipeline will continue with Q-learning results only.\\n")
else:
    print("\\n" + "="*70)
    print("🤖 GRPO Training")
    print("="*70 + "\\n")
    
    try:
        # Import GRPOTrainer
        from training.grpo_trainer import GRPOTrainer
        
        # Get training parameters
        n_epochs = grpo_epochs.value if 'grpo_epochs' in dir() else 3
        batch_sz = grpo_batch_size.value if 'grpo_batch_size' in dir() else 2
        
        print(f"📋 GRPO Configuration:")
        print(f"   Model: Qwen2.5-0.5B-Instruct")
        print(f"   Epochs: {n_epochs}")
        print(f"   Batch Size: {batch_sz}")
        print(f"   Samples per Prompt: 4")
        print(f"   Device: {DEVICE}")
        print(f"   Mixed Precision: {USE_FP16}")
        print()
        
        # Instantiate trainer
        print("🚀 Initializing GRPO Trainer...\\n")
        grpo_trainer = GRPOTrainer(
            epochs=n_epochs,
            batch_size=batch_sz,
            device=str(DEVICE),
            use_fp16=USE_FP16
        )
        
        # Load model
        grpo_trainer.load_model()
        
        # Train
        print("⏳ Starting GRPO training...")
        print("   This will take approximately 45 minutes on T4 GPU.\\n")
        
        grpo_stats = grpo_trainer.train()
        
        print("\\n✅ GRPO training complete!\\n")
        
        # Save checkpoint
        checkpoint_path = "training/checkpoints/civicmind_grpo"
        print(f"💾 Saving GRPO checkpoint to: {checkpoint_path}")
        grpo_trainer.save_checkpoint(checkpoint_path)
        
        # Generate loss curve
        plot_path = "evidence/plots/grpo_loss_curve.png"
        print(f"\\n📊 Generating loss curve: {plot_path}")
        grpo_trainer.plot_training_curve(save_path=plot_path, show=False)
        
        # Display summary
        print("\\n" + "="*70)
        print("✅ GRPO Training Complete!")
        print("="*70)
        print(f"   Checkpoint: {checkpoint_path}")
        print(f"   Training Time: {grpo_stats['total_time']:.2f}s ({grpo_stats['total_time']/60:.2f} min)")
        print(f"   Final Loss: {grpo_stats['losses'][-1]:.4f}")
        print(f"   Final Reward: {grpo_stats['rewards'][-1]:.4f}")
        print("="*70 + "\\n")
        
        # Store in global variable
        GRPO_TRAINER = grpo_trainer
        GRPO_STATS = grpo_stats
        
    except Exception as e:
        print(f"\\n❌ ERROR: GRPO training failed")
        print(f"   Error: {e}")
        print(f"\\n   This is optional - continuing with Q-learning results.\\n")
'''
    
    new_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": grpo_code.split('\\n')
    })
    
    # ========== ANTI-HACKING VALIDATION CELLS ==========
    
    # Anti-Hacking Validation Markdown
    new_cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\\n",
            "\\n",
            "## 🛡️ Anti-Reward-Hacking Validation\\n",
            "\\n",
            "This section runs comprehensive tests to prove the reward function is robust against exploitation.\\n",
            "\\n",
            "**Tests**:\\n",
            "1. **Inaction Exploit** - Verify holding during crisis is penalized\\n",
            "2. **Budget Abuse** - Verify budget depletion triggers penalties\\n",
            "3. **Instability Gaming** - Monitor erratic policy changes\\n",
            "4. **Crisis Gaming** - Verify crisis severity affects penalties\\n",
            "5. **Reward Consistency** - Verify reward components are valid\\n",
            "\\n",
            "**Expected Runtime**: ~30 seconds"
        ]
    })
    
    # Anti-Hacking Validation Code
    validation_code = '''print("\\n" + "="*70)
print("🛡️ Anti-Reward-Hacking Validation")
print("="*70 + "\\n")

try:
    # Run validation script
    import subprocess
    import sys
    
    print("⏳ Running anti-hacking validation tests...\\n")
    
    result = subprocess.run(
        [sys.executable, "evaluation/anti_hacking_validation.py"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # Display output
    print(result.stdout)
    
    if result.returncode == 0:
        print("\\n✅ Anti-hacking validation complete!")
        
        # Load results
        import json
        with open("evidence/eval/anti_hacking_validation.json", 'r') as f:
            validation_results = json.load(f)
        
        print(f"\\n📊 Results: {validation_results['passed_tests']}/{validation_results['total_tests']} tests passed")
        
        # Store in global variable
        VALIDATION_RESULTS = validation_results
    else:
        print(f"\\n⚠️  WARNING: Validation script returned non-zero exit code: {result.returncode}")
        print(f"   stderr: {result.stderr[:500]}")
        VALIDATION_RESULTS = None

except subprocess.TimeoutExpired:
    print("\\n⚠️  WARNING: Validation timed out after 60 seconds")
    VALIDATION_RESULTS = None
    
except Exception as e:
    print(f"\\n⚠️  WARNING: Validation failed: {e}")
    print("   Continuing without validation results.\\n")
    VALIDATION_RESULTS = None
'''
    
    new_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": validation_code.split('\\n')
    })
    
    # ========== EVIDENCE GENERATION CELLS ==========
    
    # Evidence Generation Markdown
    new_cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\\n",
            "\\n",
            "## 📊 Evidence Package Generation\\n",
            "\\n",
            "This section generates comprehensive evidence including:\\n",
            "- Training curve plots\\n",
            "- Before/after comparison plots\\n",
            "- Loss curves (if GRPO trained)\\n",
            "- Summary report (markdown)\\n",
            "\\n",
            "**Expected Runtime**: ~10 seconds"
        ]
    })
    
    # Evidence Generation Code
    evidence_code = '''print("\\n" + "="*70)
print("📊 Evidence Package Generation")
print("="*70 + "\\n")

try:
    from training.evidence_generator import EvidenceGenerator
    
    # Instantiate generator
    generator = EvidenceGenerator()
    
    # Prepare training stats
    training_stats = {}
    if 'Q_LEARNING_STATS' in dir():
        training_stats.update(Q_LEARNING_STATS)
    if 'GRPO_STATS' in dir():
        training_stats.update(GRPO_STATS)
    
    # Prepare evaluation results
    eval_results = EVALUATION_RESULTS if 'EVALUATION_RESULTS' in dir() else {}
    
    # Prepare validation results
    val_results = VALIDATION_RESULTS if 'VALIDATION_RESULTS' in dir() else None
    
    # Generate all evidence
    artifacts = generator.generate_all(
        training_stats=training_stats,
        evaluation_results=eval_results,
        validation_results=val_results
    )
    
    print("✅ Evidence package generation complete!")
    print(f"   Generated {len(artifacts)} artifacts\\n")
    
    # Store artifacts in global variable
    EVIDENCE_ARTIFACTS = artifacts
    
except Exception as e:
    print(f"\\n❌ ERROR: Evidence generation failed")
    print(f"   Error: {e}")
    print(f"\\n   Continuing without evidence package.\\n")
    EVIDENCE_ARTIFACTS = {}
'''
    
    new_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": evidence_code.split('\\n')
    })
    
    # Insert new cells before the final cell
    notebook['cells'] = notebook['cells'][:final_cell_idx] + new_cells + [notebook['cells'][final_cell_idx]]
    
    # Write updated notebook
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    
    print(f"✅ Successfully added {len(new_cells)} new cells to the notebook")
    print(f"   Total cells: {len(notebook['cells'])}")
    print(f"   Notebook saved: {notebook_path}")

if __name__ == "__main__":
    main()
