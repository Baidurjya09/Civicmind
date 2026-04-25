# ⚡ Google Colab Quick Start - 3 Steps

## Step 1: Upload to Colab (2 minutes)

### Option A: Direct Upload (Easiest)
1. Go to https://colab.research.google.com/
2. Click **File** > **Upload notebook**
3. Select `Civicmind/notebooks/colab_training_pipeline.ipynb`
4. Click the **folder icon** (📁) in left sidebar
5. Click **upload button** (📤)
6. **Drag and drop** the entire `Civicmind` folder
7. Wait for upload (~2-3 min)

### Option B: From GitHub
1. Push your code to GitHub first
2. Go to https://colab.research.google.com/
3. Click **File** > **Open notebook** > **GitHub** tab
4. Enter: `https://github.com/YOUR_USERNAME/civicmind`
5. Select `notebooks/colab_training_pipeline.ipynb`
6. In first code cell, uncomment and fix the git clone line

## Step 2: Enable GPU (Optional - for GRPO)

1. Click **Runtime** > **Change runtime type**
2. Select **T4 GPU** under Hardware accelerator
3. Click **Save**

## Step 3: Run Everything

1. Click **Runtime** > **Run all** (or press Ctrl+F9)
2. Wait ~5 minutes for Quick Q-Learning
3. Or ~50 minutes for Full GRPO (with GPU)
4. Download results when complete

## That's It! 🎉

The notebook will:
- ✅ Auto-install all dependencies
- ✅ Generate training dataset
- ✅ Train Q-learning model
- ✅ Evaluate against baselines
- ✅ Generate plots and reports
- ✅ Package everything for download

## Expected Output

```
✅ Environment setup complete!
✅ GPU DETECTED! (if GPU enabled)
✅ Dataset generation complete! (100 samples)
✅ Q-Learning training complete! (318 states learned)
✅ Model evaluation complete! (+20% improvement)
✅ Evidence package generated!
✅ Artifact export complete!
📥 Downloading: civicmind_results_20260425_143022.zip
```

## Troubleshooting

**"CivicMind repository not found"**
→ Upload the Civicmind folder (Step 1)

**"No module named X"**
→ Restart runtime and re-run all cells

**"GPU Out of Memory"**
→ Reduce batch_size from 2 to 1 in the training mode widget

## Need More Help?

See `COLAB_SETUP_GUIDE.md` for detailed instructions and troubleshooting.
