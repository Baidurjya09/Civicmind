#!/usr/bin/env pwsh
# CivicMind GitHub Push Helper Script
# This script helps you push your code to your own GitHub repository

Write-Host "🚀 CivicMind GitHub Push Helper" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "notebooks/colab_training_pipeline.ipynb")) {
    Write-Host "❌ Error: This script must be run from the Civicmind directory" -ForegroundColor Red
    Write-Host "   Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# Get current remote
$currentRemote = git remote get-url origin 2>$null
if ($currentRemote) {
    Write-Host "📍 Current remote: $currentRemote" -ForegroundColor Yellow
    Write-Host ""
}

# Ask for GitHub username
Write-Host "Please enter your GitHub username:" -ForegroundColor Green
$username = Read-Host "GitHub username"

if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "❌ Error: Username cannot be empty" -ForegroundColor Red
    exit 1
}

# Ask for repository name
Write-Host ""
Write-Host "Please enter your repository name (default: civicmind):" -ForegroundColor Green
$repoName = Read-Host "Repository name"

if ([string]::IsNullOrWhiteSpace($repoName)) {
    $repoName = "civicmind"
}

$newRemote = "https://github.com/$username/$repoName.git"

Write-Host ""
Write-Host "📋 Configuration:" -ForegroundColor Cyan
Write-Host "   Username: $username" -ForegroundColor White
Write-Host "   Repository: $repoName" -ForegroundColor White
Write-Host "   Remote URL: $newRemote" -ForegroundColor White
Write-Host ""

# Confirm
Write-Host "Is this correct? (y/n):" -ForegroundColor Green
$confirm = Read-Host

if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "❌ Cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🔧 Step 1: Updating remote URL..." -ForegroundColor Cyan
try {
    git remote set-url origin $newRemote
    Write-Host "✅ Remote URL updated" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to update remote URL: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Step 2: Staging all files..." -ForegroundColor Cyan
try {
    git add .
    $status = git status --short
    $fileCount = ($status | Measure-Object).Count
    Write-Host "✅ Staged $fileCount files" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to stage files: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "💾 Step 3: Committing changes..." -ForegroundColor Cyan
try {
    git commit -m "Add complete Colab training pipeline with GRPO and Q-learning"
    Write-Host "✅ Changes committed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Commit may have failed (this is OK if there are no changes): $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Step 4: Pushing to GitHub..." -ForegroundColor Cyan
Write-Host "   This may take a minute..." -ForegroundColor Yellow
Write-Host ""

try {
    git push -u origin main 2>&1 | ForEach-Object { Write-Host $_ }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎉 Next Steps:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. Update the notebook git clone line:" -ForegroundColor White
        Write-Host "   - Open: notebooks/colab_training_pipeline.ipynb" -ForegroundColor Yellow
        Write-Host "   - Find line: # !git clone https://github.com/YOUR_GITHUB_USERNAME/civicmind.git Civicmind" -ForegroundColor Yellow
        Write-Host "   - Change to: !git clone https://github.com/$username/$repoName.git Civicmind" -ForegroundColor Yellow
        Write-Host "   - Save and push again" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "2. Open in Google Colab:" -ForegroundColor White
        Write-Host "   https://colab.research.google.com/github/$username/$repoName/blob/main/notebooks/colab_training_pipeline.ipynb" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "3. Run all cells in Colab to train your models!" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "❌ Push failed!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Common issues:" -ForegroundColor Yellow
        Write-Host "1. Repository doesn't exist - Create it at: https://github.com/new" -ForegroundColor White
        Write-Host "2. Authentication failed - You may need a Personal Access Token" -ForegroundColor White
        Write-Host "   Get one at: https://github.com/settings/tokens" -ForegroundColor White
        Write-Host "3. Wrong username or repository name" -ForegroundColor White
        Write-Host ""
        Write-Host "See PUSH_TO_GITHUB.md for detailed troubleshooting" -ForegroundColor Cyan
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "❌ Push failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "See PUSH_TO_GITHUB.md for troubleshooting steps" -ForegroundColor Cyan
    exit 1
}
