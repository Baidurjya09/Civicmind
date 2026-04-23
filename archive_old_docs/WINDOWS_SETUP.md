# 🪟 CivicMind — Windows Setup Guide

Complete setup guide for Windows with NVIDIA GPU.

## ✅ Prerequisites Check

### 1. Check Your GPU

Open PowerShell and run:
```powershell
nvidia-smi
```

You should see your GPU info:
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.xx       Driver Version: 535.xx       CUDA Version: 12.1    |
|-------------------------------+----------------------+----------------------+
| GPU  Name            TCC/WDDM | Bus-Id        Disp.A | Volatile Uncorr. ECC |
|   0  NVIDIA GeForce RTX 3060  | 00000000:01:00.0  On |                  N/A |
+-----------------------------------------------------------------------------+
```

**No output?** Install NVIDIA drivers from: https://www.nvidia.com/download/index.aspx

### 2. Check Python

```powershell
python --version
```

Should show: `Python 3.10.x` or higher

**Not installed?** Download from: https://www.python.org/downloads/

**Important:** Check "Add Python to PATH" during installation!

## 🚀 Installation (5 Minutes)

### Step 1: Download CivicMind

```powershell
# Option 1: Git (if installed)
git clone https://github.com/YOUR_USERNAME/civicmind.git
cd civicmind

# Option 2: Download ZIP
# Download from GitHub → Extract → Open folder in PowerShell
```

### Step 2: Create Virtual Environment

```powershell
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your prompt.

### Step 3: Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This takes 5-10 minutes. Grab a coffee! ☕

### Step 4: Verify Installation

```powershell
python verify_setup.py
```

Should show all ✅ checks passing.

### Step 5: Check GPU

```powershell
python check_gpu.py
```

Should show:
```
✅ Your GPU is ready for training!
GPU name: NVIDIA GeForce RTX 3060
GPU memory: 12.9 GB
```

## 🎮 Quick Start

### Run Demo (No Training)

```powershell
run_local.bat eval
```

Or manually:
```powershell
python evaluate.py --mode compare --n_episodes 3
```

### Train on Your GPU

```powershell
run_local.bat train
```

Or manually:
```powershell
python training/data_generator.py --n_samples 500
python training/train_grpo.py --mode train --epochs 2 --max_weeks 12
```

**Time:** ~45 minutes on RTX 3060

### Launch Dashboard

```powershell
run_local.bat dashboard
```

Or manually:
```powershell
streamlit run demo/dashboard.py
```

Open: http://localhost:8501

### Full Stack (API + Dashboard)

```powershell
run_local.bat all
```

Open:
- API: http://localhost:8080/docs
- Dashboard: http://localhost:8501

## 🐛 Common Windows Issues

### Issue 1: "python not recognized"

**Solution:**
1. Reinstall Python with "Add to PATH" checked
2. Or add manually:
   - Search "Environment Variables"
   - Edit PATH
   - Add: `C:\Users\YOUR_USERNAME\AppData\Local\Programs\Python\Python310`

### Issue 2: "pip not recognized"

**Solution:**
```powershell
python -m pip install --upgrade pip
```

### Issue 3: "CUDA not available"

