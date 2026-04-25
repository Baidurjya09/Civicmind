# Requirements Document

## Introduction

This document specifies requirements for a Google Colab notebook that trains the CivicMind multi-agent reinforcement learning governance system. The notebook enables users to train both Q-learning (tabular RL) and GRPO (LLM-based RL) models, generate evaluation results, and export all artifacts needed for hackathon submission.

CivicMind is a 6-agent governance system where AI agents learn optimal civic policy decisions through reinforcement learning. The system has proven results: +20.4% reward improvement and +104% trust improvement using Q-learning training.

## Glossary

- **Colab_Notebook**: The Google Colab Jupyter notebook that orchestrates the training pipeline
- **Training_Pipeline**: The complete workflow from environment setup through model export
- **Q_Learning_Trainer**: Tabular reinforcement learning trainer (3 seconds, CPU-based)
- **GRPO_Trainer**: Group Relative Policy Optimization trainer for LLM-based agents (30-45 min, GPU-based)
- **Evaluation_Engine**: System that compares trained vs untrained policies
- **Evidence_Generator**: Component that produces all required result files and visualizations
- **Artifact_Exporter**: System that packages all outputs for download
- **Environment_Setup**: Installation of dependencies and GPU configuration
- **Dataset_Generator**: Component that creates synthetic training data
- **Checkpoint_Manager**: System that saves and loads trained model states

## Requirements

### Requirement 1: Environment Setup and Dependency Installation

**User Story:** As a user, I want the notebook to automatically install all dependencies and configure GPU access, so that I can start training without manual setup.

#### Acceptance Criteria

1. WHEN the notebook is opened, THE Environment_Setup SHALL detect the runtime environment (Colab, Kaggle, or local)
2. THE Environment_Setup SHALL install all required Python packages from requirements.txt within 2 minutes
3. WHEN a GPU is available, THE Environment_Setup SHALL configure CUDA and display GPU information (name, VRAM)
4. WHEN no GPU is available, THE Environment_Setup SHALL display a warning and configure CPU-only mode
5. THE Environment_Setup SHALL verify all critical imports (torch, transformers, datasets, peft) succeed
6. THE Environment_Setup SHALL clone or mount the CivicMind repository if not already present
7. THE Environment_Setup SHALL display a success message with environment summary (Python version, PyTorch version, device type)

### Requirement 2: Training Data Generation

**User Story:** As a user, I want to generate synthetic training data for the RL agents, so that I have examples of good and bad policy decisions.

#### Acceptance Criteria

1. THE Dataset_Generator SHALL create a configurable number of training samples (default: 500)
2. THE Dataset_Generator SHALL generate samples with a configurable good-to-bad action ratio (default: 70% good, 30% bad)
3. WHEN generating samples, THE Dataset_Generator SHALL include all 6 agent types (mayor, health_minister, finance_officer, police_chief, infrastructure_head, media_spokesperson)
4. THE Dataset_Generator SHALL save the dataset in JSONL format to training/civicmind_dataset.jsonl
5. THE Dataset_Generator SHALL display generation progress every 100 samples
6. THE Dataset_Generator SHALL complete generation within 30 seconds for 500 samples
7. WHEN generation completes, THE Dataset_Generator SHALL display dataset statistics (total samples, good/bad ratio, samples per agent)

### Requirement 3: Q-Learning Training Execution

**User Story:** As a user, I want to train the Q-learning model quickly, so that I can validate the training pipeline works.

#### Acceptance Criteria

1. THE Q_Learning_Trainer SHALL support configurable training parameters (episodes, epsilon_start, epsilon_end, learning_rate)
2. THE Q_Learning_Trainer SHALL train for a default of 2000 episodes
3. THE Q_Learning_Trainer SHALL display training progress every 200 episodes showing (episode number, epsilon value, states learned, average reward)
4. THE Q_Learning_Trainer SHALL complete training within 10 seconds on CPU
5. THE Q_Learning_Trainer SHALL save the trained Q-table to training/checkpoints/rl_policy.pkl
6. WHEN training completes, THE Q_Learning_Trainer SHALL display final statistics (total states learned, final epsilon, training time)
7. THE Q_Learning_Trainer SHALL generate a training curve plot showing reward progression over episodes

### Requirement 4: GRPO Training Execution

