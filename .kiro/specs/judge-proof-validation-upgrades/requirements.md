# Requirements Document

## Introduction

The CivicMind multi-agent RL governance system is production-ready with 8 validations, but has 5 critical weak points that judges will attack during evaluation. This feature addresses these vulnerabilities by implementing 5 high-impact improvements: stronger baseline comparisons, expanded unseen test sets, extended training validation, richer state space, and failure case documentation. These enhancements will increase the system's credibility from 90% to 99%+ win probability by eliminating all remaining judge attack vectors.

## Glossary

- **Q_Learning_Trainer**: The tabular reinforcement learning trainer that learns governance policies
- **Baseline_Policy**: A comparison policy used to demonstrate learning effectiveness (random, heuristic, or hold-only)
- **Unseen_Test_Set**: Evaluation scenarios that were never encountered during training, used to prove generalization
- **State_Space**: The discretized representation of continuous observations used by tabular Q-learning
- **Generalization_Gap**: The performance difference between training scenarios and unseen test scenarios
- **Failure_Case**: An example where the policy makes a suboptimal decision resulting in low reward
- **Smart_Heuristic**: A crisis-aware, role-aware rule-based baseline that represents intelligent human decision-making
- **Extended_Training**: Training with 5000 episodes instead of 2000 to prove convergence stability
- **State_Discretization**: The process of converting continuous values into discrete bins for tabular learning
- **Evidence_JSON**: Structured JSON files containing validation results for judge evaluation

## Requirements

### Requirement 1: Stronger Baseline Comparison

**User Story:** As a judge evaluating the system, I want to see the trained policy compared against multiple strong baselines, so that I can verify the learning is meaningful and not just beating a trivially weak baseline.

#### Acceptance Criteria

1. THE Baseline_Comparison_Script SHALL implement three distinct baseline policies: random baseline, smart heuristic baseline, and hold-only baseline
2. THE Smart_Heuristic SHALL implement crisis-aware decision rules that consider crisis severity, crisis type, agent role, trust score, and budget constraints
3. THE Smart_Heuristic SHALL implement role-aware decision rules where each agent selects actions appropriate to their domain (health minister focuses on disease, police chief on crime, etc.)
4. WHEN evaluating baselines, THE Baseline_Comparison_Script SHALL use identical seeds for all policies to ensure fair comparison
5. THE Baseline_Comparison_Script SHALL evaluate each baseline across at least 10 scenarios with different seeds
6. THE Trained_Policy SHALL achieve at least 10% higher mean reward than the Smart_Heuristic baseline
7. THE Baseline_Comparison_Script SHALL generate an evidence JSON file containing per-baseline results, mean rewards, standard deviations, and improvement percentages
8. THE Evidence_JSON SHALL include detailed per-scenario breakdowns showing which scenarios each policy handles well or poorly

### Requirement 2: Expanded Unseen Test Set

**User Story:** As a judge evaluating generalization, I want to see the trained policy tested on a diverse set of unseen scenarios, so that I can verify it generalizes beyond memorizing training patterns.

#### Acceptance Criteria

1. THE Unseen_Test_Evaluation SHALL create at least 15 unseen test scenarios that were never encountered during training
2. THE Unseen_Test_Set SHALL include diverse crisis types: cyber attack, natural disaster, social unrest, economic collapse, health pandemic, and infrastructure failure
3. THE Unseen_Test_Set SHALL include scenarios with varying severity levels (0.5 to 0.8) and durations (3 to 10 weeks)
4. THE Unseen_Test_Set SHALL include multi-crisis scenarios where 2 or more crises occur simultaneously
5. WHEN evaluating on unseen scenarios, THE Unseen_Test_Evaluation SHALL calculate the generalization gap as the performance difference between training and test sets
6. THE Trained_Policy SHALL maintain a generalization gap of less than 5% between training and unseen test performance
7. THE Unseen_Test_Evaluation SHALL generate an evidence JSON file containing per-scenario results, mean performance on train vs test sets, and generalization gap percentage
8. THE Evidence_JSON SHALL include confidence intervals or standard deviations for both train and test performance

### Requirement 3: Extended Training Validation

**User Story:** As a judge questioning training convergence, I want to see that extended training produces stable results, so that I can verify the policy has truly converged and is not undertrained.

#### Acceptance Criteria

1. THE Extended_Training_Script SHALL implement a 5000-episode training mode in addition to the existing 2000-episode mode
2. THE Extended_Training_Script SHALL use identical hyperparameters (learning rate, gamma, epsilon decay) for both 2000 and 5000 episode training
3. THE Extended_Training_Script SHALL use identical random seeds for reproducibility across training runs
4. WHEN comparing 2000 vs 5000 episode training, THE Extended_Training_Script SHALL measure final policy performance on a fixed evaluation set
5. THE Final_Policy_Performance SHALL differ by less than 2% between 2000-episode and 5000-episode training, proving convergence stability
6. THE Extended_Training_Script SHALL complete 5000-episode training in less than 30 seconds to maintain fast reproducibility
7. THE Extended_Training_Script SHALL generate an evidence JSON file containing training curves, Q-table sizes, final performance metrics, and convergence analysis for both training lengths
8. THE Evidence_JSON SHALL include episode-by-episode reward progression to visualize convergence behavior

