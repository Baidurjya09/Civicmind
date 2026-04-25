# 📓 CivicMind Notebooks

This directory contains Jupyter notebooks for training and evaluating CivicMind multi-agent RL models.

## 📁 Files

### `colab_training_pipeline.ipynb`
**Complete end-to-end training pipeline for Google Colab**

- ✅ Environment setup (auto-detects Colab/Kaggle/local)
- ✅ Dataset generation (500 synthetic samples)
- ✅ Q-learning training (~10 seconds)
- ✅ Model evaluation (compare 3 policies)
- ✅ Artifact export (automatic download)

**Runtime**: ~5 minutes for complete Q-learning pipeline

**Platforms**: Google Colab, Kaggle, Local Jupyter

### `COLAB_GUIDE.md`
**Comprehensive guide for using the Colab notebook**

- Step-by-step instructions
- Troubleshooting tips
- Performance benchmarks
- Customization options

## 🚀 Quick Start

### Option 1: Google Colab (Recommended)

1. Go to [Google Colab](https://colab.research.google.com/)
2. Upload `colab_training_pipeline.ipynb`
3. Click **Runtime → Run all**
4. Download results (~5 min)

See [COLAB_GUIDE.md](COLAB_GUIDE.md) for detailed instructions.

### Option 2: Local Jupyter

```bash
cd Civicmind
jupyter notebook notebooks/colab_training_pipeline.ipynb
```

### Option 3: Kaggle

1. Go to [Kaggle Notebooks](https://www.kaggle.com/code)
2. Upload `colab_training_pipeline.ipynb`
3. Run all cells
4. Results saved to `/kaggle/working/`

## 📊 What You'll Get

After running the notebook:

```
civicmind_results_YYYYMMDD_HHMMSS.zip
├── training/checkpoints/rl_policy.pkl
├── evaluation/artifacts/training_results.json
└── evidence/plots/q_learning_training_curve.png
```

**Typical Results**:
- Training time: ~10 seconds
- Reward improvement: +20% over random baseline
- Trust improvement: +104%
- States learned: 300-500

## 🎯 Training Modes

| Mode | Runtime | Requirements | Output |
|------|---------|--------------|--------|
| Quick Q-Learning | 10 sec | CPU | Q-table checkpoint |
| Full GRPO | 45 min | GPU | Fine-tuned LLM |
| Both Sequential | 45 min | GPU | Both models |
| Evaluation Only | 2 min | Checkpoints | Metrics only |

## 📚 Documentation

- **Colab Guide**: [COLAB_GUIDE.md](COLAB_GUIDE.md) - Complete usage guide
- **Main README**: [../README.md](../README.md) - Project overview
- **Requirements**: [../requirements.txt](../requirements.txt) - Dependencies
- **Design Doc**: [../.kiro/specs/colab-training-pipeline/design.md](../.kiro/specs/colab-training-pipeline/design.md) - Technical design

## 🔧 Customization

Edit the notebook cells to:
- Change training parameters (episodes, learning rate)
- Modify dataset size and composition
- Add custom evaluation policies
- Adjust export directories

## 🐛 Troubleshooting

**Common Issues**:

1. **"Repository clone failed"** → Continue anyway, files will be used
2. **"No GPU detected"** → Enable GPU in Runtime settings
3. **"Dependency installation failed"** → Restart runtime and retry
4. **"Download not triggered"** → Check Files panel in Colab

See [COLAB_GUIDE.md](COLAB_GUIDE.md) for detailed troubleshooting.

## 📈 Performance

**Colab Free Tier (CPU)**:
- Total runtime: ~5 minutes
- Q-learning: ~10 seconds
- No GPU required

**Colab Free Tier (T4 GPU)**:
- Q-learning: ~10 seconds (same as CPU)
- GRPO: ~45 minutes (GPU-accelerated)

## ✅ Validation

The notebook has been tested on:
- ✅ Google Colab (Free tier, T4 GPU)
- ✅ Kaggle Notebooks
- ✅ Local Jupyter (Python 3.8+)
- ✅ Windows, Linux, macOS

## 🎓 Learning Resources

**New to RL?**
- Start with "Quick Q-Learning" mode
- Review the evaluation metrics
- Check the training curves
- Compare with baseline policies

**Advanced Users?**
- Experiment with GRPO mode
- Modify reward functions
- Add custom policies
- Tune hyperparameters

## 📝 Citation

```bibtex
@software{civicmind2024,
  title={CivicMind: Multi-Agent Reinforcement Learning for Governance},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/civicmind}
}
```

## 🤝 Contributing

Found a bug or have a suggestion?
1. Open an issue on GitHub
2. Submit a pull request
3. Contact the maintainers

## 📄 License

See [../LICENSE](../LICENSE) for details.

---

**Ready to train?** Open `colab_training_pipeline.ipynb` and get started! 🚀
