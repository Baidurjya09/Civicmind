# Design Document: Judge-Proof Validation Upgrades

## Overview

This design addresses 5 critical weak points in the CivicMind validation suite by implementing enhanced validation scripts that eliminate judge attack vectors. The system will add 5 new validation modules that integrate with the existing Q-learning trainer and evaluation infrastructure while maintaining fast reproducibility (< 60 seconds total runtime).

### Design Goals

1. **Eliminate Weak Baselines**: Replace trivial "hold-only" baseline with smart heuristic that represents intelligent human decision-making
2. **Prove Generalization**: Expand unseen test set from 4 to 15+ diverse scenarios covering all crisis types
3. **Demonstrate Convergence**: Show that 5000-episode training produces stable results within 2% of 2000-episode training
4. **Increase State Complexity**: Expand state space from ~140 states to 300+ states with finer discretization
5. **Show Realistic Learning**: Document failure cases from early training and learning progression to late training

### Key Constraints

- **Performance**: All 5 validations must complete in < 60 seconds total
- **Reproducibility**: Fixed seeds ensure identical results across runs
- **Integration**: Reuse existing environment, trainer, and evidence infrastructure
- **Backward Compatibility**: Enhanced state discretization must not break existing checkpoints (separate checkpoint path)

## Architecture

### System Components

```
judge-proof-validation-upgrades/
├── validation/
│   ├── baseline_comparison_enhanced.py      # Req 1: Multi-baseline comparison
│   ├── unseen_test_expanded.py              # Req 2: 15+ unseen scenarios
│   ├── extended_training_validation.py      # Req 3: 2000 vs 5000 episodes
│   ├── enhanced_state_space.py              # Req 4: Richer discretization
│   └── failure_case_documentation.py        # Req 5: Learning progression
├── evidence/
│   └── judge_proof_upgrades/
│       ├── baseline_comparison_enhanced.json
│       ├── unseen_test_expanded.json
│       ├── extended_training_validation.json
│       ├── enhanced_state_space.json
│       ├── failure_case_documentation.json
│       ├── master_summary.json
│       └── plots/
│           ├── baseline_comparison.png
│           ├── generalization_gap.png
│           ├── training_convergence.png
│           ├── state_space_growth.png
│           └── failure_progression.png
└── run_all_validations.py                   # Master orchestration script
```

### Integration Points

1. **Q-Learning Trainer** (`training/q_learning_trainer.py`):
   - Extended training mode: Add `episodes` parameter support
   - Enhanced state discretization: New `get_state_key_enhanced()` method
   - Failure logging: Add `failure_logger` callback parameter

2. **Environment** (`environment/civic_env.py`):
   - No changes required - existing interface sufficient
   - Crisis injection for scenario generation

3. **Evidence System** (`evidence/eval/`):
   - New subdirectory: `evidence/judge_proof_upgrades/`
   - Master summary aggregation script

## Components and Interfaces

### 1. Baseline Comparison Enhanced

**Purpose**: Compare trained policy against 3 baselines (random, smart heuristic, hold-only) across 10 scenarios.

**Interface**:
```python
def run_baseline_comparison(
    trained_policy_path: str,
    num_scenarios: int = 10,
    seeds: List[int] = None,
    output_path: str = "evidence/judge_proof_upgrades/baseline_comparison_enhanced.json"
) -> Dict[str, Any]
```

**Smart Heuristic Implementation**:
```python
def smart_heuristic_policy(obs: Dict) -> Dict[str, Dict]:
    """
    Crisis-aware, role-aware baseline representing intelligent human decisions.
    
    Decision Rules:
    1. Crisis Response Priority:
       - If active_crises and severity > 0.6: Emergency response mode
       - If active_crises and severity <= 0.6: Measured response mode
       - If no crises: Maintenance mode
    
    2. Role-Aware Actions:
       - Mayor: Budget management based on crisis severity
       - Health Minister: Disease response based on prevalence
       - Finance Officer: Economic stabilization based on unemployment
       - Police Chief: Security based on crime index
       - Infrastructure Head: Repairs based on grid health
       - Media Spokesperson: Trust building based on trust score
    
    3. Budget Constraints:
       - If budget < 200k: Conservative actions only
       - If budget >= 200k: Full action space available
    
    4. Trust Threshold:
       - If trust < 0.4: Prioritize trust-building actions
       - If trust >= 0.4: Normal operations
    """
```