**User Story:** As a user, I want to train the GRPO LLM-based model with GPU acceleration, so that I can compare LLM-based RL to tabular RL.

#### Acceptance Criteria

1. THE GRPO_Trainer SHALL load the Qwen2.5-0.5B-Instruct model with LoRA adapters
2. THE GRPO_Trainer SHALL support configurable training parameters (epochs, batch_size, learning_rate, n_samples_per_prompt)
3. THE GRPO_Trainer SHALL train for a default of 3 epochs
4. THE GRPO_Trainer SHALL display training progress showing (epoch, batch, loss, estimated time remaining)
5. WHEN GPU is available, THE GRPO_Trainer SHALL use mixed precision (fp16) training
6. THE GRPO_Trainer SHALL complete training within 45 minutes on T4 GPU (Colab free tier)
7. THE GRPO_Trainer SHALL save the trained model and tokenizer to training/checkpoints/civicmind_grpo
8. THE GRPO_Trainer SHALL generate a loss curve plot showing training loss over batches
9. WHEN training completes, THE GRPO_Trainer SHALL display final statistics (final loss, training time, trainable parameters)

### Requirement 5: Model Evaluation and Comparison

**User Story:** As a user, I want to evaluate trained models against baselines, so that I can prove training effectiveness.

#### Acceptance Criteria

1. THE Evaluation_Engine SHALL run evaluations for random baseline, heuristic baseline, and trained policy
2. THE Evaluation_Engine SHALL run a configurable number of episodes per policy (default: 5)
3. THE Evaluation_Engine SHALL use identical random seeds for fair comparison across policies
4. THE Evaluation_Engine SHALL measure and report (mean reward, final reward, survival rate, trust score, rebel spawn rate)
5. THE Evaluation_Engine SHALL calculate improvement percentages (trained vs random, trained vs heuristic)
6. THE Evaluation_Engine SHALL save evaluation results to evaluation/artifacts/training_results.json
7. THE Evaluation_Engine SHALL display a comparison table showing all policies side-by-side
8. THE Evaluation_Engine SHALL generate before/after comparison plots (reward curves, trust progression)

### Requirement 6: Anti-Reward-Hacking Validation

**User Story:** As a user, I want to validate that the reward function is robust against exploitation, so that I can prove the model learned genuine policies.

#### Acceptance Criteria

1. THE Evidence_Generator SHALL run 5 anti-hacking tests (inaction exploit, budget abuse, instability, crisis gaming, reward consistency)
2. THE Evidence_Generator SHALL compare exploit attempts against proper behavior for each test
3. THE Evidence_Generator SHALL calculate penalty deltas showing exploit attempts receive lower rewards
4. THE Evidence_Generator SHALL save validation results to evidence/eval/anti_hacking_validation.json
5. THE Evidence_Generator SHALL display test results with pass/fail status for each test
6. THE Evidence_Generator SHALL report overall pass rate (target: 5/5 tests passing)
7. WHEN any test fails, THE Evidence_Generator SHALL display detailed failure information

### Requirement 7: Evidence Package Generation

**User Story:** As a user, I want to generate all required evidence files and visualizations, so that I have complete documentation of training results.

#### Acceptance Criteria

1. THE Evidence_Generator SHALL create all required directories (evidence/eval, evidence/plots, evaluation/artifacts)
2. THE Evidence_Generator SHALL generate training curve plots saved to evidence/plots/training_results.png
3. THE Evidence_Generator SHALL generate before/after comparison plots saved to evidence/plots/before_after_comparison.png
4. THE Evidence_Generator SHALL save training results JSON to evidence/eval/training_results.json
5. THE Evidence_Generator SHALL save per-agent validation JSON to evidence/eval/per_agent_validation.json
6. THE Evidence_Generator SHALL generate a summary report showing (training time, improvement metrics, validation results)
7. THE Evidence_Generator SHALL display file paths for all generated evidence files

### Requirement 8: Artifact Export and Download

**User Story:** As a user, I want to download all training artifacts as a single archive, so that I can use results locally or for submission.

#### Acceptance Criteria

