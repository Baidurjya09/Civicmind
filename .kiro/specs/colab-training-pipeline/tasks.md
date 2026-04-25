# Implementation Plan: Google Colab Training Pipeline

## Overview

This implementation plan creates a Google Colab Jupyter notebook that orchestrates the complete CivicMind training pipeline. The notebook provides an interactive interface for training both Q-learning (tabular RL) and GRPO (LLM-based RL) models, evaluating performance, and exporting all artifacts for hackathon submission.

The implementation follows a modular cell-based structure where each major component is implemented in separate notebook cells for transparency, independent execution, and debugging. The notebook prioritizes zero-setup experience with automatic dependency installation, GPU configuration, and comprehensive error handling.

## Tasks

- [x] 1. Create notebook structure and header documentation
  - Create new Jupyter notebook file `notebooks/colab_training_pipeline.ipynb`
  - Add markdown header cell with title, description, and overview
  - Add "Quick Start" section with 3-step instructions (Run Setup, Choose Mode, Download Results)
  - Add estimated runtimes for each section (Setup: 2 min, Q-Learning: 10 sec, GRPO: 45 min)
  - Add links to GitHub repository and documentation
  - _Requirements: 12.1, 12.2, 12.3, 12.6_

- [x] 2. Implement environment detection and setup
  - [x] 2.1 Create EnvironmentSetup class with detection logic
    - Implement `detect_environment()` method using `sys.modules` checks for Colab/Kaggle
    - Implement `install_dependencies()` method with subprocess pip install
    - Implement `verify_imports()` method to check torch, transformers, datasets, peft
    - Implement `get_environment_summary()` method returning Python/PyTorch versions
    - Add retry logic with exponential backoff (1s, 2s, 4s) for failed installations
    - _Requirements: 1.1, 1.2, 1.5, 1.7, 11.2, 11.4_

  - [ ]* 2.2 Write unit tests for EnvironmentSetup
    - Test environment detection with mocked sys.modules
    - Test dependency verification with mocked imports
    - Test environment summary generation
    - _Requirements: 1.1, 1.5_

  - [x] 2.3 Create notebook cell for environment setup
    - Add code cell that instantiates EnvironmentSetup
    - Clone/mount CivicMind repository if not present
    - Install requirements.txt with progress bar display
    - Display environment summary (Python version, PyTorch version)
    - Add error handling with specific failure messages
    - _Requirements: 1.1, 1.2, 1.5, 1.6, 1.7, 11.4_

- [x] 3. Implement GPU configuration and verification
  - [x] 3.1 Create GPU configuration cell
    - Check `torch.cuda.is_available()` and set global device variable
    - Display GPU name and VRAM capacity using `torch.cuda.get_device_properties()`
    - Configure mixed precision (fp16) if GPU available
    - Display warning message if no GPU detected, continue in CPU mode
    - _Requirements: 1.3, 1.4, 1.7_

  - [ ]* 3.2 Write unit tests for GPU configuration
    - Test GPU detection with mocked torch.cuda
    - Test device variable setting
    - Test warning display for CPU-only mode
    - _Requirements: 1.3, 1.4_

- [x] 4. Checkpoint - Ensure environment setup completes successfully
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement training mode selection widget
  - [x] 5.1 Create interactive training mode dropdown
    - Create ipywidgets.Dropdown with 4 options (Quick Q-Learning, Full GRPO, Both Sequential, Evaluation Only)
    - Add option descriptions showing estimated runtime for each mode
    - Create parameter customization form widgets (epochs, batch_size, n_episodes)
    - Display estimated runtime for selected mode
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

  - [ ]* 5.2 Write unit tests for widget creation
    - Test dropdown options are correctly configured
    - Test parameter form accepts valid inputs
    - _Requirements: 9.1, 9.7_