**Output Schema**:
```json
{
  "evaluation_type": "baseline_comparison_enhanced",
  "date": "2026-04-25",
  "scenarios_evaluated": 10,
  "baselines": {
    "random": {
      "mean_reward": 0.6234,
      "std_dev": 0.0823,
      "per_scenario": [...]
    },
    "smart_heuristic": {
      "mean_reward": 0.7891,
      "std_dev": 0.0456,
      "per_scenario": [...]
    },
    "hold_only": {
      "mean_reward": 0.7123,
      "std_dev": 0.0512,
      "per_scenario": [...]
    },
    "trained_policy": {
      "mean_reward": 0.8734,
      "std_dev": 0.0389,
      "per_scenario": [...]
    }
  },
  "improvements": {
    "vs_random": "+40.1%",
    "vs_smart_heuristic": "+10.7%",
    "vs_hold_only": "+22.6%"
  },
  "statistical_significance": {
    "vs_smart_heuristic": {
      "t_statistic": 4.23,
      "p_value": 0.0012,
      "significant": true
    }
  }
}
```

### 2. Unseen Test Expanded

**Purpose**: Evaluate generalization on 15+ diverse unseen scenarios never seen during training.

**Interface**:
```python
def run_unseen_test_expanded(
    trained_policy_path: str,
    train_scenarios: List[Dict],
    test_scenarios: List[Dict],
    output_path: str = "evidence/judge_proof_upgrades/unseen_test_expanded.json"
) -> Dict[str, Any]
```

**Scenario Generation Strategy**:
```python
def generate_unseen_scenarios() -> List[Dict]:
    """
    Generate 15+ diverse unseen scenarios covering:
    
    Crisis Types (6 categories):
    - Cyber Attack: misinformation + trust erosion + grid damage
    - Natural Disaster: survival + hospital + infrastructure damage
    - Social Unrest: civil unrest + trust erosion + crime
    - Economic Collapse: unemployment + GDP crash + budget crisis
    - Health Pandemic: disease + survival + unemployment
    - Infrastructure Failure: grid + hospital + service disruption
    
    Severity Levels (3 levels):
    - Moderate: 0.5-0.6 severity
    - High: 0.6-0.7 severity
    - Critical: 0.7-0.8 severity
    
    Duration Variation:
    - Short: 3-4 weeks
    - Medium: 5-7 weeks
    - Long: 8-10 weeks
    
    Multi-Crisis Scenarios (3 scenarios):
    - 2 simultaneous crises
    - 3 simultaneous crises
    - Sequential crises (one triggers another)
    """
```

**Output Schema**:
```json
{
  "evaluation_type": "unseen_test_expanded",
  "train_set": {
    "scenarios": 5,
    "mean_reward": 0.8734,
    "std_dev": 0.0389,
    "per_scenario": [...]
  },
  "test_set": {
    "scenarios": 15,
    "mean_reward": 0.8512,
    "std_dev": 0.0456,
    "per_scenario": [...]
  },
  "generalization_gap": {
    "absolute": 0.0222,
    "percentage": 2.54,
    "assessment": "EXCELLENT - gap < 5%"
  },
  "scenario_breakdown": {
    "cyber_attack": {"count": 2, "mean_reward": 0.8423},
    "natural_disaster": {"count": 3, "mean_reward": 0.8234},
    "social_unrest": {"count": 2, "mean_reward": 0.8678},
    "economic_collapse": {"count": 2, "mean_reward": 0.8456},
    "health_pandemic": {"count": 3, "mean_reward": 0.8512},
    "infrastructure_failure": {"count": 3, "mean_reward": 0.8734}
  }
}
```

### 3. Extended Training Validation

**Purpose**: Prove convergence stability by comparing 2000-episode vs 5000-episode training.

**Interface**:
```python
def run_extended_training_validation(
    seed: int = 42,
    eval_scenarios: List[Dict] = None,
    output_path: str = "evidence/judge_proof_upgrades/extended_training_validation.json"
) -> Dict[str, Any]
```

**Training Comparison Strategy**:
```python
def compare_training_lengths():
    """
    1. Train with 2000 episodes (existing)
       - Save checkpoint: checkpoints/rl_policy_2000.pkl
       - Record training curve
    
    2. Train with 5000 episodes (extended)
       - Save checkpoint: checkpoints/rl_policy_5000.pkl
       - Record training curve
    
    3. Evaluate both on fixed test set (10 scenarios)
       - Use identical seeds for fair comparison
       - Measure mean reward, std dev, per-scenario performance
    
    4. Analyze convergence:
       - Performance delta: |reward_2000 - reward_5000|
       - Q-table size comparison
       - Training curve plateau detection
    """
```

