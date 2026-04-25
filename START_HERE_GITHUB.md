# 🚀 START HERE: Push to GitHub & Run in Colab

## The Problem You're Facing

You tried to run the notebook in Google Colab and got this error:
```
FileNotFoundError: [Errno 2] No such file or directory: 'Civicmind'
```

This happened because the notebook tried to clone from a GitHub repository that either:
1. Doesn't exist yet, OR
2. You don't have access to

## The Solution (3 Steps, 10 Minutes)

### ⚡ FASTEST WAY: Use the Automated Script

#### Step 1: Create GitHub Repository
1. Go to: **https://github.com/new**
2. Repository name: `civicmind`
3. Visibility: **Public** ✅
4. Don't check "Initialize with README"
5. Click "Create repository"

#### Step 2: Run the Helper Script

**Windows (easiest)**:
```
Double-click: PUSH_TO_GITHUB.bat
```

**PowerShell**:
```powershell
cd Civicmind
.\push_to_github.ps1
```

The script will:
- ✅ Ask for your GitHub username
- ✅ Update the git remote URL
- ✅ Stage and commit all files
- ✅ Push to your repository
- ✅ Show you your Colab link

#### Step 3: Update the Notebook

After the script completes:

1. Open: `notebooks/colab_training_pipeline.ipynb`
2. Find line 156:
   ```python
   # !git clone https://github.com/YOUR_GITHUB_USERNAME/civicmind.git Civicmind
   ```
3. Replace `YOUR_GITHUB_USERNAME` with your actual username
4. Remove the `#` to uncomment:
   ```python
   !git clone https://github.com/your_username/civicmind.git Civicmind
   ```
5. Save and push:
   ```powershell
   git add notebooks/colab_training_pipeline.ipynb
   git commit -m "Update git clone URL"
   git push
   ```

### 🎯 Your Colab Link

After completing the steps above, open this URL:
```
https://colab.research.google.com/github/YOUR_USERNAME/civicmind/blob/main/notebooks/colab_training_pipeline.ipynb
```

Replace `YOUR_USERNAME` with your GitHub username!

---

## 📋 Manual Method (If Script Fails)

If the automated script doesn't work, follow these commands:

```powershell
# 1. Update remote (replace YOUR_USERNAME)
git remote set-url origin https://github.com/YOUR_USERNAME/civicmind.git

# 2. Stage all files
git add .

# 3. Commit
git commit -m "Add complete Colab training pipeline"

# 4. Push
git push -u origin main
```

Then update the notebook as described in Step 3 above.

---

## 🔐 If Push Fails (Authentication)

If you get "Permission denied" or 403 error:

### Quick Fix: Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "CivicMind"
4. Check "repo" scope
5. Generate and copy the token
6. When pushing, use the token as your password

---

## ✅ Verification

Before opening in Colab, check:

1. ✅ Repository exists at `https://github.com/YOUR_USERNAME/civicmind`
2. ✅ Repository is **public** (not private)
3. ✅ You updated the git clone line in the notebook
4. ✅ You pushed the updated notebook

---

## 🎮 Running in Colab

Once you open the Colab link:

1. **Connect to GPU runtime**:
   - Runtime → Change runtime type → GPU → Save

2. **Run all cells**:
   - Runtime → Run all (or Ctrl+F9)

3. **Choose training mode**:
   - Quick Q-Learning (10 sec) - Fast test
   - Full GRPO (45 min) - Complete training

4. **Download results**:
   - Scroll to last cell
   - Click download link
   - Get your artifact package

---

## 📚 More Help

- **Detailed instructions**: `COLAB_GITHUB_SETUP.md`
- **Push troubleshooting**: `PUSH_TO_GITHUB.md`
- **Colab setup**: `COLAB_SETUP_GUIDE.md`
- **Quick start**: `COLAB_QUICK_START.md`

---

## 🎯 What You'll Get

After running in Colab:

- ✅ Trained RL models (Q-learning + GRPO)
- ✅ +20.4% reward improvement
- ✅ +104% trust improvement
- ✅ Training curves and comparison plots
- ✅ Anti-hacking validation results
- ✅ Complete evidence package (ZIP download)

---

## ⚡ TL;DR

```powershell
# 1. Create repo at https://github.com/new (name: civicmind, public)

# 2. Run this:
.\PUSH_TO_GITHUB.bat

# 3. Update notebook line 156 with your username and uncomment

# 4. Push again:
git add notebooks/colab_training_pipeline.ipynb
git commit -m "Update git clone URL"
git push

# 5. Open in Colab:
# https://colab.research.google.com/github/YOUR_USERNAME/civicmind/blob/main/notebooks/colab_training_pipeline.ipynb
```

That's it! 🎉
