"""
Cleanup Script for Hackathon Submission
Removes unnecessary files to make repo clean and professional
"""

import os
from pathlib import Path

print("=" * 70)
print("CLEANING UP FOR HACKATHON SUBMISSION")
print("=" * 70)
print()

# Files to delete
files_to_delete = [
    # Documentation spam
    "ADVANCED_DATA_SUMMARY.md",
    "AGENT_DIVERSITY_ANALYSIS.md",
    "AUTO_CONTINUE_PLAN.md",
    "BLOG_POST.md",
    "CHEAT_SHEET.md",
    "CLEANUP_SUMMARY.md",
    "COLAB_PIPELINE_COMPLETE.md",
    "COLAB_QUICK_START.md",
    "COLAB_SETUP_GUIDE.md",
    "COMPLETE_WORK_SUMMARY.md",
    "CONTINUATION_STATUS.md",
    "CURRENT_STATUS.md",
    "DEPLOY_NOW.md",
    "ELITE_DATA_COMPLETE.md",
    "EVIDENCE_SUMMARY.md",
    "FINAL_ACTION_PLAN.md",
    "FINAL_AGGRESSIVE_AUDIT.md",
    "FINAL_DECISION_GUIDE.md",
    "FINAL_HACKATHON_AUDIT.md",
    "FINAL_MASTER_AUDIT.md",
    "FINAL_STATUS.md",
    "FINAL_TRAINING_STATUS.md",
    "FINAL_WINNING_PACKAGE.md",
    "FIX_ALL_TRAINING_ISSUES.md",
    "FIXING_PLAN.md",
    "GRPO_TRAINING_SUMMARY.md",
    "HACKATHON_AUDIT.md",
    "HACKATHON_CRITERIA_AUDIT.md",
    "HACKATHON_SUBMISSION_CHECKLIST.md",
    "HF_SPACE_DEPLOYMENT_GUIDE.md",
    "HF_SPACE_DOCKER_GUIDE.md",
    "JUDGE_DEFENSE_NOTES.md",
    "JUDGE_PROOF_PACKAGE.md",
    "LLM_AGENT_GUIDE.md",
    "LLM_IMPLEMENTATION_COMPLETE.md",
    "LLM_TRAINING_PIPELINE_STATUS.md",
    "LOSS_CURVE_ANALYSIS.md",
    "OPENENV_COMPLIANCE_CHECK.md",
    "OPENENV_STATUS.md",
    "PLOTS_UPDATED_SUMMARY.md",
    "PROJECT_READY.md",
    "README_FIRST.md",
    "READY_TO_DEPLOY.md",
    "REALISTIC_WINNING_ASSESSMENT.md",
    "RESULTS_VERIFIED.md",
    "REVISED_HACKATHON_AUDIT.md",
    "REVISED_WINNING_CHANCES.md",
    "REWARD_FUNCTION_ANALYSIS.md",
    "SHOULD_I_RETRAIN.md",
    "START_DEPLOYMENT.md",
    "START_HERE.md",
    "STRICT_AUDIT_REPORT.md",
    "SUBMISSION_READY.md",
    "TASK_7_1_COMPLETE.md",
    "TOP_5_PACKAGE.md",
    "TRAINING_CURVE_EXPLAINED.md",
    "TRAINING_DEFENSE.md",
    "TRAINING_ISSUES_FIXED_SUMMARY.md",
    "TRAINING_PIPELINE_VERIFIED.md",
    "TRAINING_STATUS_SUMMARY.md",
    "TRAINING_VERIFICATION.md",
    "WHEN_YOU_RETURN.md",
    "WINNING_DEFENSE_STRATEGY.md",
    "YOU_CAN_WIN.md",
    
    # Test/temp scripts
    "analyze_agent_diversity.py",
    "create_before_after_graph.py",
    "create_hf_space.py",
    "demo_environment_setup.py",
    "demo_q_learning_trainer.py",
    "evaluate_elite_model.py",
    "evaluate.py",
    "fix_all_training_issues.py",
    "fix_training_data.py",
    "live_demo.py",
    "make_data_elite.py",
    "quick_eval_and_plots.py",
    "quick_eval.py",
    "regenerate_all_plots.py",
    "regenerate_evidence_plots.py",
    "retrain_with_fixed_data.py",
    "run_demo_pipeline.py",
    "run_grpo_demo.py",
    "simple_comparison.py",
    "STRICT_AUDIT.py",
    "test_before_deploy.py",
    "test_environment_setup_integration.py",
    "test_hf_space_app.py",
    "test_plotting.py",
    "test_q_learning_trainer.py",
    "test_reward_hacking.py",
    "test_task_7_1_complete.py",
    "train_5_epochs.py",
    "train_aggressive.py",
    "train_and_evaluate.py",
    "train_elite_model.py",
    "train_fixed_with_results.py",
    "train_grpo_elite.py",
    "train_llm_pipeline.py",
    "upgrade_training_data_advanced.py",
    "validate_llm_system.py",
    "validate_submission.py",
    "verify_reproducibility.py",
    
    # Unused docker
    "docker-compose.yml",
    "Dockerfile",
]

deleted_count = 0
skipped_count = 0

print("Deleting unnecessary files...")
print()

for file in files_to_delete:
    if os.path.exists(file):
        try:
            os.remove(file)
            print(f"  ✅ Deleted: {file}")
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ Failed to delete {file}: {e}")
            skipped_count += 1
    else:
        skipped_count += 1

print()
print("=" * 70)
print(f"✅ Cleanup complete!")
print(f"  Deleted: {deleted_count} files")
print(f"  Skipped: {skipped_count} files (already gone or protected)")
print("=" * 70)
print()
print("Repository is now clean and ready for submission!")