**Output Schema**:
```json
{
  "evaluation_type": "extended_training_validation",
  "training_2000": {
    "episodes": 2000,
    "training_time_seconds": 8.23,
    "final_q_table_size": 142,
    "eval_mean_reward": 0.8734,
    "eval_std_dev": 0.0389,
    "training_curve": [...]
  },
  "training_5000": {
    "episodes": 5000,
    "training_time_seconds": 20.45,
    "final_q_table_size": 156,
    "eval_mean_reward": 0.8756,
    "eval_std_dev": 0.0378,
    "training_curve": [...]
  },
  "convergence_analysis": {
    "performance_delta_absolute": 0.0022,
    "performance_delta_percentage": 0.25,
    "converged": true,
    "assessment": "STABLE - delta < 2%"
  }
}
```

### 4. Enhanced State Space

**Purpose**: Demonstrate learning with richer state discretization (300+ states vs 140 states).

**Interface**:
```python
def run_enhanced_state_space_validation(
    seed: int = 42,
    output_path: str = "evidence/judge_proof_upgrades/enhanced_state_space.json"
) -> Dict[str, Any]
```

**Enhanced State Discretization**:
```python
def get_state_key_enhanced(observation: Dict[str, Any]) -> str:
    """
    Enhanced discretization with finer granularity:
    
    Original Discretization:
    - trust: 10 bins (0.0, 0.1, ..., 1.0)
    - gdp: 10 bins
    - survival: 10 bins
    - budget: 3 bins (< 200k, 200k-400k, > 400k)
    - crisis_count: 4 bins (0, 1, 2, 3+)
    - rebel_active: 2 bins (0, 1)
    
    Enhanced Discretization:
    - trust: 20 bins (0.00, 0.05, 0.10, ..., 1.00)
    - gdp: 15 bins (finer economic tracking)
    - survival: 20 bins (0.00, 0.05, 0.10, ..., 1.00)
    - budget: 10 bins (50k increments: 0-50k, 50k-100k, ..., 450k-500k)
    - crisis_severity: 5 bins (none=0, low=0.2, med=0.4, high=0.6, critical=0.8)
    - crisis_count: 4 bins (unchanged)
    - rebel_active: 2 bins (unchanged)
    
    State Space Size Estimate:
    - Original: 10 * 10 * 10 * 3 * 4 * 2 = 24,000 possible (140 learned)
    - Enhanced: 20 * 15 * 20 * 10 * 5 * 4 * 2 = 2,400,000 possible (300+ learned)
    """
```

**Backward Compatibility Strategy**:
- Use separate checkpoint path: `checkpoints/rl_policy_enhanced.pkl`
- Do NOT modify existing `get_state_key()` method
- Add new method: `get_state_key_enhanced()`
- Trainer parameter: `use_enhanced_discretization=True`

**Output Schema**:
```json
{
  "evaluation_type": "enhanced_state_space",
  "original_discretization": {
    "trust_bins": 10,
    "gdp_bins": 10,
    "survival_bins": 10,
    "budget_bins": 3,
    "crisis_severity_bins": 0,
    "theoretical_state_space": 24000,
    "learned_states": 142,
    "eval_mean_reward": 0.8734
  },
  "enhanced_discretization": {
    "trust_bins": 20,
    "gdp_bins": 15,
    "survival_bins": 20,
    "budget_bins": 10,
    "crisis_severity_bins": 5,
    "theoretical_state_space": 2400000,
    "learned_states": 318,
    "eval_mean_reward": 0.8812
  },
  "comparison": {
    "state_space_increase": "+124%",
    "performance_change": "+0.9%",
    "assessment": "Successfully learns with richer state space"
  }
}
```

### 5. Failure Case Documentation

**Purpose**: Document realistic learning progression from early failures to late successes.

**Interface**:
```python
def run_failure_case_documentation(
    seed: int = 42,
    output_path: str = "evidence/judge_proof_upgrades/failure_case_documentation.json"
) -> Dict[str, Any]
```

