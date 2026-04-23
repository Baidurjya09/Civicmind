# %% [markdown]
# # 🏛 CivicMind — AI Governance Simulation
# ## Meta × Hugging Face OpenEnv Hackathon
#
# **All 5 themes in one environment:**
# - T1 Multi-Agent: 6 government agents + oversight
# - T2 Long-Horizon: 52-week city simulation
# - T3.1 Professional: Real tool/API calls
# - T3.2 Personal: Citizen petitions with schema drift
# - T4 Self-Improve: Auto-escalating difficulty
# - T5 Wild Card: Emergent Rebel agent spawns!
#
# **Bonus prizes targeted:** Fleet AI, Halluminate, Scale AI, Snorkel AI, Patronus AI, Mercor
#
# **NOTE:** This notebook is OPTIONAL. You can run everything locally!
# See TRAINING_GUIDE.md for local setup instructions.

# %% [markdown]
# ## Cell 1: Install Dependencies

# %%
# !pip install unsloth trl transformers datasets accelerate peft torch -q
# !pip install fastapi uvicorn streamlit pandas numpy -q
# !git clone https://github.com/YOUR_USERNAME/civicmind.git
# %cd civicmind

# Alternative: Upload civicmind.zip to Colab and extract
# from google.colab import files
# uploaded = files.upload()  # Upload civicmind.zip
# !unzip -q civicmind.zip
# %cd civicmind

# %% [markdown]
# ## Cell 2: Verify GPU

# %%
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    gpu = torch.cuda.get_device_properties(0)
    print(f"GPU: {gpu.name}")
    print(f"VRAM: {gpu.total_memory / 1e9:.1f} GB")
    print(f"BF16 supported: {torch.cuda.is_bf16_supported()}")
else:
    print("No GPU — use Colab Runtime > Change runtime type > A100 or T4")

# %% [markdown]
# ## Cell 3: Quick Environment Demo

# %%
import sys
sys.path.insert(0, ".")

from environment.civic_env import CivicMindEnv, CivicMindConfig
from agents.agent_definitions import ALL_AGENTS

# Create environment
env = CivicMindEnv(CivicMindConfig(
    max_weeks=8,
    difficulty=3,
    enable_rebel=True,
    enable_schema_drift=True,
    seed=42,
))

obs = env.reset()
print("Environment created!")
print(f"Agents: {list(obs.keys())}")
print(f"\nInitial city state:")
print(env.render())

# %% [markdown]
# ## Cell 4: Run a Demo Episode (Heuristic Policy)

# %%
from evaluation.evaluate import heuristic_policy, run_episode

print("Running demo episode with heuristic policy...\n")
result = run_episode(
    heuristic_policy,
    policy_name="Heuristic Demo",
    difficulty=4,
    max_weeks=12,
    seed=42,
    verbose=True,
)

print(f"\nEpisode complete!")
print(f"Mean reward: {result.mean_reward:.4f}")
print(f"Rebel spawned: {result.rebel_spawned}")
print(f"City survived: {not result.city_collapsed}")

# %% [markdown]
# ## Cell 5: Visualize Reward Curve

# %%
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

fig, axes = plt.subplots(2, 2, figsize=(14, 8))
fig.suptitle("CivicMind — Episode Metrics", fontsize=14, fontweight="bold")

weeks = list(range(1, len(result.rewards) + 1))

# Reward curve
ax1 = axes[0, 0]
ax1.plot(weeks, result.rewards, color="#378ADD", linewidth=2)
ax1.fill_between(weeks, result.rewards, alpha=0.15, color="#378ADD")
ax1.set_title("Composite Reward", fontweight="bold")
ax1.set_xlabel("Week")
ax1.set_ylabel("Reward [0–1]")
ax1.set_ylim(0, 1)
ax1.grid(alpha=0.3)