1. THE Artifact_Exporter SHALL create a zip archive containing all training outputs
2. THE Artifact_Exporter SHALL include in the archive (trained model checkpoints, evaluation results JSON, all plots, training logs)
3. THE Artifact_Exporter SHALL name the archive with timestamp (civicmind_results_YYYYMMDD_HHMMSS.zip)
4. THE Artifact_Exporter SHALL display archive size and contents summary
5. WHEN running in Google Colab, THE Artifact_Exporter SHALL trigger automatic download to user's local machine
6. WHEN running in Kaggle, THE Artifact_Exporter SHALL save the archive to /kaggle/working/
7. THE Artifact_Exporter SHALL complete archiving within 10 seconds

### Requirement 9: Interactive Training Mode Selection

**User Story:** As a user, I want to choose which training mode to run, so that I can quickly test Q-learning or run full GRPO training.

#### Acceptance Criteria

1. THE Colab_Notebook SHALL provide a dropdown widget for training mode selection (Quick Q-Learning, Full GRPO, Both, Evaluation Only)
2. WHEN "Quick Q-Learning" is selected, THE Training_Pipeline SHALL run Q-learning training and evaluation only
3. WHEN "Full GRPO" is selected, THE Training_Pipeline SHALL run GRPO training and evaluation only
4. WHEN "Both" is selected, THE Training_Pipeline SHALL run Q-learning first, then GRPO, then compare both
5. WHEN "Evaluation Only" is selected, THE Training_Pipeline SHALL load existing checkpoints and run evaluation
6. THE Colab_Notebook SHALL display estimated runtime for each mode before execution
7. THE Colab_Notebook SHALL allow parameter customization (epochs, batch_size, n_episodes) via form widgets

### Requirement 10: Progress Monitoring and Logging

**User Story:** As a user, I want to see real-time progress updates during training, so that I know the notebook is working and can estimate completion time.

#### Acceptance Criteria

1. THE Training_Pipeline SHALL display a progress bar for long-running operations (training, evaluation, data generation)
2. THE Training_Pipeline SHALL update progress every 10 seconds showing (current step, elapsed time, estimated remaining time)
3. THE Training_Pipeline SHALL log key events to console (training start, epoch completion, checkpoint saved, evaluation complete)
4. THE Training_Pipeline SHALL display live training metrics (current loss, current reward, epsilon value)
5. WHEN training is interrupted, THE Training_Pipeline SHALL save a checkpoint and display recovery instructions
6. THE Training_Pipeline SHALL display memory usage warnings when VRAM exceeds 90% capacity
7. WHEN all steps complete, THE Training_Pipeline SHALL display a success summary with total runtime and key results

### Requirement 11: Error Handling and Recovery

**User Story:** As a user, I want clear error messages and recovery options when issues occur, so that I can troubleshoot problems quickly.

#### Acceptance Criteria

1. WHEN GPU memory is insufficient, THE Training_Pipeline SHALL display an error message suggesting batch size reduction
2. WHEN model download fails, THE Training_Pipeline SHALL retry up to 3 times with exponential backoff
3. WHEN a training step fails, THE Training_Pipeline SHALL save the last valid checkpoint and display the error
4. WHEN dependencies fail to install, THE Training_Pipeline SHALL display the specific package name and error message
5. THE Training_Pipeline SHALL validate all file paths exist before attempting to load checkpoints
6. WHEN evaluation fails, THE Training_Pipeline SHALL continue with remaining evaluation modes and report partial results
7. THE Training_Pipeline SHALL provide a "Reset Environment" button that clears all outputs and restarts from setup

### Requirement 12: Notebook Documentation and Instructions

**User Story:** As a user, I want clear instructions and documentation in the notebook, so that I understand what each section does.

#### Acceptance Criteria

1. THE Colab_Notebook SHALL include a markdown header explaining the notebook purpose and expected outputs
2. THE Colab_Notebook SHALL include a "Quick Start" section with 3-step instructions (Run Setup, Choose Mode, Download Results)
3. THE Colab_Notebook SHALL include markdown cells before each major section explaining what will happen
4. THE Colab_Notebook SHALL include estimated runtimes for each section (Setup: 2 min, Q-Learning: 10 sec, GRPO: 45 min)
5. THE Colab_Notebook SHALL include a "Troubleshooting" section with common issues and solutions
6. THE Colab_Notebook SHALL include links to the GitHub repository and documentation
7. THE Colab_Notebook SHALL include a final section summarizing all generated files and their purposes
