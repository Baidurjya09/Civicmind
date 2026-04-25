# Judge Defense Notes (Harsh-Truth Ready)

Use these exact talking points when challenged.

## 1) "This looks too simple / toy RL"

**Answer**  
We intentionally optimized for verifiability and reproducibility under hackathon time constraints.  
The objective is not to maximize state count; it is to prove that the policy improves under measurable rewards and remains robust to reward hacking.

**Proof to cite**
- `evaluation/artifacts/baseline_vs_improved.json`
- `test_reward_hacking.py`
- `training/train_grpo.py` logs + checkpoint

## 2) "Are these really multi-agent or just copies?"

**Answer**  
Agents have distinct roles, observation slices, and reward-relevant action preferences.  
They operate in a shared environment, so one agent's action changes downstream context for others.

**Proof to cite**
- Role-specific observations/actions: `environment/civic_env.py`
- Agent-specific reward shaping: `training/train_grpo.py`

## 3) "Why not pure rule-based?"

**Answer**  
We benchmark against baseline policies and report measurable gain.  
If this were only scripted behavior, we would not observe reward lift across seeded episodes and stress scenarios.

**Proof to cite**
- `evaluation/artifacts/baseline_vs_improved.png`
- `evaluation/model_vs_baseline.py` output artifact

## 4) "Is this Q-learning?"

**Answer**  
No. This project uses a GRPO-style LLM RL loop for policy improvement, not tabular Q-learning.

## 5) "How do you prevent reward hacking?"

**Answer**  
We use multi-component rewards and explicit exploit tests:
- inaction during crisis is penalized
- low-budget abuse is penalized
- bounded reward range reduces degenerate optimization

**Proof to cite**
- `environment/reward_hardening.py`
- `test_reward_hacking.py`

## 6) "How to reproduce quickly?"

```bash
python test_reward_hacking.py
python evaluation/baseline_vs_improved.py
python evaluation/model_vs_baseline.py --checkpoint training/checkpoints/civicmind_grpo_gpu_smoke
```
