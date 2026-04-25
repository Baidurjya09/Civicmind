# 🔧 Fix: "FileNotFoundError: No such file or directory: 'Civicmind'"

## Your Error

```
🔍 Detecting runtime environment... 
✅ Running in Google Colab 
📥 Cloning CivicMind repository... 
⚠️  Clone failed: Cloning into 'Civicmind'... 
fatal: could not read Username for 'https://github.com': No such device or address     
Continuing with existing files... 
---------------------------------------------------------------------------
FileNotFoundError: [Errno 2] No such file or directory: 'Civicmind'
```

## What Happened

The notebook tried to clone the CivicMind repository from GitHub, but:
1. The git clone command failed (couldn't authenticate)
2. The `Civicmind` directory doesn't exist in Colab
3. The notebook can't continue without the code

## Root Cause

The git clone line in your notebook is either:
- Pointing to a repository that doesn't exist
- Pointing to a private repository
- Using a placeholder URL that needs to be updated

## ✅ Solution: 3 Options

### Option 1: Push to Your GitHub (Recommended)

This is the best long-term solution. Follow these steps:

#### 1. Create GitHub Repository
- Go to: https://github.com/new
- Name: `civicmind`
- Visibility: **Public** (important!)
- Don't initialize with README
- Click "Create repository"

#### 2. Push Your Code
```powershell
# In the Civicmind directory
cd Civicmind

# Update remote (replace YOUR_USERNAME)
git remote set-url origin https://github.com/YOUR_USERNAME/civicmind.git

# Stage and commit
git add .
git commit -m "Add complete Colab training pipeline"

# Push
git push -u origin main
```

#### 3. Update Notebook
Open `notebooks/colab_training_pipeline.ipynb` and find this line (around line 156):
```python
# !git clone https://github.com/YOUR_GITHUB_USERNAME/civicmind.git Civicmind
```

Change it to (replace with your username):
```python
!git clone https://github.com/your_actual_username/civicmind.git Civicmind
```

#### 4. Push Updated Notebook
```powershell
git add notebooks/colab_training_pipeline.ipynb
git commit -m "Update git clone URL"
git push
```

#### 5. Open in Colab
```
https://colab.research.google.com/github/YOUR_USERNAME/civicmind/blob/main/notebooks/colab_training_pipeline.ipynb
```

---

### Option 2: Upload Files Directly (Quick Fix)

If you don't want to use GitHub:

#### 1. Open Colab
Go to: https://colab.research.google.com/

#### 2. Upload Notebook
- Click "Upload" tab
- Upload `colab_training_pipeline.ipynb`

#### 3. Upload Civicmind Folder
When the notebook runs and asks for files:
- Click the folder icon on the left sidebar
- Click the upload button
- Upload the entire `Civicmind` folder from your computer

#### 4. Run Cells
After upload completes, run all cells.

**Note**: You'll need to re-upload files every time you start a new Colab session.

---

### Option 3: Use Google Drive

Mount your Google Drive and upload files there:

#### 1. Upload to Drive
- Upload the entire `Civicmind` folder to your Google Drive

#### 2. Modify First Cell
In the notebook, replace the first code cell with:
```python
from google.colab import drive
import os

# Mount Google Drive
drive.mount('/content/drive')

# Navigate to your Civicmind folder
os.chdir('/content/drive/MyDrive/Civicmind')

print(f"📂 Current directory: {os.getcwd()}")
```

#### 3. Run Notebook
All files will be loaded from your Google Drive.

---

## 🚀 Automated Helper (Option 1)

To make Option 1 easier, use the automated script:

**Windows**:
```
Double-click: PUSH_TO_GITHUB.bat
```

**PowerShell**:
```powershell
.\push_to_github.ps1
```

The script will:
- Ask for your GitHub username
- Update git remote
- Stage and commit files
- Push to GitHub
- Show you your Colab link

---

## 🔐 Authentication Issues

If `git push` fails with "Permission denied":

### Use Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "CivicMind Push"
4. Check "repo" scope
5. Generate and copy the token
6. When pushing, use the token as your password (not your GitHub password)

---

## ✅ Verification

After fixing, verify:

1. **If using GitHub**:
   - [ ] Repository exists at `https://github.com/YOUR_USERNAME/civicmind`
   - [ ] Repository is public
   - [ ] Git clone line in notebook has your username
   - [ ] Git clone line is uncommented (no `#` at start)

2. **If uploading directly**:
   - [ ] Civicmind folder is uploaded to Colab
   - [ ] All files are present in the folder

3. **Test in Colab**:
   - [ ] First cell runs without errors
   - [ ] Shows "✅ CivicMind repository found"
   - [ ] Can proceed to next cells

---

## 📋 Quick Command Reference

```powershell
# Check current remote
git remote -v

# Update remote to your repo
git remote set-url origin https://github.com/YOUR_USERNAME/civicmind.git

# Stage all files
git add .

# Commit
git commit -m "Add Colab pipeline"

# Push
git push -u origin main

# Check status
git status
```

---

## 🎯 Expected Behavior (After Fix)

When you run the first cell in Colab, you should see:

```
🔍 Detecting runtime environment...
✅ Running in Google Colab
📥 Cloning CivicMind repository...
Cloning into 'Civicmind'...
✅ Repository cloned successfully
📂 Current directory: /content/Civicmind
```

Then the notebook will continue with dependency installation.

---

## 📚 More Resources

- **Complete setup guide**: `COLAB_GITHUB_SETUP.md`
- **Push instructions**: `PUSH_TO_GITHUB.md`
- **Quick start**: `START_HERE_GITHUB.md`
- **Automated script**: `push_to_github.ps1`

---

## 💡 Recommended Approach

**For best results, use Option 1 (GitHub)**:
1. Takes 10 minutes to set up
2. Works permanently (no re-uploading)
3. Easy to share with others
4. Professional workflow
5. Can track changes with git

**Use Option 2 (Direct Upload) only if**:
- You need a quick test
- You don't want to use GitHub
- You're okay re-uploading every session

---

## 🎉 After Fixing

Once the error is fixed, you can:
1. ✅ Run the complete training pipeline in Colab
2. ✅ Train Q-learning models (10 seconds)
3. ✅ Train GRPO models (45 minutes)
4. ✅ Generate evaluation plots
5. ✅ Download complete artifact package

Your notebook will work perfectly! 🚀
