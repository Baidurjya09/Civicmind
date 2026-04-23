# 🚀 CivicMind — Local Training Guide

Complete guide for training CivicMind locally (no Colab needed).

## Hardware Requirements

### Minimum (Training Possible)
- GPU: RTX 3060 (12GB VRAM) or better
- RAM: 16GB
- Storage: 20GB free

### Recommended (Fast Training)
- GPU: RTX 3090/4090 (24GB VRAM) or A100
- RAM: 32GB+
- Storage: 50GB free (for checkpoints)

### Budget Options
- **Cloud GPU**: RunPod, Vast.ai, Lambda Labs ($0.30-0.80/hour)
- **Free Tier**: Google Colab (T4 GPU, limited hours)
- **CPU Only**: Possible but 50x slower (not recommended)

## Setup

### 1. Install CUDA Toolkit

**Ubuntu/Debian:**
```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get install cuda-toolkit-12-1
```

**Windows:**
Download from: https://developer.nvidia.com/cuda-downloads

Verify:
```bash
nvidia-smi
nvcc --version
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If you get CUDA errors, install PyTorch manually:
```bash
# For CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 4. Verify GPU Access

```bash
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"
```

Expected output:
```
CUDA: True
GPU: NVIDIA GeForce RTX 4090
```

## Training Workflow

### Step 1: Generate Dataset

```bash
python training/data_generator.py --n_samples 500 --output training/civicmind_dataset.jsonl
```

This creates 500 synthetic episodes with good/bad action labels.

### Step 2: Configure Training

Edit `training/train_grpo.py` if needed:

```python
cfg = TrainingConfig(
    model_name="unsloth/Qwen2.5-7B-Instruct-bnb-4bit",  # 4-bit quantized
    num_train_epochs=2,                                  # Increase for better results
    per_device_train_batch_size=1,                       # Increase if you have VRAM
    gradient_accumulation_steps=4,                       # Effective batch = 1*4 = 4
    max_weeks_per_episode=12,                            # Episode length
    num_generations=4,                                   # GRPO: samples per prompt
    max_new_tokens=256,                                  # Agent response length
)
```

**Memory optimization:**
- 12GB VRAM: `batch_size=1, gradient_accumulation=4`
- 24GB VRAM: `batch_size=2, gradient_accumulation=2`
- 40GB+ VRAM: `batch_size=4, gradient_accumulation=1`

### Step 3: Start Training

```bash
python training/train_grpo.py --mode train --epochs 2 --max_weeks 12
```

**Expected output:**
```
Loading model...
  Model: unsloth/Qwen2.5-7B-Instruct-bnb-4bit
  Trainable params: 41,943,040 (4-bit LoRA)
  
Loading dataset...
  500 samples loaded
  
Building GRPO trainer...
  Reward model: PyTorch composite scorer
  
Training...
Epoch 1/2: 100%|████████| 125/125 [12:34<00:00, 6.04s/it]
  train_loss: 0.4523
  train_reward: 0.5124
  
Epoch 2/2: 100%|████████| 125/125 [12:28<00:00, 5.98s/it]
  train_loss: 0.3891
  train_reward: 0.5847
  
Training complete!
  Saved → training/checkpoints/civicmind_final
```

**Training time estimates:**
- RTX 3060 (12GB): ~45 min for 2 epochs
- RTX 4090 (24GB): ~25 min for 2 epochs
- A100 (40GB): ~15 min for 2 epochs

### Step 4: Evaluate

```bash
python evaluate.py --mode full --model_path training/checkpoints/civicmind_final
```

This runs 3 episodes each for:
1. Random baseline
2. Heuristic policy
3. Trained LLM policy

**Expected improvement:**
```
Policy              Mean Reward    Improvement
─────────────────────────────────────────────
Random Baseline        0.4523         —
Heuristic Policy       0.4982        +10.2%
Trained (GRPO)         0.5447        +20.4%
```

## Troubleshooting

### Out of Memory (OOM)

**Error:** `CUDA out of memory`