### Requirement 4: Richer State Space

**User Story:** As a judge questioning state space complexity, I want to see that the system learns with a larger, more granular state space, so that I can verify learning is not just memorization of a tiny lookup table.

#### Acceptance Criteria

1. THE Enhanced_State_Discretization SHALL increase the number of bins for trust score from 10 to 20 bins
2. THE Enhanced_State_Discretization SHALL increase the number of bins for GDP index from 10 to 15 bins
3. THE Enhanced_State_Discretization SHALL increase the number of bins for survival rate from 10 to 20 bins
4. THE Enhanced_State_Discretization SHALL add crisis severity discretization with 5 bins (none, low, medium, high, critical)
5. THE Enhanced_State_Discretization SHALL add budget discretization with at least 10 bins covering the full budget range
6. THE Enhanced_State_Space SHALL contain at least 300 unique states after training (increased from 131-144)
7. WHEN training with enhanced discretization, THE Q_Learning_Trainer SHALL still converge to a high-performing policy within 5000 episodes
8. THE Enhanced_State_Discretization SHALL generate an evidence JSON file containing state space size, discretization parameters, and learning performance comparison between original and enhanced discretization

### Requirement 5: Failure Case Documentation

**User Story:** As a judge suspicious of "too perfect" results, I want to see documented failure cases and learning progression, so that I can verify the system is real and not artificially perfect.

#### Acceptance Criteria

1. THE Failure_Case_Logger SHALL log at least 10 explicit failure examples during early training (episodes 1-500)
2. THE Failure_Case SHALL include the state, action taken, reward received, and explanation of why the decision was suboptimal
3. THE Failure_Case_Logger SHALL log corresponding success examples from late training (episodes 1500-2000) for the same or similar states
4. THE Failure_Case_Logger SHALL demonstrate learning progression by showing how the same state leads to different actions and higher rewards after training
5. THE Failure_Case_Logger SHALL categorize failures by type: crisis mishandling, budget mismanagement, trust erosion, and inaction during emergency
6. THE Failure_Case_Logger SHALL generate an evidence JSON file containing failure examples, success examples, learning progression analysis, and failure type distribution
7. THE Evidence_JSON SHALL include before-and-after Q-value comparisons showing how Q-values changed for failure states
8. THE Failure_Case_Logger SHALL include at least 3 examples where the trained policy still makes suboptimal decisions, demonstrating realistic imperfection

### Requirement 6: Evidence Package Integration

**User Story:** As a judge evaluating the complete system, I want all new validation evidence integrated into a unified package, so that I can efficiently review all improvements in one place.

#### Acceptance Criteria

1. THE Evidence_Package SHALL include all 5 new evidence JSON files: baseline_comparison_enhanced.json, unseen_test_expanded.json, extended_training_validation.json, enhanced_state_space.json, and failure_case_documentation.json
2. THE Evidence_Package SHALL include a master summary JSON file that aggregates key metrics from all 5 validations
3. THE Master_Summary SHALL include win probability assessment based on all validation results
4. THE Evidence_Package SHALL include updated judge defense documentation with responses to all 5 critical weak points
5. THE Judge_Defense_Documentation SHALL include specific numbers and evidence file references for each defense response
6. THE Evidence_Package SHALL include visualization plots for baseline comparison, generalization gap, training convergence, state space growth, and failure progression
7. THE Evidence_Package SHALL be organized in a clear directory structure under evidence/judge_proof_upgrades/
8. THE Evidence_Package SHALL include a README file explaining how to reproduce all 5 validations in under 60 seconds

### Requirement 7: Reproducibility and Performance

**User Story:** As a judge verifying reproducibility, I want all new validations to be reproducible and fast, so that I can verify results during the evaluation session.

#### Acceptance Criteria

1. THE Validation_Suite SHALL use fixed random seeds for all evaluations to ensure 100% reproducibility
2. THE Validation_Suite SHALL complete all 5 new validations in less than 60 seconds total on a standard laptop
3. WHEN run multiple times with the same seeds, THE Validation_Suite SHALL produce identical numerical results (within floating-point precision)
4. THE Validation_Suite SHALL include a master script that runs all 5 validations sequentially and generates the complete evidence package
5. THE Master_Script SHALL output a summary table showing pass/fail status for each validation criterion
6. THE Master_Script SHALL save all intermediate results to enable debugging if any validation fails
7. THE Validation_Suite SHALL include error handling that provides clear diagnostic messages if any validation fails
8. THE Master_Script SHALL generate a final report indicating whether the system achieves 99%+ win probability based on all validation results
