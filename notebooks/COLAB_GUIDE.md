# 🏛️ CivicMind Training Pipeline - Google Colab Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Upload to Google Colab

1. Go to [Google Colab](https://colab.research.google.com/)
2. Click **File → Upload notebook**
3. Select `colab_training_pipeline.ipynb` from your computer
4. Wait for upload to complete

**OR** use this direct link (if hosted on GitHub):
```
https://colab.research.google.com/github/yourusername/civicmind/blob/main/notebooks/colab_training_pipeline.ipynb
```

### Step 2: Enable GPU (Recommended)

1. Click **Runtime → Change runtime type**
2. Select **T4 GPU** from the "Hardware accelerator" dropdown
3. Click **Save**
4. The runtime will restart

**Note**: GPU is optional for Q-learning (runs in 10 sec on CPU) but required for GRPO training.

### Step 3: Run the Pipeline

1. Click **Runtime → Run all** (or press `Ctrl+F9`)
2. The notebook will:
   - Clone the CivicMind repository
   - Install dependencies (~2 min)
   - Configure GPU
   - Generate dataset (~30 sec)
   - Train Q-learning model (~10 sec)
   - Evaluate performance (~2 min)
   - Package and download results (~10 sec)

**Total Runtime**: ~5 minutes for complete Q-learning pipeline

---

## 📋 What the Notebook Does

### Cell-by-Cell Breakdown:

| Cell | Description | Runtime | Output |
|------|-------------|---------|--------|
| 1 | Header & Documentation | Instant | Overview and instructions |
| 2 | Clone Repository | 30 sec | CivicMind repo in Colab |
| 3 | Install Dependencies | 2 min | PyTorch, Transformers, etc. |
| 4 | Configure GPU | 5 sec | Device setup (CUDA/CPU) |
| 5 | Training Mode Selection | Instant | Interactive dropdown widget |
| 6 | Generate Dataset | 30 sec | 500 training samples |
| 7 | Train Q-Learning | 10 sec | Trained Q-table checkpoint |
| 8 | Evaluate Models | 2 min | Performance comparison |
| 9 | Export Artifacts | 10 sec | Zip file download |
| 10 | Success Summary | Instant | Final results |

---

## 🎯 Training Modes

The notebook supports 4 training modes (select in Cell 5):

### 1. Quick Q-Learning (Recommended for First Run)
- **Runtime**: ~10 seconds
- **Requirements**: CPU only
- **Output**: Trained Q-table, evaluation results
- **Best for**: Testing, validation, CPU-only environments

### 2. Full GRPO
- **Runtime**: ~45 minutes (with T4 GPU)
- **Requirements**: GPU required
- **Output**: Fine-tuned LLM, evaluation results
- **Best for**: LLM-based RL research

### 3. Both Sequential
- **Runtime**: ~45 minutes (with T4 GPU)
- **Requirements**: GPU required
- **Output**: Both Q-learning and GRPO results
- **Best for**: Comparing approaches

### 4. Evaluation Only
- **Runtime**: ~2 minutes
- **Requirements**: Existing checkpoints
- **Output**: Evaluation results only
- **Best for**: Re-running evaluation

---

## 📦 What Gets Downloaded

After running the pipeline, you'll download a zip file containing:

```
civicmind_results_YYYYMMDD_HHMMSS.zip
├── training/
│   └── checkpoints/
│       └── rl_policy.pkl              # Trained Q-table
├── evaluation/
│   └── artifacts/
│       └── training_results.json      # Evaluation metrics
├── evidence/
│   ├── eval/
│   │   └── training_results.json      # Detailed results
│   └── plots/
│       └── q_learning_training_curve.png  # Training visualization
```

**File Sizes**:
- Q-table checkpoint: ~50-100 KB
- Evaluation results: ~5-10 KB
- Training plots: ~50-100 KB
- **Total archive**: ~200-300 KB

---

## 🔧 Customization

### Adjust Training Parameters

In Cell 5, expand the "Training Parameters (Advanced)" accordion to customize:

**Q-Learning Parameters**:
- Episodes: 2000 (default) - More episodes = better learning
- Epsilon decay: 1.0 → 0.1 (exploration to exploitation)
- Learning rate: 0.1 (how fast to update Q-values)

**Dataset Parameters**:
- Samples: 500 (default) - More samples = more diverse training data
- Good ratio: 0.7 (70% good actions, 30% bad actions)

**Evaluation Parameters**:
- Episodes: 5 (default) - More episodes = more reliable metrics

### Modify Code

You can edit any cell to customize behavior:
- Change environment difficulty (Cell 7)
- Add custom policies (Cell 8)
- Modify export directories (Cell 9)

---

## 📊 Expected Results

### Q-Learning Performance:

**Typical Metrics** (after 2000 episodes):
- States learned: 300-500
- Training time: 8-12 seconds
- Mean reward improvement: +15% to +25% over random baseline
- Trust score improvement: +50% to +150%

**Comparison Table** (Cell 8 output):
```
Policy                    Mean Reward  Final Reward  Survival  Rebel%
─────────────────────────────────────────────────────────────────────
Random Baseline                0.6234        0.6189    75.2%    40.0%
Heuristic Baseline             0.6891        0.6845    82.1%    20.0%
Trained Q-Learning             0.7512        0.7468    88.5%    20.0%
```

**Improvement Analysis**:
- Trained vs Random: +20.5% reward improvement
- Trained vs Heuristic: +9.0% reward improvement
- Trust improvement: +104% over random baseline

---

## 🐛 Troubleshooting

### Issue: "Repository clone failed"
**Solution**: The notebook will continue with existing files. If you see errors later, manually upload the CivicMind folder to Colab.

### Issue: "Dependency installation failed"
**Solution**: 
1. Click **Runtime → Restart runtime**
2. Run Cell 3 again
3. Check internet connection

### Issue: "No GPU detected"
**Solution**:
1. Go to **Runtime → Change runtime type**
2. Select **T4 GPU** or **GPU**
3. Click **Save**
4. Re-run all cells from the beginning

### Issue: "Checkpoint file not found" (in Evaluation Only mode)
**Solution**: Run the training cells first (Cells 6-7) to create checkpoints.

### Issue: "Download not triggered"
**Solution**: 
- Check your browser's download settings
- Look for the file in Colab's file browser (left sidebar)
- Manually download from the Files panel

### Issue: "Out of memory (OOM)"
**Solution**:
- This shouldn't happen with Q-learning (CPU-based)
- If using GRPO mode, reduce batch_size from 2 to 1
- Restart runtime to clear memory

---

## 💡 Tips & Best Practices

### For First-Time Users:
1. ✅ Use "Quick Q-Learning" mode
2. ✅ Keep default parameters
3. ✅ Run all cells sequentially
4. ✅ Wait for each cell to complete before proceeding

### For Advanced Users:
1. 🔧 Experiment with different episode counts
2. 🔧 Try different good/bad action ratios
3. 🔧 Modify the evaluation seeds for different scenarios
4. 🔧 Add custom baseline policies

### For Reproducibility:
1. 📌 Note the random seeds used (42, 43, 44, 45, 46)
2. 📌 Keep the same training parameters
3. 📌 Use the same environment difficulty
4. 📌 Save the downloaded archive with results

---

## 📈 Performance Benchmarks

### Colab Free Tier (CPU):
- Environment setup: ~2 minutes
- Dataset generation: ~30 seconds
- Q-learning training: ~10 seconds
- Evaluation: ~2 minutes
- **Total**: ~5 minutes

### Colab Free Tier (T4 GPU):
- Environment setup: ~2 minutes
- Dataset generation: ~30 seconds
- Q-learning training: ~10 seconds (CPU-based)
- GRPO training: ~45 minutes (if selected)
- Evaluation: ~2 minutes
- **Total**: ~5 minutes (Q-learning) or ~50 minutes (GRPO)

### Colab Pro (A100 GPU):
- GRPO training: ~20-25 minutes (faster than T4)
- All other times similar to free tier

---

## 🔗 Useful Links

- **CivicMind GitHub**: https://github.com/yourusername/civicmind
- **Google Colab**: https://colab.research.google.com/
- **Documentation**: See README.md in the repository
- **Issues**: Report bugs on GitHub Issues

---

## 📝 Citation

If you use this notebook in your research, please cite:

```bibtex
@software{civicmind2024,
  title={CivicMind: Multi-Agent Reinforcement Learning for Governance},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/civicmind}
}
```

---

## ✅ Checklist

Before running the notebook:
- [ ] Uploaded notebook to Google Colab
- [ ] Enabled GPU (optional but recommended for GRPO)
- [ ] Read the Quick Start guide
- [ ] Understand the training modes

After running the notebook:
- [ ] Downloaded the results archive
- [ ] Reviewed the evaluation metrics
- [ ] Checked the training plots
- [ ] Saved the archive for submission

---

## 🎉 Success!

If you see this message at the end of the notebook:

```
✅ Pipeline Complete!
   Archive: civicmind_results_YYYYMMDD_HHMMSS.zip
   Size: X.XX MB
   Files: XX
   Ready for submission!
```

Congratulations! You've successfully trained and evaluated a CivicMind RL agent. 🏛️

---

**Questions or Issues?**
- Check the Troubleshooting section above
- Review the notebook documentation
- Open an issue on GitHub
- Contact the maintainers

**Happy Training!** 🚀
