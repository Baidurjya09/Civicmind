# 🚀 DEPLOYMENT STEPS - DO THIS AFTER TRAINING

**Current Status:** Training at 13% (~25 min remaining)

---

## STEP 1: Upload Colab Notebook (~5 min)

### Option A: Google Colab (Recommended)
1. Go to https://colab.research.google.com/
2. Click "File" → "Upload notebook"
3. Upload `CivicMind_Training.ipynb`
4. Click "Share" → "Get link" → "Anyone with the link can view"
5. Copy the URL (format: `https://colab.research.google.com/drive/...`)

### Option B: HuggingFace Space
1. Upload `CivicMind_Training.ipynb` to your HF Space repo
2. URL will be: `https://huggingface.co/spaces/YOUR_USERNAME/civicmind/blob/main/CivicMind_Training.ipynb`

**Save this URL for submission form!**

---

## STEP 2: Deploy HuggingFace Space (~10 min)

### 2.1 Create Space
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Name: `civicmind`
4. License: MIT
5. SDK: Docker
6. Click "Create Space"

### 2.2 Upload Files
Upload these files to your Space:

**Required Files:**
```
app.py
Dockerfile.space
requirements_hf.txt
README_SPACE.md
BLOG_POST_FINAL.md
openenv.yaml
setup.py
```

**Required Folders:**
```
environment/
agents/
rewards/
core/
utils/
apis/
```

**Optional (for demo):**
```
training/checkpoints/llm_agent_elite/  (if you want live model)
train_result/plots/  (for embedded images)
```

### 2.3 Configure Space
1. Rename `Dockerfile.space` to `Dockerfile`
2. Rename `README_SPACE.md` to `README.md`
3. Wait for build (5-10 minutes)
4. Test in incognito browser

**Your Space URL:** `https://huggingface.co/spaces/YOUR_USERNAME/civicmind`

**Save this URL for submission form!**

---

## STEP 3: Update Main README (~5 min)

Add these sections to your main `README.md`:

```markdown
## 🚀 Quick Links

- **[🎮 Live Demo on HuggingFace Space](https://huggingface.co/spaces/YOUR_USERNAME/civicmind)**
- **[📓 Training Notebook (Colab)](YOUR_COLAB_URL)**
- **[📝 Blog Post](https://huggingface.co/spaces/YOUR_USERNAME/civicmind/blob/main/BLOG_POST_FINAL.md)**
- **[📦 GitHub Repository](https://github.com/YOUR_USERNAME/civicmind)**

## 📊 Training Results

![Loss Curve](train_result/plots/loss_curve.png)
![Agent Diversity](train_result/plots/agent_diversity.png)
![GRPO Training](train_result/plots/grpo_training.png)

### Key Metrics
- **SFT Loss Reduction:** 96.2% (2.62 → 0.10)
- **Agent Diversity:** 87.4% active governance
- **Q-Learning Improvement:** +18.4% reward
- **Training Time:** 37.6 minutes (SFT) + 15 minutes (GRPO)
```

---

## STEP 4: Clean Repository (~5 min)

```bash
python cleanup_for_submission.py
```

This removes 100+ unnecessary files.

---

## STEP 5: Final Verification (~10 min)

### Test Checklist:
- [ ] Open HF Space in incognito browser - does it load?
- [ ] Click Colab notebook link - does it open?
- [ ] Click blog post link - is it accessible?
- [ ] Check README - are all links working?
- [ ] Run environment locally - no errors?
- [ ] Check plots - do they display?

---

## STEP 6: Submit Form (~2 min)

Go to submission form and fill in:

```
Email: baidujyabastavhazarika@gmail.com

Hugging Face Space URL:
https://huggingface.co/spaces/YOUR_USERNAME/civicmind

Training Run Notebook URL:
[Your Google Colab URL from Step 1]

Choose: Blog Post

Blog Post URL:
https://huggingface.co/spaces/YOUR_USERNAME/civicmind/blob/main/BLOG_POST_FINAL.md
```

**DOUBLE CHECK:**
- All URLs are public
- Test each URL in incognito browser
- No typos in URLs

---

## ⏰ TIMELINE

| Step | Time | When |
|------|------|------|
| Wait for training | 25 min | Now |
| Upload Colab | 5 min | After training |
| Deploy HF Space | 10 min | After training |
| Update README | 5 min | After HF Space |
| Clean repo | 5 min | After README |
| Verify everything | 10 min | Before submit |
| Submit form | 2 min | Final step |
| **TOTAL** | **62 min** | After training |

---

## 🚨 IMPORTANT REMINDERS

1. **Test in incognito** - Judges will check
2. **All links must work** - Broken links = lost points
3. **HF Space must load** - This is your demo
4. **Colab must run** - Judges will test it
5. **Blog must be accessible** - Not just in your local files
6. **Submit before 5 PM IST** - No extensions

---

## ✅ READY?

After training completes:
1. Upload Colab notebook → Get URL
2. Deploy HF Space → Get URL
3. Update README with both URLs
4. Clean repository
5. Verify everything works
6. Submit form with all URLs

**YOU GOT THIS! 🚀**
