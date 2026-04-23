# 🚀 DEPLOY TO HUGGING FACE SPACES - QUICK GUIDE

**CRITICAL**: The official hackathon guide emphasizes HF Spaces deployment multiple times!

---

## 🎯 WHY THIS MATTERS

**From Official Guide**:
> "OpenEnv environments are designed to be deployed as Hugging Face Spaces, which provide: a running server, a Git repository, and a container registry."

> "A good habit is to deploy an early version of the environment before training seriously."

**For Judges**: They expect to see your environment deployed and accessible!

---

## ⚡ QUICK DEPLOYMENT (30 MINUTES)

### Option 1: Deploy Ultimate Demo (EASIEST)

**What**: Deploy your Streamlit ultimate demo as a Space

**Steps**:

1. **Create HF Space**:
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Name: `civicmind-demo`
   - SDK: Streamlit
   - Hardware: CPU (free) or GPU (if available)

2. **Upload Files**:
   ```bash
   # Clone the Space repo
   git clone https://huggingface.co/spaces/YOUR_USERNAME/civicmind-demo
   cd civicmind-demo
   
   # Copy your files
   cp -r /path/to/civicmind/demo ./
   cp -r /path/to/civicmind/core ./
   cp -r /path/to/civicmind/agents ./
   cp -r /path/to/civicmind/environment ./
   cp -r /path/to/civicmind/training/checkpoints ./checkpoints
   cp /path/to/civicmind/requirements.txt ./
   
   # Create app.py (entry point)
   echo "import sys; sys.path.insert(0, '.')" > app.py
   echo "from demo.ultimate_demo import *" >> app.py
   
   # Push to HF
   git add .
   git commit -m "Deploy CivicMind ultimate demo"
   git push
   ```

3. **Wait for Build** (5-10 minutes)

4. **Test**: Visit `https://huggingface.co/spaces/YOUR_USERNAME/civicmind-demo`

**Time**: 30 minutes  
**Difficulty**: Easy  
**Priority**: 🔥🔥🔥🔥🔥 CRITICAL

---

### Option 2: Deploy FastAPI Environment (RECOMMENDED FOR JUDGES)

**What**: Deploy your OpenEnv-compliant environment as an API

**Steps**:

1. **Create HF Space**:
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Name: `civicmind-env`
   - SDK: Docker
   - Hardware: CPU (free)

2. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.10-slim
   
   WORKDIR /app
   
   # Copy files
   COPY requirements.txt .
   COPY environment ./environment
   COPY agents ./agents
   COPY core ./core
   COPY apis ./apis
   COPY rewards ./rewards
   
   # Install dependencies
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Expose port
   EXPOSE 7860
   
   # Run FastAPI
   CMD ["uvicorn", "apis.mock_apis:app", "--host", "0.0.0.0", "--port", "7860"]
   ```

3. **Upload Files**:
   ```bash
   # Clone the Space repo
   git clone https://huggingface.co/spaces/YOUR_USERNAME/civicmind-env
   cd civicmind-env
   
   # Copy your files
   cp -r /path/to/civicmind/environment ./
   cp -r /path/to/civicmind/agents ./
   cp -r /path/to/civicmind/core ./
   cp -r /path/to/civicmind/apis ./
   cp -r /path/to/civicmind/rewards ./
   cp /path/to/civicmind/requirements.txt ./
   cp /path/to/civicmind/Dockerfile ./
   
   # Create README
   cat > README.md << 'EOF'
   ---
   title: CivicMind Environment
   emoji: 🏛️
   colorFrom: blue
   colorTo: purple
   sdk: docker
   pinned: false
   ---
   
   # CivicMind - OpenEnv RL Environment
   
   OpenEnv-compliant environment for civic governance RL training.
   
   ## API Endpoints
   
   - `GET /` - Health check
   - `POST /reset` - Reset environment
   - `POST /step` - Take action
   - `GET /state` - Get current state
   
   ## Usage
   
   ```python
   import requests
   
   # Reset
   response = requests.post("https://huggingface.co/spaces/YOUR_USERNAME/civicmind-env/reset")
   state = response.json()
   
   # Step
   response = requests.post("https://huggingface.co/spaces/YOUR_USERNAME/civicmind-env/step", 
                           json={"action": "invest_in_welfare"})
   next_state = response.json()
   ```
   EOF
   
   # Push to HF
   git add .
   git commit -m "Deploy CivicMind OpenEnv environment"
   git push
   ```

4. **Wait for Build** (10-15 minutes)

5. **Test**:
   ```bash
   curl https://huggingface.co/spaces/YOUR_USERNAME/civicmind-env/
   ```

**Time**: 1 hour  
**Difficulty**: Medium  
**Priority**: 🔥🔥🔥🔥 HIGH

---

### Option 3: Deploy Both (BEST FOR HACKATHON)

**What**: Deploy both demo and environment

**Steps**:
1. Follow Option 1 for demo
2. Follow Option 2 for environment
3. Link them in your README

**Time**: 1.5 hours  
**Difficulty**: Medium  
**Priority**: 🔥🔥🔥🔥🔥 IDEAL

---

## 📝 WHAT TO ADD TO YOUR README

After deployment, update your main README.md:

```markdown
## 🚀 Live Demo

### Interactive Demo
Try CivicMind live: https://huggingface.co/spaces/YOUR_USERNAME/civicmind-demo