- [x] 6. Implement dataset generation component
  - [x] 6.1 Create DatasetGenerator class
    - Implement `__init__()` with n_samples and good_ratio parameters
    - Implement `generate_sample()` method creating training samples for each agent type
    - Implement `generate_dataset()` method with tqdm progress bar (update every 100 samples)
    - Implement `save_dataset()` method saving to JSONL format
    - Implement `get_statistics()` method returning total samples, good/bad ratio, samples per agent
    - Include all 6 agent types (mayor, health_minister, finance_officer, police_chief, infrastructure_head, media_spokesperson)
    - Good actions: welfare investment, trust building, crisis response
    - Bad actions: tax increases during low trust, riot control, inaction during crisis
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [ ]* 6.2 Write unit tests for DatasetGenerator
    - Test sample generation for each agent type
    - Test good/bad action ratio (70% good, 30% bad)
    - Test JSONL serialization format
    - Test statistics calculation
    - _Requirements: 2.1, 2.2, 2.3, 2.7_

  - [x] 6.3 Create notebook cell for dataset generation
    - Instantiate DatasetGenerator with default parameters (500 samples, 0.7 good ratio)
    - Call generate_dataset() and display progress bar
    - Save dataset to training/civicmind_dataset.jsonl
    - Display dataset statistics (total samples, good/bad ratio, samples per agent)
    - Add error handling for file write permissions and disk space
    - _Requirements: 2.1, 2.4, 2.5, 2.7, 11.5_