**Failure Logging Strategy**:
```python
class FailureLogger:
    """
    Logs failure cases during training for documentation.
    
    Failure Detection:
    - Episode reward < 0.6 (below acceptable threshold)
    - Trust drops below 0.3 (crisis mishandling)
    - Budget exhaustion (< 50k remaining)
    - Rebel strength > 0.5 (security failure)
    
    Logging Windows:
    - Early training: Episodes 1-500 (expect many failures)
    - Late training: Episodes 1500-2000 (expect few failures)
    
    Failure Categories:
    - crisis_mishandling: Active crisis but agent takes "hold" action
    - budget_mismanagement: Budget < 100k but agent spends on non-essentials
    - trust_erosion: Trust < 0.4 but no trust-building actions
    - inaction_during_emergency: Severity > 0.7 but no emergency response
    """
    
    def log_failure(self, episode: int, state: str, action: str, 
                   reward: float, q_values: Dict, reason: str):
        """Log a failure case with context"""
        
    def log_success(self, episode: int, state: str, action: str,
                   reward: float, q_values: Dict):
        """Log a success case for comparison"""
        
    def generate_report(self) -> Dict:
        """Generate failure progression report"""
```

**Output Schema**:
```json
{
  "evaluation_type": "failure_case_documentation",
  "early_training_failures": [
    {
      "episode": 23,
      "state": "(3, 8, 7, 1, 2, 0)",
      "action": "hold",
      "reward": 0.4523,
      "q_values": {"hold": 0.12, "crisis_response": 0.08, ...},
      "reason": "crisis_mishandling",
      "explanation": "Active crisis (severity 0.65) but agent chose 'hold' instead of emergency response"
    },
    ...
  ],
  "late_training_successes": [
    {
      "episode": 1823,
      "state": "(3, 8, 7, 1, 2, 0)",
      "action": "crisis_response",
      "reward": 0.8234,
      "q_values": {"hold": 0.45, "crisis_response": 0.82, ...},
      "explanation": "Same state as early failure - now correctly responds to crisis"
    },
    ...
  ],
  "learning_progression": {
    "early_failures": 47,
    "late_failures": 3,
    "improvement": "93.6% reduction in failures"
  },
  "failure_type_distribution": {
    "crisis_mishandling": 18,
    "budget_mismanagement": 12,
    "trust_erosion": 11,
    "inaction_during_emergency": 6
  },
  "realistic_imperfections": [
    {
      "episode": 1956,
      "state": "(2, 5, 6, 0, 3, 1)",
      "action": "invest_in_welfare",
      "reward": 0.6234,
      "explanation": "Suboptimal: Should have prioritized crisis response over welfare investment"
    },
    ...
  ]
}
```

## Data Models

### Scenario Definition
```python
@dataclass
class ValidationScenario:
    """Defines a test scenario for validation"""
    name: str
    seed: int
    crisis_type: str  # "cyber_attack", "natural_disaster", etc.
    severity: float  # 0.5-0.8
    duration: int  # 3-10 weeks
    effects: Dict[str, float]  # Metric changes
    multi_crisis: bool = False
    secondary_crises: List[Crisis] = None
```

### Baseline Policy Interface
```python
class BaselinePolicy(Protocol):
    """Interface for baseline policies"""
    def __call__(self, obs: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Args:
            obs: Environment observation dict
        Returns:
            actions: {agent_id: {"policy_decision": action_str}}
        """
        ...
```

### Evidence Report Schema
```python
@dataclass
class ValidationReport:
    """Standard evidence report structure"""
    evaluation_type: str
    date: str
    scenarios_evaluated: int
    mean_reward: float
    std_dev: float
    per_scenario_results: List[Dict]
    assessment: str
    pass_criteria_met: bool
```

## Error Handling

### Validation Failure Modes

1. **Training Timeout**:
   - If training exceeds 30 seconds, abort and report failure
   - Provide diagnostic: episode count, Q-table size, last reward

2. **Checkpoint Load Failure**:
   - If trained policy checkpoint missing, provide clear error
   - Suggest running training first

3. **Scenario Generation Failure**:
   - If crisis injection fails, skip scenario and log warning
   - Continue with remaining scenarios

4. **Performance Regression**:
   - If trained policy performs worse than smart heuristic, flag as critical failure
   - Generate detailed diagnostic report

### Error Messages

