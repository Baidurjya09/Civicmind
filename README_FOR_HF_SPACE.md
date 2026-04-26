---
title: CivicMind - Multi-Agent Governance System
emoji: 🏛️
colorFrom: blue
colorTo: purple
sdk: docker
app_file: app.py
pinned: false
---

# 🏛️ CivicMind - Multi-Agent Governance System

**OpenEnv India Hackathon 2026**

A multi-agent reinforcement learning environment where 6 AI agents govern a city through crises using LLM-based decision making.

---

## 🚀 Quick Links

- **[🎮 Live Demo on HuggingFace Space](https://huggingface.co/spaces/Baidurjya09/civicmind)**
- **[📓 Training Notebook (Colab)](https://colab.research.google.com/github/Baidurjya09/Civicmind/blob/main/CivicMind_Training.ipynb)**
- **[📝 Blog Post](https://huggingface.co/spaces/Baidurjya09/civicmind/blob/main/BLOG_POST_FINAL.md)**

---

## 📊 Training Results

![Loss Curve](train_result_elite/plots/loss_curve.png)
![Training Summary](train_result_elite/plots/training_summary.png)
![Agent Diversity](train_result_elite/plots/agent_diversity_comparison.png)

### Key Metrics
| Metric | Value |
|--------|-------|
| SFT Initial Loss | 2.62 |
| SFT Final Loss | 0.10 |
| Loss Reduction | 96.2% |
| Agent Diversity | 87.4% active governance |
| Q-Learning Improvement | +18.4% reward |
| Training Time | ~37 minutes |
| Model | Qwen2.5-0.5B + LoRA |
| Trainable Params | 0.44% |

---

## 🎮 How It Works

### The 6 Government Agents
1. **Mayor** — Budget allocation, emergency powers
2. **Health Minister** — Hospitals, disease response
3. **Finance Officer** — Taxes, bonds, stimulus
4. **Police Chief** — Crime, protests
5. **Infrastructure Head** — Power grid, repairs
6. **Media Spokesperson** — Trust, misinformation control

### The Rebel Agent (Wild Card)
Spawns automatically when trust < 30% for 2+ weeks. Grows stronger if ignored. Can only be defeated by restoring trust above 55%.

### Crisis Engine
10 difficulty tiers. Auto-escalates based on performance:
- Difficulty 1: Single flood
- Difficulty 5: Flood + strike + disease
- Difficulty 10: Everything at once

---

## 🚀 Try the Demo

Use the interface above to:
- Run episodes with different difficulty levels
- Watch agents make decisions in real-time
- See how the rebel mechanic works
- Compare different agent strategies

---

## 📈 Training Results

### Q-Learning Training (Actual Results)

**Before vs After Training**:
```
Metric              Untrained    Trained     Improvement
─────────────────────────────────────────────────────────
Avg Reward          0.6890       0.8160      +18.4%
Final Trust         0.3387       0.7013      +107.0%
Final Survival      0.8708       0.8753      +0.5%
```

**Validation Against Multiple Baselines**:
- vs Random Baseline: +18.4% reward, +107.0% trust
- vs Rule-Based Heuristic: +12.2% reward, +61.3% trust
- vs Hold-Only Policy: +7.8% reward

---

## 🏆 Hackathon Theme Coverage

| Theme | Implementation |
|-------|---------------|
| T1: Multi-Agent | 6 gov agents + oversight + rebel |
| T2: Long-Horizon | 52-week simulation, compound effects |
| T3.1: Professional | 8 FastAPI tool endpoints |
| T3.2: Personal | Citizen petitions with schema drift |
| T4: Self-Improve | 10-tier auto-escalating difficulty |
| T5: Wild Card | Emergent rebel agent mechanic |

---

## 📁 Repository

Full code and training scripts: [GitHub](https://github.com/Baidurjya09/Civicmind)

---

**Built for Meta × Hugging Face OpenEnv Hackathon 2026**