- [x] 7. Implement Q-learning training component
  - [x] 7.1 Create QLearningTrainer class
    - Implement `__init__()` with episodes, epsilon_start, epsilon_end, learning_rate parameters
    - Implement `get_state_key()` method discretizing continuous values (trust, GDP, survival) into bins
    - Implement `select_action()` method with epsilon-greedy action selection
    - Implement `update_q_value()` method using Q-learning update rule: Q(s,a) = Q(s,a) + lr * (r + gamma * max_a' Q(s',a') - Q(s,a))
    - Implement `train()` method running training loop with linear epsilon decay
    - Implement `save_checkpoint()` method saving Q-table to pickle file
    - Add progress updates every 200 episodes showing epsilon, states learned, avg reward
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

  - [ ]* 7.2 Write unit tests for QLearningTrainer
    - Test state key generation (discretization)
    - Test epsilon-greedy action selection
    - Test Q-value update rule
    - Test epsilon decay (linear from 1.0 to 0.1)
    - Test checkpoint save/load
    - _Requirements: 3.1, 3.2, 3.5_

  - [x] 7.3 Create notebook cell for Q-learning training
    - Instantiate QLearningTrainer with default parameters (2000 episodes)
    - Call train() method and display progress updates
    - Save checkpoint to training/checkpoints/rl_policy.pkl
    - Display final statistics (total states learned, final epsilon, training time)
    - Generate training curve plot showing reward progression over episodes
    - Add error handling for checkpoint directory creation and pickle serialization
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 11.5_

- [x] 8. Checkpoint - Ensure Q-learning training completes successfully
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement GRPO training component
  - [x] 9.1 Create GRPOTrainer class
    - Implement `__init__()` with model_name, epochs, batch_size, n_samples_per_prompt, learning_rate parameters
    - Implement `load_model()` method loading Qwen2.5-0.5B-Instruct with LoRA adapters
    - Configure LoRA with r=16, alpha=32, dropout=0.05, target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
    - Implement `compute_text_reward()` method with reward shaping (positive for welfare/trust/crisis response, negative for force/inaction)
    - Implement `grpo_step()` method: generate N samples per prompt, compute rewards, select best, update policy
    - Implement `train()` method running training loop with mixed precision (fp16) if GPU available
    - Implement `save_checkpoint()` method saving model and tokenizer
    - Add progress bar with loss, ETA, memory usage display
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_

  - [ ]* 9.2 Write unit tests for GRPOTrainer
    - Test reward computation for various responses
    - Test LoRA configuration parameters
    - Test checkpoint save/load
    - _Requirements: 4.1, 4.2, 4.7_

  - [x] 9.3 Create notebook cell for GRPO training
    - Instantiate GRPOTrainer with default parameters (3 epochs, batch_size=2)
    - Load model and tokenizer with LoRA
    - Call train() method and display progress bar
    - Save checkpoint to training/checkpoints/civicmind_grpo
    - Display final statistics (final loss, training time, trainable parameters)
    - Generate loss curve plot showing training loss over batches
    - Add error handling for OOM errors with batch size reduction suggestion
    - Add checkpoint saving on KeyboardInterrupt
    - _Requirements: 4.1, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 11.1, 11.3, 11.6_

- [x] 10. Checkpoint - Ensure GRPO training completes successfully
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement model evaluation component
  - [x] 11.1 Create EvaluationEngine class
    - Implement `__init__()` with n_episodes, max_weeks, difficulty parameters
    - Implement `run_episode()` method executing single episode and returning metrics
    - Implement `evaluate_policy()` method running N episodes with identical seeds (42, 43, 44, 45, 46)
    - Implement `compare_policies()` method comparing random baseline, heuristic baseline, trained policy
    - Measure metrics: mean reward, final reward, survival rate, trust score, rebel spawn rate
    - Calculate improvement percentages: (trained - baseline) / baseline * 100
    - Implement `save_results()` method saving to JSON
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_

  - [ ]* 11.2 Write unit tests for EvaluationEngine
    - Test episode execution with mock environment
    - Test metric calculation
    - Test improvement percentage calculation
    - Test JSON serialization
    - _Requirements: 5.3, 5.4, 5.5, 5.6_

  - [x] 11.3 Create notebook cell for model evaluation
    - Instantiate EvaluationEngine with default parameters (5 episodes)
    - Run evaluations for random baseline, heuristic baseline, trained Q-learning policy
    - Display comparison table showing all policies side-by-side
    - Save results to evaluation/artifacts/training_results.json
    - Generate before/after comparison plots (reward curves, trust progression)
    - Add error handling to continue with partial results if one policy fails
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 11.6_

- [x] 12. Implement anti-reward-hacking validation
  - [x] 12.1 Create anti-hacking validation tests
    - Implement inaction exploit test (compare "hold" vs action during crisis)
    - Implement budget abuse test (compare wasteful vs prudent spending)
    - Implement instability gaming test (compare chaos vs stability actions)
    - Implement crisis gaming test (compare crisis exploitation vs proper response)
    - Implement reward consistency test (verify same state-action pairs yield consistent rewards)
    - Calculate penalty deltas for each test
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [ ]* 12.2 Write unit tests for anti-hacking validation
    - Test each anti-hacking test independently
    - Test penalty delta calculation
    - Test pass/fail status determination
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 12.3 Create notebook cell for anti-hacking validation
    - Run all 5 anti-hacking tests
    - Display test results with pass/fail status for each test
    - Save validation results to evidence/eval/anti_hacking_validation.json
    - Report overall pass rate (target: 5/5 tests passing)
    - Display detailed failure information if any test fails
    - Add error handling to report partial results if tests fail
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 11.6_

- [x] 13. Implement evidence package generation
  - [x] 13.1 Create EvidenceGenerator class
    - Implement `create_directories()` method creating evidence/eval, evidence/plots, evaluation/artifacts
    - Implement `generate_training_curve()` method creating line plot with reward over episodes
    - Implement `generate_comparison_plot()` method creating grouped bar chart comparing policies
    - Implement `generate_summary_report()` method creating markdown summary with training time, improvement metrics, validation results
    - Set matplotlib backend to 'Agg' for Colab compatibility
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

  - [ ]* 13.2 Write unit tests for EvidenceGenerator
    - Test directory creation
    - Test plot generation (verify file exists, not visual quality)
    - Test JSON serialization
    - Test summary report generation
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [x] 13.3 Create notebook cell for evidence generation
    - Instantiate EvidenceGenerator
    - Create all required directories
    - Generate training curve plot saved to evidence/plots/training_results.png
    - Generate before/after comparison plot saved to evidence/plots/before_after_comparison.png
    - Generate loss curve plot (if GRPO trained) saved to evidence/plots/loss_curve.png
    - Save training results JSON to evidence/eval/training_results.json
    - Save per-agent validation JSON to evidence/eval/per_agent_validation.json
    - Display summary report with file paths for all generated evidence files
    - Add error handling for matplotlib backend and missing data
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 11.6_

- [x] 14. Implement artifact export and download
  - [x] 14.1 Create ArtifactExporter class
    - Implement `collect_artifacts()` method gathering all file paths from training/checkpoints, evaluation/artifacts, evidence/
    - Implement `create_archive()` method creating zip with timestamp name (civicmind_results_YYYYMMDD_HHMMSS.zip)
    - Implement `get_archive_info()` method returning archive size and contents summary
    - Implement `trigger_download()` method with Colab-specific (files.download()) and Kaggle-specific (/kaggle/working/) logic
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

  - [ ]* 14.2 Write unit tests for ArtifactExporter
    - Test artifact collection
    - Test zip archive creation
    - Test archive integrity
    - Test archive info generation
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [x] 14.3 Create notebook cell for artifact export
    - Instantiate ArtifactExporter
    - Collect all artifacts from training, evaluation, evidence directories
    - Create zip archive with timestamp name
    - Display archive size and contents summary
    - Trigger download (Colab: files.download(), Kaggle: save to /kaggle/working/)
    - Add error handling for disk space and zip integrity validation
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 11.5_

- [x] 15. Implement progress monitoring and logging
  - [x] 15.1 Add progress monitoring to all long-running operations
    - Add tqdm progress bars to dataset generation, training loops, evaluation
    - Update progress every 10 seconds showing current step, elapsed time, estimated remaining time
    - Log key events to console (training start, epoch completion, checkpoint saved, evaluation complete)
    - Display live training metrics (current loss, current reward, epsilon value)
    - Add memory usage warnings when VRAM exceeds 90% capacity
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.6, 10.7_

  - [x] 15.2 Implement checkpoint saving on interruption
    - Add KeyboardInterrupt handling to training loops
    - Save checkpoint when interrupted
    - Display recovery instructions (load checkpoint and resume)
    - _Requirements: 10.5_

  - [x] 15.3 Create final success summary cell
    - Display success message when all steps complete
    - Show total runtime for entire pipeline
    - Show key results (improvement percentages, validation pass rate)
    - _Requirements: 10.7_

- [x] 16. Implement error handling and recovery
  - [x] 16.1 Create safe_operation wrapper function
    - Implement generic error handling wrapper with retry logic (max 3 attempts)
    - Add exponential backoff (1s, 2s, 4s) between retries
    - Display error messages with operation name and attempt number
    - Support fallback functions for graceful degradation
    - _Requirements: 11.2, 11.3, 11.4, 11.6_

  - [x] 16.2 Add specific error handlers
    - Add OOM error handler suggesting batch size reduction
    - Add model download failure handler with retry logic
    - Add checkpoint loading validation (check file exists before loading)
    - Add disk space validation before file operations
    - Add permission error handler with suggestions
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

  - [x] 16.3 Create "Reset Environment" functionality
    - Add button widget that clears all outputs
    - Reset all variables to initial state
    - Display instructions to restart from setup cell
    - _Requirements: 11.7_

- [x] 17. Add notebook documentation and instructions
  - [x] 17.1 Create comprehensive markdown documentation
    - Add markdown header explaining notebook purpose and expected outputs
    - Add "Quick Start" section with 3-step instructions
    - Add markdown cells before each major section explaining what will happen
    - Add estimated runtimes for each section
    - Add "Troubleshooting" section with common issues and solutions (OOM errors, model download failures, checkpoint loading issues)
    - Add links to GitHub repository and documentation
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_

  - [x] 17.2 Create final summary section
    - Add markdown cell summarizing all generated files and their purposes
    - List all output files with descriptions (checkpoints, JSON results, plots)
    - Add next steps guidance (how to use results, where to submit)
    - _Requirements: 12.7_

- [x] 18. Final checkpoint - Integration testing and validation
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 19. Write integration tests for complete workflows
  - Test Quick Q-Learning pipeline end-to-end (Setup → Data → Training → Eval → Export)
  - Test Evaluation Only pipeline (Setup → Load Checkpoints → Eval → Export)
  - Test error recovery scenarios (OOM during training, checkpoint loading failure)
  - Verify all files created in correct locations
  - Verify training completes within expected time limits
  - Verify improvement over random baseline
  - _Requirements: 3.4, 5.1, 8.7, 11.1, 11.3_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at major milestones
- Unit tests validate specific examples and edge cases for individual components
- Integration tests validate end-to-end workflows
- The notebook architecture prioritizes transparency with all logic in visible cells
- Conservative defaults (batch_size=2, fp16 precision) prevent OOM errors on Colab free tier
- Progress monitoring provides real-time feedback during long-running operations
- Comprehensive error handling ensures graceful degradation and clear recovery paths