**Solution:**
1. Check NVIDIA driver: `nvidia-smi`
2. Reinstall PyTorch with CUDA:
   ```powershell
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

### Issue 4: "Access Denied" when installing

**Solution:**
Run PowerShell as Administrator:
- Right-click PowerShell → "Run as Administrator"

### Issue 5: Scripts disabled

**Error:** `cannot be loaded because running scripts is disabled`

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 6: Port already in use

**Error:** `Address already in use: 8080`

**Solution:**
```powershell
# Find process using port
netstat -ano | findstr :8080

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn apis.mock_apis:app --port 8081
```

### Issue 7: Out of Memory

**Error:** `CUDA out of memory`

**Solution:**
1. Close other GPU apps (Chrome, games, etc.)
2. Reduce batch size in `training/train_grpo.py`:
   ```python
   per_device_train_batch_size=1
   gradient_accumulation_steps=8
   ```

## 📁 File Locations

```
C:\Users\YOUR_USERNAME\
├── Downloads\civicmind\          # Your project folder
│   ├── venv\                     # Virtual environment
│   ├── training\
│   │   ├── checkpoints\          # Trained models
│   │   └── civicmind_dataset.jsonl
│   ├── evaluation\               # Results
│   └── logs\                     # Log files
```

## 🎯 Recommended Workflow

### First Time Setup
1. Install Python 3.10+
2. Install NVIDIA drivers
3. Clone/download CivicMind
4. Create venv: `python -m venv venv`
5. Activate: `venv\Scripts\activate`
6. Install: `pip install -r requirements.txt`
7. Verify: `python verify_setup.py`

### Daily Development
1. Open PowerShell in project folder
2. Activate venv: `venv\Scripts\activate`
3. Run commands: `run_local.bat eval`
4. Deactivate when done: `deactivate`

### Training Session
1. Close other GPU apps
2. Activate venv: `venv\Scripts\activate`
3. Train: `run_local.bat train`
4. Wait ~45 minutes
5. Evaluate: `python evaluate.py --mode full`

## 🔧 Performance Tips

### 1. GPU Performance Mode

NVIDIA Control Panel → Manage 3D Settings → Power Management Mode → "Prefer Maximum Performance"

### 2. Disable Windows Game Bar

Settings → Gaming → Game Bar → Off

### 3. Close Background Apps

- Chrome (uses GPU)
- Discord (uses GPU)
- Games
- Video players

### 4. Monitor GPU

Keep `nvidia-smi -l 1` running in another window to watch GPU usage.

### 5. Temperature

Keep GPU below 85°C. If higher:
- Clean dust from PC
- Improve case airflow
- Reduce room temperature

## 📊 Expected Performance (RTX 3060)

| Task | Time | VRAM | GPU % |
|------|------|------|-------|
| Demo (eval) | 2 min | 2 GB | 60% |
| Training (2 epochs) | 45 min | 11 GB | 95% |
| Dashboard | instant | 1 GB | 20% |
| API server | instant | 0.5 GB | 5% |

## 🎮 GPU Optimization

### For RTX 3060 (12GB)
```python
# training/train_grpo.py
per_device_train_batch_size=1
gradient_accumulation_steps=4
```

### For RTX 3070/3080 (8-10GB)
```python
per_device_train_batch_size=1
gradient_accumulation_steps=8
```

### For RTX 3090/4090 (24GB)
```python
per_device_train_batch_size=2
gradient_accumulation_steps=2
```

## 🚀 Quick Commands Reference

```powershell
# Activate environment
venv\Scripts\activate

# Check GPU
python check_gpu.py

# Verify setup
python verify_setup.py

# Run demo
run_local.bat eval

# Train model
run_local.bat train

# Launch dashboard
run_local.bat dashboard

# Full stack
run_local.bat all

# Deactivate environment
deactivate
```

## 📞 Getting Help

1. Check `verify_setup.py` output
2. Check `check_gpu.py` output
3. Read error messages carefully
4. Check this troubleshooting section
5. Open issue on GitHub with:
   - Windows version
   - GPU model
   - Error message
   - Output of `python verify_setup.py`

## ✅ Final Checklist

Before training:
- [ ] `nvidia-smi` shows your GPU
- [ ] `python --version` shows 3.10+
- [ ] Virtual environment activated
- [ ] `python verify_setup.py` passes
- [ ] `python check_gpu.py` shows GPU ready
- [ ] Other GPU apps closed
- [ ] 10GB+ free disk space

Ready to go! Run `run_local.bat train` to start training on your GPU.

---

**Windows + NVIDIA GPU = Perfect for CivicMind** 🪟🎮
