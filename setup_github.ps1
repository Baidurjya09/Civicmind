# GitHub Setup Script for CivicMind Colab Pipeline
# Run this after creating your GitHub repository

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "GITHUB SETUP FOR CIVICMIND COLAB PIPELINE" -ForegroundColor Yellow
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

# Get GitHub username
Write-Host "Enter your GitHub username: " -NoNewline -ForegroundColor Green
$username = Read-Host

if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "Error: Username cannot be empty!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Setting up repository for: $username" -ForegroundColor Cyan
Write-Host ""

# Confirm
Write-Host "This will:" -ForegroundColor Yellow
Write-Host "  1. Change git remote to: https://github.com/$username/civicmind.git" -ForegroundColor White
Write-Host "  2. Push all commits to your repository" -ForegroundColor White
Write-Host ""
Write-Host "Make sure you've created the repository on GitHub first!" -ForegroundColor Yellow
Write-Host "  Go to: https://github.com/new" -ForegroundColor Cyan
Write-Host "  Repository name: civicmind" -ForegroundColor Cyan
Write-Host "  Make it PUBLIC" -ForegroundColor Cyan
Write-Host ""
Write-Host "Continue? (Y/N): " -NoNewline -ForegroundColor Green
$confirm = Read-Host

if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1: Updating git remote..." -ForegroundColor Cyan

# Update remote
git remote set-url origin "https://github.com/$username/civicmind.git"

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Remote updated successfully!" -ForegroundColor Green
} else {
    Write-Host "  ❌ Failed to update remote" -ForegroundColor Red
    exit 1
}

# Verify
Write-Host ""
Write-Host "Step 2: Verifying remote..." -ForegroundColor Cyan
git remote -v

Write-Host ""
Write-Host "Step 3: Pushing to GitHub..." -ForegroundColor Cyan
Write-Host "  (You may need to enter your GitHub credentials)" -ForegroundColor Yellow
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Green
    Write-Host "✅ SUCCESS! Code pushed to GitHub" -ForegroundColor Green
    Write-Host ("=" * 70) -ForegroundColor Green
    Write-Host ""
    Write-Host "Your Colab notebook is now available at:" -ForegroundColor Cyan
    Write-Host "https://colab.research.google.com/github/$username/civicmind/blob/main/notebooks/colab_training_pipeline.ipynb" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Click the link above to open in Colab" -ForegroundColor White
    Write-Host "  2. Enable GPU (Runtime > Change runtime type > T4 GPU)" -ForegroundColor White
    Write-Host "  3. Run all cells (Runtime > Run all)" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Push failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  1. Repository doesn't exist - create it at https://github.com/new" -ForegroundColor White
    Write-Host "  2. Authentication failed - use a Personal Access Token" -ForegroundColor White
    Write-Host "     Go to: GitHub Settings > Developer settings > Personal access tokens" -ForegroundColor Cyan
    Write-Host "     Generate token with 'repo' scope" -ForegroundColor Cyan
    Write-Host "     Use token as password when pushing" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}