```python
class ValidationError(Exception):
    """Base class for validation errors"""
    pass

class TrainingTimeoutError(ValidationError):
    """Training exceeded time limit"""
    pass

class CheckpointNotFoundError(ValidationError):
    """Required checkpoint file not found"""
    pass

class PerformanceRegressionError(ValidationError):
    """Policy performance below acceptable threshold"""
    pass
```

## Testing Strategy

This feature does NOT use property-based testing because:
1. **Infrastructure Validation**: These are validation scripts that test the RL system, not pure functions
2. **Deterministic Outputs**: Fixed seeds ensure reproducible results - no need for randomized testing
3. **Integration Testing**: Focus is on end-to-end validation, not unit-level properties

### Unit Testing Approach

**Test Coverage**:
1. **Baseline Policies**: Verify each baseline produces valid actions
2. **Scenario Generation**: Verify all 15+ scenarios are unique and valid
3. **State Discretization**: Verify enhanced discretization produces correct bins
4. **Failure Detection**: Verify failure logger correctly identifies failure types
5. **Evidence Generation**: Verify JSON output matches schema

**Example Unit Tests**:
```python
def test_smart_heuristic_crisis_response():
    """Verify smart heuristic responds to crises"""
    obs = create_crisis_observation(severity=0.7)
    actions = smart_heuristic_policy(obs)
    assert actions["mayor"]["policy_decision"] != "hold"
    assert actions["health_minister"]["policy_decision"] != "hold"

def test_enhanced_discretization_bins():
    """Verify enhanced discretization creates correct bins"""
    obs = create_observation(trust=0.75, gdp=1.2, survival=0.85)
    state_key = get_state_key_enhanced(obs)
    # Trust 0.75 -> bin 15 (out of 20)
    # GDP 1.2 -> bin 8 (out of 15)
    # Survival 0.85 -> bin 17 (out of 20)
    assert "15" in state_key
    assert "8" in state_key
    assert "17" in state_key

def test_failure_logger_categorization():
    """Verify failure logger correctly categorizes failures"""
    logger = FailureLogger()
    # Crisis active but agent holds
    logger.log_failure(
        episode=10,
        state="(3,8,7,1,2,0)",
        action="hold",
        reward=0.45,
        q_values={"hold": 0.12},
        reason="crisis_mishandling"
    )
    report = logger.generate_report()
    assert report["failure_type_distribution"]["crisis_mishandling"] == 1
```

### Integration Testing

**End-to-End Validation**:
1. Run all 5 validations sequentially
2. Verify all evidence files generated
3. Verify master summary aggregates correctly
4. Verify total runtime < 60 seconds

**Reproducibility Testing**:
1. Run validation suite 3 times with same seeds
2. Verify identical numerical results (within floating-point precision)
3. Verify identical JSON outputs (byte-for-byte)

## Implementation Plan

### Phase 1: Core Infrastructure (Tasks 1-3)
1. Create validation directory structure
2. Implement baseline policies (random, smart heuristic, hold-only)
3. Implement scenario generation utilities

### Phase 2: Validation Scripts (Tasks 4-8)
4. Implement baseline_comparison_enhanced.py
5. Implement unseen_test_expanded.py
6. Implement extended_training_validation.py
7. Implement enhanced_state_space.py
8. Implement failure_case_documentation.py

### Phase 3: Integration (Tasks 9-11)
9. Implement master orchestration script
10. Implement evidence aggregation and master summary
11. Create visualization plots

### Phase 4: Documentation (Tasks 12-13)
12. Create judge defense documentation
13. Create reproducibility README

## Performance Considerations

### Runtime Optimization

**Target Breakdown** (60 seconds total):
- Baseline comparison: 15 seconds (10 scenarios × 3 baselines)
- Unseen test: 12 seconds (15 scenarios × 1 policy)
- Extended training: 25 seconds (5000 episodes)
- Enhanced state space: 6 seconds (training + eval)
- Failure documentation: 2 seconds (analysis only, reuses training data)

**Optimization Strategies**:
1. **Parallel Evaluation**: Run scenarios in parallel where possible
2. **Checkpoint Reuse**: Load trained policies once, reuse across validations
3. **Lazy Plotting**: Generate plots only if requested
4. **Efficient State Keys**: Use tuple hashing instead of string concatenation

### Memory Management

- Q-tables: ~1-2 MB each (300 states × 6 agents × 4 actions × 8 bytes)
- Episode history: Limit to last 100 episodes during training
- Evidence files: ~500 KB total (JSON compression)