### OpenEnv API
Access the environment API: https://huggingface.co/spaces/YOUR_USERNAME/civicmind-env

### Usage Example

```python
import requests

# Connect to deployed environment
base_url = "https://huggingface.co/spaces/YOUR_USERNAME/civicmind-env"

# Reset environment
response = requests.post(f"{base_url}/reset")
state = response.json()

# Take action
response = requests.post(f"{base_url}/step", 
                        json={"action": "invest_in_welfare", "agent_id": "mayor"})
next_state, reward, done = response.json()

print(f"Reward: {reward}")
```

## 🏗️ Architecture

```
User → HF Space (Demo) → Local/Remote Environment
                      ↓
                  FastAPI Backend (HF Space)
                      ↓
                  CivicMindEnv (OpenEnv)
                      ↓
                  Reward Model
```
```

---

## 🎤 WHAT TO SAY TO JUDGES

### Before Deployment:
> "CivicMind is OpenEnv-compliant and ready for deployment to Hugging Face Spaces."

### After Deployment:
> "CivicMind is deployed on Hugging Face Spaces. You can try the live demo at [URL] or access the environment API at [URL]. The environment follows OpenEnv spec with reset(), step(), and reward methods."

**Impact**: 🔥🔥🔥🔥🔥 MASSIVE (judges expect this!)

---

## ⚠️ TROUBLESHOOTING

### Build Fails:
1. Check requirements.txt has all dependencies
2. Verify Python version (3.10 recommended)
3. Check logs in HF Space settings

### Demo Doesn't Load:
1. Verify app.py entry point is correct
2. Check file paths are relative
3. Ensure all imports work

### API Returns Errors:
1. Test locally first: `uvicorn apis.mock_apis:app --port 8080`
2. Check FastAPI routes are correct
3. Verify environment reset/step work

---

## 🚀 MINIMAL DEPLOYMENT (15 MINUTES)

**If you're short on time**, do this:

1. **Create Space**:
   - Name: `civicmind-demo`
   - SDK: Streamlit
   - Hardware: CPU

2. **Upload 3 Files**:
   - `app.py` (your ultimate demo)
   - `requirements.txt`
   - `README.md` (with description)

3. **Push**:
   ```bash
   git add .
   git commit -m "Deploy demo"
   git push
   ```

**Done!** You now have a deployed demo.

---

## 📊 DEPLOYMENT CHECKLIST

### Before Demo Day:
- [ ] Create HF Space for demo
- [ ] Upload all necessary files
- [ ] Test Space loads correctly
- [ ] Add Space URL to README
- [ ] Test Space on mobile (judges may check)
- [ ] Create backup: download Space as ZIP

### Optional (If Time):
- [ ] Create HF Space for environment API
- [ ] Test API endpoints work
- [ ] Add API documentation
- [ ] Create usage examples

### For Demo:
- [ ] Have Space URL ready to show
- [ ] Test Space works on venue WiFi
- [ ] Have backup: local demo if Space is slow

---

## 🏆 WHY THIS MATTERS FOR WINNING

**From Official Guide**:
> "The strongest hackathon projects usually show: a clear environment design, objective reward functions, evidence that the model improved, prevention against reward hacking, **a reproducible deployment story**, and a sharp demo."

**Deployment = Reproducible Deployment Story**

**Judges will ask**:
- "Can I try this?" → YES (HF Space URL)
- "Can I use this environment?" → YES (API endpoint)
- "Is this production-ready?" → YES (deployed and working)

**Without deployment**: "Good project" (7/10)  
**With deployment**: "Production-ready system" (9/10)

---

## 🎯 FINAL RECOMMENDATION

### MINIMUM (Must Do):
- ✅ Deploy ultimate demo to HF Spaces (30 min)
- ✅ Add Space URL to README (5 min)
- ✅ Test Space works (5 min)

**Total**: 40 minutes

### IDEAL (If Time):
- ✅ Deploy demo to HF Spaces (30 min)
- ✅ Deploy environment API to HF Spaces (1 hour)
- ✅ Add both URLs to README (10 min)
- ✅ Test both work (10 min)
- ✅ Create usage examples (10 min)

**Total**: 2 hours

---

## 📞 QUICK COMMANDS

### Deploy Demo:
```bash
# Create Space on HF website first, then:
git clone https://huggingface.co/spaces/YOUR_USERNAME/civicmind-demo
cd civicmind-demo
cp -r /path/to/civicmind/* ./
git add .
git commit -m "Deploy CivicMind"
git push
```

### Test Locally First:
```bash
# Test Streamlit demo
streamlit run demo/ultimate_demo.py

# Test FastAPI
uvicorn apis.mock_apis:app --port 8080
```

---

## 💡 PRO TIP

**Deploy tonight (April 25 evening)**, not on demo day morning!

**Why**:
- Builds take 10-15 minutes
- May need debugging
- Venue WiFi may be slow
- Reduces stress on demo day

**Timeline**:
- 7:00 PM: Start deployment
- 7:30 PM: Space building
- 7:45 PM: Test and verify
- 8:00 PM: Done! Rest easy.

---

*Deploy to HF Spaces Guide*  
*Priority: CRITICAL*  
*Time: 30 min (minimum) to 2 hours (ideal)*  
*🚀 DO THIS BEFORE DEMO DAY! 🚀*
