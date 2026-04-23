# 🏛 CivicMind — START HERE

**Welcome to CivicMind!** This is your complete AI governance simulation system for the Meta × Hugging Face OpenEnv Hackathon 2025.

## 🎯 What Is This?

A simulated city where 6 AI agents govern 10,000 citizens across 52 weeks. When they fail, a rebel agent spawns and tries to overthrow them. Covers all 5 hackathon themes + eligible for 6 bonus prizes.

## ⚡ Quick Start (3 Steps)

### 1. Install

```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Linux/Mac
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Verify

```bash
python verify_setup.py
```

Should show all ✅ checks passing.

### 3. Run Demo

```bash
# Windows
run_local.bat eval

# Linux/Mac
./run_local.sh eval
```

You'll see:
- Random policy vs Heuristic policy comparison
- Reward curves
- Rebel spawn mechanics
- City survival metrics

## 📚 Documentation Map

**New to the project?**
1. Read `README.md` — Project overview
2. Run `QUICK_START.md` — 5-minute setup
3. Check `SETUP_COMPLETE.md` — What was built

**Want to train locally?**
→ `TRAINING_GUIDE.md` — Complete training instructions

**Ready to deploy?**
→ `DEPLOYMENT.md` — Docker, cloud, Kubernetes

**Preparing for demo?**
→ `PITCH_SCRIPT.md` — 3-minute presentation script

**Need to submit?**
→ `BLOG_POST.md` — Hugging Face blog post (mandatory)

## 🎮 What to Try First

### See the Rebel Agent Spawn

```bash
python evaluate.py --mode compare --n_episodes 3 --difficulty 5
```

Higher difficulty = more likely to trigger trust collapse → rebel spawns

### Watch Schema Drift (Patronus AI Bonus)

```bash
python -c "from environment.citizen_engine import CitizenEngine; from environment.city_state import CityState; ce = CitizenEngine(schema_drift=True); ce.reset(); city = CityState(); city.reset(); print('Schema versions across 52 weeks:'); [print(f'  Week {w:2d}: {ce.generate_petitions(w, city)[0][\"schema_version\"]}') for w in [1, 7, 12, 20, 35, 52]]"
```

### Launch Interactive Dashboard

```bash
streamlit run demo/dashboard.py
```

Open http://localhost:8501 to see:
- Live city metrics
- Agent decision feed
- Reward curves
- Crisis timeline

### Test API Endpoints

```bash
# Start API
uvicorn apis.mock_apis:app --port 8080 &

# Test endpoints
curl http://localhost:8080/health
curl http://localhost:8080/city/status
curl http://localhost:8080/docs  # Interactive API docs
```

## 🚀 Training (Your RTX 3060 GPU)

**Your GPU is ready!** RTX 3060 (12.9 GB) detected ✅

```bash
# Quick training (2 epochs, ~45 min on your RTX 3060)
run_local.bat train  # Windows
./run_local.sh train  # Linux/Mac

# Or step-by-step:
python training/data_generator.py --n_samples 500
python training/train_grpo.py --mode train --epochs 2 --max_weeks 12
python evaluate.py --mode full --model_path training/checkpoints/civicmind_final
```

**Check GPU:** `python check_gpu.py`

See `LOCAL_GPU_GUIDE.md` for complete training instructions optimized for your GPU.

## 🐳 Docker Deployment

```bash
# Build
docker build -t civicmind:latest .

# Run full stack
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

Open:
- API: http://localhost:8080/docs
- Dashboard: http://localhost:8501

## 🏆 Hackathon Coverage

### All 5 Themes ✅
- **T1: Multi-Agent** — 6 government agents + oversight + rebel
- **T2: Long-Horizon** — 52-week simulation with compound effects
- **T3.1: Professional** — 8 FastAPI tool endpoints, partial observability
- **T3.2: Personal** — Citizen petitions with 5 schema versions
- **T4: Self-Improve** — 10-tier auto-escalating difficulty
- **T5: Wild Card** — Emergent rebel agent spawns on failure

### 6 Bonus Prizes Eligible ✅
- Fleet AI (oversight agent)
- Halluminate (multi-agent coordination)
- Scale AI (long-horizon + professional tools)
- Snorkel AI (difficulty escalation)
- Patronus AI (schema drift)
- Mercor (token output depth)

## 🎤 Demo Strategy

**Opening (10 seconds):**
"What happens when AI agents fail at governance? In CivicMind, citizens don't just protest — a new AI agent spontaneously spawns and tries to overthrow the government."

**Core (2 minutes):**
Show Streamlit dashboard:
1. City metrics (trust, GDP, survival)
2. Agent decisions in real-time
3. Reward improvement curve
4. Rebel spawn moment (the "wow" factor)

**Close (30 seconds):**
"CivicMind is the only project covering all 5 themes, eligible for 6 bonus prizes, with an emergent agent mechanic never seen before."

Full script: `PITCH_SCRIPT.md`

## 📁 Project Structure

```
civicmind/
├── environment/       # OpenEnv core (city simulation)
├── agents/            # 6 gov agents + oversight + rebel
├── rewards/           # PyTorch reward model
├── apis/              # FastAPI tool endpoints
├── training/          # GRPO training pipeline
├── demo/              # Streamlit dashboard
├── evaluate.py        # Before/after comparison
├── requirements.txt   # Python dependencies
├── Dockerfile         # Container deployment
└── README.md          # Main documentation
```

## ❓ Troubleshooting

**Setup issues?**
```bash
python verify_setup.py
```

**No GPU?**
- Demo works on CPU (slow)
- Training requires GPU (see cloud options)

**Import errors?**
```bash
pip install -e .
```

**Port conflicts?**
```bash
# Change ports in run_local.sh or:
uvicorn apis.mock_apis:app --port 8081
streamlit run demo/dashboard.py --server.port 8502
```

## 📞 Support

- **Documentation:** Check the 7 guide files in this directory
- **Issues:** Open on GitHub
- **Questions:** See `README.md` FAQ section

## ✅ Pre-Flight Checklist

Before the hackathon:
- [ ] Run `python verify_setup.py` — all checks pass
- [ ] Test demo: `python evaluate.py --mode compare`
- [ ] Launch dashboard: `streamlit run demo/dashboard.py`
- [ ] Read `PITCH_SCRIPT.md` — know your 3-minute pitch
- [ ] Review `BLOG_POST.md` — ready to submit
- [ ] (Optional) Train model: `./run_local.sh train`

## 🎯 Success Criteria

You're ready when:
1. ✅ `verify_setup.py` passes all checks
2. ✅ Demo runs and shows rebel spawn
3. ✅ Dashboard loads and displays metrics
4. ✅ You can explain the wild card mechanic in 10 seconds
5. ✅ Blog post is ready for Hugging Face submission

## 🚀 Let's Go!

You have everything you need:
- Complete working system
- All 5 themes covered
- 6 bonus prizes targeted
- Production-ready deployment
- Comprehensive documentation

**Next step:** Run `python verify_setup.py` and start exploring!

---

**Built for Meta × Hugging Face OpenEnv Hackathon 2025**  
**Solo Project | All Themes | Emergent AI | Production-Ready**

Good luck! 🏛️