## Dependencies

### Existing System Dependencies
- `environment/civic_env.py`: CivicMindEnv, CivicMindConfig
- `environment/crisis_engine.py`: Crisis, CrisisEngine
- `training/q_learning_trainer.py`: QLearningTrainer
- `evaluation/baseline_vs_improved.py`: Baseline policy patterns

### New Dependencies
- None - uses only Python standard library + existing dependencies

### Python Standard Library
- `json`: Evidence file generation
- `pickle`: Checkpoint loading
- `pathlib`: File path management
- `dataclasses`: Data structure definitions
- `typing`: Type annotations
- `time`: Performance measurement
- `statistics`: Mean, std dev calculations

## Deployment Considerations

### File Organization
```
Civicmind/
├── validation/
│   └── judge_proof_upgrades/
│       ├── __init__.py
│       ├── baseline_comparison_enhanced.py
│       ├── unseen_test_expanded.py
│       ├── extended_training_validation.py
│       ├── enhanced_state_space.py
│       ├── failure_case_documentation.py
│       ├── scenario_generator.py
│       └── baseline_policies.py
├── evidence/
│   └── judge_proof_upgrades/
│       ├── baseline_comparison_enhanced.json
│       ├── unseen_test_expanded.json
│       ├── extended_training_validation.json
│       ├── enhanced_state_space.json
│       ├── failure_case_documentation.json
│       ├── master_summary.json
│       └── plots/
└── run_judge_proof_validations.py
```

### Execution Workflow
```bash
# Run all validations
python run_judge_proof_validations.py

# Run individual validation
python validation/judge_proof_upgrades/baseline_comparison_enhanced.py

# Generate master summary
python validation/judge_proof_upgrades/generate_master_summary.py
```

### Evidence Package Structure
```
evidence/judge_proof_upgrades/
├── README.md                              # Reproducibility instructions
├── master_summary.json                    # Aggregated results
├── baseline_comparison_enhanced.json      # Req 1 evidence
├── unseen_test_expanded.json             # Req 2 evidence
├── extended_training_validation.json     # Req 3 evidence
├── enhanced_state_space.json             # Req 4 evidence
├── failure_case_documentation.json       # Req 5 evidence
├── judge_defense_responses.md            # Defense documentation
└── plots/
    ├── baseline_comparison.png
    ├── generalization_gap.png
    ├── training_convergence.png
    ├── state_space_growth.png
    └── failure_progression.png
```

## Security Considerations

### Input Validation
- Validate seed values are positive integers
- Validate scenario parameters are within valid ranges
- Validate checkpoint files are valid pickle format

### Output Sanitization
- Sanitize file paths to prevent directory traversal
- Validate JSON output is well-formed
- Limit file sizes to prevent disk exhaustion

### Reproducibility Security
- Fixed seeds prevent non-deterministic behavior
- Checksums for evidence files ensure integrity
- Version tracking for validation scripts

## Monitoring and Observability

### Progress Reporting
```python
def report_validation_progress(validation_name: str, progress: float):
    """Report validation progress to console"""
    print(f"[{validation_name}] {progress:.1%} complete")
```

### Performance Metrics
- Training time per episode
- Evaluation time per scenario
- Q-table growth rate
- Memory usage

### Validation Status
```python
@dataclass
class ValidationStatus:
    """Track validation execution status"""
    validation_name: str
    status: str  # "running", "completed", "failed"
    start_time: float
    end_time: float
    error_message: str = None
```

## Future Enhancements

### Potential Improvements (Out of Scope)
1. **Adaptive Baseline**: Baseline that learns from trained policy mistakes
2. **Cross-Validation**: K-fold cross-validation for generalization
3. **Hyperparameter Sensitivity**: Test robustness to hyperparameter changes
4. **Adversarial Scenarios**: Worst-case scenario generation
5. **Transfer Learning**: Test policy transfer to different difficulty levels

### Extensibility Points
- Plugin architecture for custom baselines
- Configurable scenario generation templates
- Custom failure detection rules
- Alternative state discretization schemes

## Conclusion

This design provides a comprehensive solution to the 5 critical weak points in the CivicMind validation suite. The architecture maintains backward compatibility, ensures fast reproducibility, and generates judge-proof evidence that eliminates all remaining attack vectors. The modular design allows each validation to be run independently or as part of the complete suite, with clear evidence outputs and diagnostic capabilities.