# Mark rebel spawn weeks
rebel_weeks = [i+1 for i, h in enumerate(result.rewards) if i < len(result.survival_rates)]
for w in rebel_weeks:
    if result.rebel_spawned and w == result.weeks_survived // 2:
        ax1.axvline(w, color="red", linestyle="--", alpha=0.7, label="Rebel spawned")

# Survival + Trust
ax2 = axes[0, 1]
ax2.plot(weeks, result.survival_rates, color="#1D9E75", linewidth=2, label="Survival")
ax2.plot(weeks, result.trust_scores, color="#D4537E", linewidth=2, label="Trust")
ax2.axhline(0.3, color="red", linestyle=":", alpha=0.5, label="Rebel threshold")
ax2.set_title("Survival & Trust", fontweight="bold")
ax2.set_xlabel("Week")
ax2.set_ylabel("Score [0–1]")
ax2.set_ylim(0, 1.1)
ax2.legend(fontsize=9)
ax2.grid(alpha=0.3)

# GDP curve
ax3 = axes[1, 0]
ax3.plot(weeks, result.gdp_indices, color="#BA7517", linewidth=2)
ax3.fill_between(weeks, result.gdp_indices, alpha=0.15, color="#BA7517")
ax3.set_title("GDP Index", fontweight="bold")
ax3.set_xlabel("Week")
ax3.set_ylabel("GDP Index")
ax3.grid(alpha=0.3)

# Reward improvement bar
ax4 = axes[1, 1]
n_chunks = min(4, len(result.rewards))
chunk_size = len(result.rewards) // n_chunks
chunk_means = []
chunk_labels = []
for i in range(n_chunks):
    chunk = result.rewards[i*chunk_size:(i+1)*chunk_size]
    chunk_means.append(sum(chunk) / len(chunk))
    chunk_labels.append(f"Wk {i*chunk_size+1}–{(i+1)*chunk_size}")
colors = plt.cm.Blues(np.linspace(0.4, 0.9, n_chunks))
bars = ax4.bar(chunk_labels, chunk_means, color=colors, edgecolor="white")
ax4.set_title("Reward by Phase", fontweight="bold")
ax4.set_ylabel("Mean Reward")
ax4.set_ylim(0, 1)
for bar, val in zip(bars, chunk_means):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
             f"{val:.3f}", ha="center", va="bottom", fontsize=10)
ax4.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig("evaluation/episode_metrics.png", dpi=150, bbox_inches="tight")
plt.show()
print("Chart saved to evaluation/episode_metrics.png")

# %% [markdown]
# ## Cell 6: Schema Drift Demo (Patronus AI Bonus)

# %%
from environment.citizen_engine import CitizenEngine
from environment.city_state import CityState

city = CityState()
city.reset()
ce = CitizenEngine(schema_drift=True)
ce.reset()

print("Schema Drift Demonstration (Patronus AI Bonus)\n")
print("Week 1  (v1 — simple):")
p1 = ce.generate_petitions(1, city)[0]
print(f"  Schema: {p1['schema_version']}")
print(f"  Fields: {list(p1['raw'].keys())}\n")

print("Week 7  (v2 — adds category):")
p2 = ce.generate_petitions(7, city)[0]
print(f"  Schema: {p2['schema_version']}")
print(f"  Fields: {list(p2['raw'].keys())}\n")

print("Week 12 (v3 — numeric priority score):")
p3 = ce.generate_petitions(12, city)[0]
print(f"  Schema: {p3['schema_version']}")
print(f"  Fields: {list(p3['raw'].keys())}\n")

print("Week 20 (v4 — nested metadata):")
p4 = ce.generate_petitions(20, city)[0]
print(f"  Schema: {p4['schema_version']}")
print(f"  Structure: citizen_id + complaint + metadata{list(p4['raw'].get('metadata', {}).keys())}\n")

print("Week 35 (v5 — enterprise JSON):")
p5 = ce.generate_petitions(35, city)[0]
print(f"  Schema: {p5['schema_version']}")
print(f"  Fields: {list(p5['raw'].keys())}")
print(f"  Meta: {list(p5['raw'].get('meta', {}).keys())}\n")