**Solutions:**
1. Reduce batch size:
   ```python
   per_device_train_batch_size=1
   gradient_accumulation_steps=8  # Keep effective batch size
   ```

2. Use smaller model:
   ```python
   model_name="unsloth/Qwen2.5-3B-Instruct-bnb-4bit"  # 3B instead of 7B
   ```

3. Reduce sequence length:
   ```python
   max_new_tokens=128  # Down from 256
   ```

4. Enable gradient checkpointing (already enabled in code)

### Slow Training

**Issue:** Training takes hours

**Solutions:**
1. Check GPU utilization:
   ```bash
   watch -n 1 nvidia-smi
   ```
   Should show 90%+ GPU usage.

2. Increase batch size if you have VRAM:
   ```python
   per_device_train_batch_size=2  # or 4
   ```

3. Use mixed precision (already enabled via `bf16=True`)

4. Reduce dataset size for testing:
   ```bash
   python training/data_generator.py --n_samples 100
   ```

### Model Not Improving

**Issue:** Reward stays flat or decreases

**Solutions:**
1. Check reward function bounds:
   ```bash
   python -c "from rewards.reward_model import RewardModel; rm = RewardModel(); print('Reward model loaded')"
   ```

2. Increase training epochs:
   ```python
   num_train_epochs=5  # Up from 2
   ```

3. Adjust learning rate:
   ```python
   learning_rate=5e-5  # Default is 1e-4
   ```

4. Verify dataset quality:
   ```bash
   python -c "import json; samples = [json.loads(l) for l in open('training/civicmind_dataset.jsonl')]; print(f'Good: {sum(s[\"is_good_action\"] for s in samples)}/{len(samples)}')"
   ```
   Should be ~70% good actions.

### CUDA Version Mismatch

**Error:** `CUDA driver version is insufficient`

**Solution:**
Update NVIDIA drivers:
```bash
# Ubuntu
sudo apt-get update
sudo apt-get install nvidia-driver-535

# Windows: Download from nvidia.com
```

## Advanced: Multi-GPU Training

If you have multiple GPUs:

```bash
# Use all GPUs
CUDA_VISIBLE_DEVICES=0,1,2,3 python training/train_grpo.py --mode train

# Or use accelerate
accelerate launch --multi_gpu --num_processes 4 training/train_grpo.py --mode train
```

## Cloud GPU Options

### RunPod (Recommended)
- RTX 4090: $0.69/hour
- A100 (40GB): $1.89/hour
- Setup: https://www.runpod.io/

### Vast.ai (Cheapest)
- RTX 3090: $0.30/hour
- A100: $1.20/hour
- Setup: https://vast.ai/

### Lambda Labs
- A100 (40GB): $1.10/hour
- Setup: https://lambdalabs.com/

### Google Colab (Free Tier)
- T4 GPU: Free (limited hours)
- A100: $9.99/month
- Use `CivicMind_Colab.py` notebook

## Monitoring Training

### Weights & Biases (Recommended)

1. Sign up: https://wandb.ai/
2. Get API key
3. Add to `.env`:
   ```
   WANDB_API_KEY=your_key_here
   WANDB_PROJECT=civicmind
   ```
4. Training will auto-log to W&B dashboard

### TensorBoard (Built-in)

```bash
tensorboard --logdir training/checkpoints/civicmind_final/runs
```

Open: http://localhost:6006

## Next Steps

After training:

1. **Upload to Hugging Face:**
   ```bash
   huggingface-cli login
   python -c "from huggingface_hub import HfApi; api = HfApi(); api.upload_folder(folder_path='training/checkpoints/civicmind_final', repo_id='YOUR_USERNAME/civicmind-agent', repo_type='model')"
   ```

2. **Run live demo:**
   ```bash
   streamlit run demo/dashboard.py
   ```

3. **Deploy API:**
   ```bash
   docker-compose up -d api dashboard
   ```

## Questions?

Open an issue on GitHub or check the main README.md for more info.
