# 🚀 Google Colab Setup Guide

## Quick Start (2 Methods)

### Method 1: Upload Files Directly (Recommended - Fastest)

1. **Open the notebook in Colab**:
   - Go to https://colab.research.google.com/
   - Click "File" > "Upload notebook"
   - Upload `notebooks/colab_training_pipeline.ipynb`

2. **Upload the Civicmind folder**:
   - Click the folder icon (📁) in the left sidebar
   - Click the upload button (📤)
   - **Upload the entire `Civicmind` folder** from your local machine
   - Wait for upload to complete (~2-3 minutes for all files)

3. **Run the notebook**:
   - Click "Runtime" > "Run all"
   - Or press Ctrl+F9 (Cmd+F9 on Mac)

### Method 2: Clone from GitHub

1. **Push your code to GitHub** (if not already done):
   ```bash
   cd Civicmind
   git init
   git add .
   git commit -m "Add CivicMind training pipeline"
   git remote add origin https://github.com/YOUR_USERNAME/civicmind.git
   git push -u origin main
   ```

2. **Open the notebook in Colab**:
   - Go to https://colab.research.google.com/
   - Click "File" > "Open notebook"
   - Select "GitHub" tab
   - Enter your repository URL
   - Select `notebooks/colab_training_pipeline.ipynb`

3. **Modify the first code cell**:
   - Find the line: `# !git clone https://github.com/YOUR_GITHUB_USERNAME/civicmind.git Civicmind`
   - Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username
   - Uncomment the line (remove the `#`)

4. **Run the notebook**:
   - Click "Runtime" > "Run all"

## Enable GPU (For GRPO Training)

1. Click "Runtime" > "Change runtime type"
2. Under "Hardware accelerator", select **"T4 GPU"** or **"GPU"**
3. Click "Save"
4. The runtime will restart - re-run all cells

## What to Expect

### Quick Q-Learning Mode (~5 minutes)
- ✅ Environment setup: 2 min
- ✅ Dataset generation: 30 sec
- ✅ Q-learning training: 10 sec
- ✅ Evaluation: 2 min
- ✅ Evidence generation: 30 sec
- ✅ Artifact export: 10 sec

### Full GRPO Mode (~50 minutes with GPU)
- ✅ Everything above PLUS:
- ✅ GRPO training: 45 min (requires GPU)
- ✅ GRPO evaluation: 2 min
- ✅ Loss curve generation: 10 sec

## Troubleshooting

### "CivicMind repository not found"
**Solution**: Upload the Civicmind folder using Method 1 above

### "No module named 'transformers'"
**Solution**: The notebook will auto-install this. If it fails:
- Restart runtime (Runtime > Restart runtime)
- Re-run all cells

### "GPU Out of Memory"
**Solution**: 
- Reduce GRPO batch size from 2 to 1
- Or skip GRPO training (use Quick Q-Learning mode)

### "Checkpoint file not found"
**Solution**: 
- Ensure training cells completed successfully
- Check that you ran all cells in order
- Don't skip the training cells

## File Structure After Upload

Your Colab environment should look like this:
```
/content/
└── Civicmind/
    ├── environment/
    │   └── setup.py
    ├── training/
    │   ├── data_generator.py
    │   ├── q_learning_trainer.py
    │   ├── grpo_trainer.py
    │   ├── evaluation_engine.py
    │   ├── artifact_exporter.py
    │   └── evidence_generator.py
    ├── evaluation/
    │   └── anti_hacking_validation.py
    ├── agents/
    ├── core/
    ├── apis/
    └── requirements.txt
```

## Download Results

After the pipeline completes:
1. The final cell will automatically trigger a download
2. You'll get a ZIP file named `civicmind_results_YYYYMMDD_HHMMSS.zip`
3. Extract it to see all results:
   - Trained model checkpoints
   - Evaluation metrics (JSON)
   - Training plots (PNG)
   - Validation reports
   - Summary report (Markdown)

## Tips for Success

✅ **Use GPU for GRPO** - It's 100x faster than CPU
✅ **Start with Quick Q-Learning** - Validate the pipeline works first
✅ **Keep Colab tab active** - Prevents disconnection during long training
✅ **Save checkpoints** - The notebook auto-saves every epoch
✅ **Download results immediately** - Colab sessions expire after 12 hours

## Need Help?

1. Check the Troubleshooting section in the notebook
2. Review the error messages - they include specific fixes
3. Try restarting the runtime and re-running all cells
4. Ensure you uploaded ALL files from the Civicmind folder

## Success Indicators

You'll know it's working when you see:
- ✅ "Environment setup complete!"
- ✅ "GPU DETECTED!" (if GPU enabled)
- ✅ "Training complete!"
- ✅ "Evaluation complete!"
- ✅ "Evidence package generated!"
- ✅ "Artifact export complete!"

Happy training! 🎉