print("Urgency is ALWAYS normalized to [0,1] regardless of schema:")
for p in [p1, p2, p3, p4, p5]:
    print(f"  {p['schema_version']}: urgency_normalized = {p['urgency_normalized']}")

# %% [markdown]
# ## Cell 7: Crisis Escalation Demo (Theme 4 — Self-Improvement)

# %%
from environment.crisis_engine import CrisisEngine

print("Crisis Escalation by Difficulty (Theme 4 — Self-Improvement)\n")
print(f"{'Difficulty':<12} {'Crisis Count':<14} {'Max Severity':<14} Crises")
print("─" * 70)
for diff in [1, 3, 5, 7, 10]:
    ce = CrisisEngine(difficulty=diff)
    ce.reset(difficulty=diff)
    crises = ce.all_crises
    max_sev = max(c.severity for c in crises) if crises else 0
    names = ", ".join(c.name for c in crises[:3])
    if len(crises) > 3:
        names += f" +{len(crises)-3} more"
    print(f"  {diff:<10} {len(crises):<14} {max_sev:<14.2f} {names}")

# %% [markdown]
# ## Cell 8: Reward Model Test (PyTorch)

# %%
import torch
from rewards.reward_model import RewardModel, RewardShaperMLP, city_metrics_to_tensor
from environment.city_state import CityState

city = CityState()
city.reset()
rm = RewardModel()

print("PyTorch Reward Model Test\n")

# Test various city states
test_states = [
    ("Healthy city",   dict(survival_rate=0.99, trust_score=0.82, gdp_index=0.95)),
    ("Crisis city",    dict(survival_rate=0.85, trust_score=0.35, gdp_index=0.62)),
    ("Collapsed city", dict(survival_rate=0.55, trust_score=0.15, gdp_index=0.40)),
]

for label, overrides in test_states:
    city.reset()
    for k, v in overrides.items():
        setattr(city, k, v)
    reward = rm.compute(city, oversight_score=0.75, crisis_resolved=False, week=10)
    print(f"  {label:<20} → reward = {reward:.4f}  {'✓ valid' if 0<=reward<=1 else '✗ INVALID'}")

# Shaper MLP
print("\nReward Shaper MLP (dense intermediate rewards):")
shaper = RewardShaperMLP()
print(f"  Parameters: {sum(p.numel() for p in shaper.parameters()):,}")
city.reset()
vec = city_metrics_to_tensor(city.metrics_dict()).unsqueeze(0)
pred = shaper(vec)
print(f"  Input shape: {vec.shape}")
print(f"  Output: {pred.item():.4f}  [bounded 0–1: {'✓' if 0<=pred.item()<=1 else '✗'}]")

# %% [markdown]
# ## Cell 9: Generate Training Dataset

# %%
from training.data_generator import generate_dataset
import json

path = generate_dataset(
    n_samples=500,
    output_path="training/civicmind_dataset.jsonl",
    good_ratio=0.70,
)

samples = [json.loads(l) for l in open(path)]
good = [s for s in samples if s["is_good_action"]]
bad  = [s for s in samples if not s["is_good_action"]]

print(f"\nDataset Summary:")
print(f"  Total samples:  {len(samples)}")
print(f"  Good actions:   {len(good)} (reward: {sum(s['reward'] for s in good)/len(good):.3f} avg)")
print(f"  Bad actions:    {len(bad)} (reward:  {sum(s['reward'] for s in bad)/len(bad):.3f} avg)")
print(f"  Agents covered: {set(s['agent_id'] for s in samples)}")
print(f"  Saved to:       {path}")

# %% [markdown]
# ## Cell 10: GRPO Training (Requires A100/T4 GPU)

# %%
# NOTE: Run on A100 for best results. T4 works with smaller batch size.

import os
os.makedirs("training/checkpoints", exist_ok=True)
os.makedirs("evaluation", exist_ok=True)

from training.train_grpo import TrainingConfig, load_model, load_or_generate_dataset, build_grpo_trainer, RewardLogger

