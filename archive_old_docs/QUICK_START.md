# ⚡ CivicMind — 5-Minute Quick Start

Get CivicMind running locally in 5 minutes.

## Prerequisites

- Python 3.10+
- GPU with 12GB+ VRAM (or use CPU mode for demo only)
- 10GB free disk space

## Installation

```bash
# 1. Clone repo
git clone https://github.com/YOUR_USERNAME/civicmind.git
cd civicmind

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}')"
```

## Run Demo (No Training)

```bash
# Option 1: Quick evaluation (heuristic vs random)
python evaluate.py --mode compare --n_episodes 1

# Option 2: Interactive dashboard
streamlit run demo/dashboard.py
```

## Train Model (Requires GPU)

```bash
# Generate dataset + train (takes ~30 min on RTX 4090)
./run_local.sh train

# Or step-by-step:
python training/data_generator.py --n_samples 500
python training/train_grpo.py --mode train --epochs 2
```

## Full Stack (API + Dashboard)

```bash
# Start everything
./run_local.sh all

# Or with Docker
docker-compose up -d
```

Open:
- API docs: http://localhost:8080/docs
- Dashboard: http://localhost:8501

## What to Try

1. **See the rebel spawn:**
   ```bash
   python evaluate.py --mode compare --n_episodes 3 --difficulty 5
   ```
   Higher difficulty = more likely to trigger rebel agent

2. **Watch schema drift:**
   ```bash
   python -c "from environment.citizen_engine import CitizenEngine; from environment.city_state import CityState; ce = CitizenEngine(schema_drift=True); ce.reset(); city = CityState(); city.reset(); [print(f'Week {w}: {ce.generate_petitions(w, city)[0][\"schema_version\"]}') for w in [1, 7, 12, 20, 35]]"
   ```

3. **Test API endpoints:**
   ```bash
   # Start API
   uvicorn apis.mock_apis:app --port 8080 &
   
   # Test
   curl http://localhost:8080/health
   curl http://localhost:8080/city/status
   ```

## Next Steps

- **Train locally:** See `TRAINING_GUIDE.md`
- **Deploy:** See `README.md` Docker section
- **Customize:** Edit `environment/civic_env.py` config

## Troubleshooting

**No GPU detected:**
```bash
# CPU-only mode (slow, demo only)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**Import errors:**
```bash
pip install -e .  # Install as package
```

**Port already in use:**
```bash
# Change ports in run_local.sh or use:
uvicorn apis.mock_apis:app --port 8081
streamlit run demo/dashboard.py --server.port 8502
```

## Questions?

Check the full README.md or open an issue on GitHub.