cfg = TrainingConfig(
    model_name="unsloth/Qwen2.5-7B-Instruct-bnb-4bit",
    num_train_epochs=2,
    max_weeks_per_episode=8,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    num_generations=4,
    max_new_tokens=256,
)

print("Loading model...")
model, tokenizer = load_model(cfg)

print("Loading dataset...")
dataset = load_or_generate_dataset(cfg, tokenizer)

print("Building trainer...")
trainer = build_grpo_trainer(model, tokenizer, dataset, cfg)

print(f"\nStarting GRPO training...")
print(f"  Model:   {cfg.model_name}")
print(f"  Epochs:  {cfg.num_train_epochs}")
print(f"  Dataset: {len(dataset)} samples")
print(f"  G:       {cfg.num_generations} generations per prompt")
print()

train_result = trainer.train()
print(f"\nTraining complete!")
print(f"  Loss:   {train_result.metrics.get('train_loss', 'N/A'):.4f}")
print(f"  Reward: {train_result.metrics.get('train_reward', 'N/A')}")

# Save
trainer.save_model("training/checkpoints/civicmind_final")
tokenizer.save_pretrained("training/checkpoints/civicmind_final")
print(f"  Saved → training/checkpoints/civicmind_final")

# %% [markdown]
# ## Cell 11: Before/After Comparison

# %%
from evaluation.evaluate import evaluate_policy, random_policy, heuristic_policy, comparison_table

print("Evaluating policies (3 episodes each, difficulty=3)...\n")

results = {}

# Random baseline
print("[1/2] Random Policy...")
results["Random Baseline"] = evaluate_policy(
    random_policy, "Random Baseline",
    n_episodes=3, difficulty=3, max_weeks=12
)

# Heuristic policy
print("\n[2/2] Heuristic Policy...")
results["Heuristic Policy"] = evaluate_policy(
    heuristic_policy, "Heuristic Policy",
    n_episodes=3, difficulty=3, max_weeks=12
)

comparison_table(results)

# Calculate improvement
r_random   = results["Random Baseline"]["mean_reward_avg"]
r_heuristic = results["Heuristic Policy"]["mean_reward_avg"]
delta = r_heuristic - r_random
pct   = delta / max(r_random, 0.001) * 100
print(f"\n  Improvement: {delta:+.4f} ({pct:+.1f}%)")

# %% [markdown]
# ## Cell 12: Upload to Hugging Face Hub

# %%
# from huggingface_hub import HfApi
# api = HfApi()
# api.upload_folder(
#     folder_path="training/checkpoints/civicmind_final",
#     repo_id="YOUR_USERNAME/civicmind-governance-agent",
#     repo_type="model",
# )
# print("Model uploaded to Hugging Face Hub!")

# Optional: Upload dataset
# from datasets import Dataset
# import json
# samples = [json.loads(l) for l in open("training/civicmind_dataset.jsonl")]
# ds = Dataset.from_list(samples)
# ds.push_to_hub("YOUR_USERNAME/civicmind-dataset")
# print("Dataset uploaded!")

# %% [markdown]
# ---
# ## Summary
#
# | Metric | Value |
# |--------|-------|
# | Themes covered | ALL 5 (T1–T5) |
# | Bonus prizes targeted | 6 (Fleet AI, Halluminate, Scale AI, Snorkel AI, Patronus AI, Mercor) |
# | Agent count | 7 (6 government + 1 oversight + rebel) |
# | Reward bounds | Strictly [0.0, 1.0] |
# | Crisis difficulties | 10 tiers, auto-escalating |
# | Schema drift versions | 5 (Patronus AI bonus) |
# | Wild card mechanic | Emergent rebel agent spawns on trust collapse |
# | Training algorithm | GRPO via Unsloth + HF TRL |
# | Base model | Qwen2.5-7B-Instruct (4-bit LoRA) |

print("Notebook complete! CivicMind is ready for the hackathon.")
