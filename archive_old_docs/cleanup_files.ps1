# Safe Cleanup Script - Move old files to archive

Write-Host "Starting safe cleanup..." -ForegroundColor Green

# Create archive folder if it doesn't exist
if (!(Test-Path "archive_old_docs")) {
    New-Item -ItemType Directory -Path "archive_old_docs" | Out-Null
}

# List of files to move
$filesToMove = @(
    "ACTION_PLAN_NOW.md",
    "ARCHITECTURE.md",
    "BLOG_POST.md",
    "CHECKPOINT_EVERYTHING.md",
    "COMPLETE_SYSTEM_STATUS.md",
    "CONTROL_ROOM_GUIDE.md",
    "CURRENT_STATUS.md",
    "DASHBOARD_GUIDE.md",
    "DEMO_CHEAT_SHEET.md",
    "DEPLOYMENT.md",
    "DO_THIS_NOW.md",
    "DO_THIS_RIGHT_NOW.md",
    "EXECUTIVE_SUMMARY.md",
    "FINAL_PROJECT_STATUS.md",
    "FINAL_SUMMARY.md",
    "FINAL_VERIFICATION.md",
    "FIXED_HTML_CONTROL_ROOM.md",
    "FIXES_APPLIED.md",
    "GRPO_QUICK_START.md",
    "GRPO_READY.md",
    "GRPO_TRAINING_GUIDE.md",
    "HTML_CONTROL_ROOM_GUIDE.md",
    "LOCAL_GPU_GUIDE.md",
    "MASTER_INDEX.md",
    "on 25 n 26.md",
    "PITCH_SCRIPT.md",
    "PROJECT_COMPLETE_DOCUMENTATION.md",
    "PROJECT_COMPLETE_VISUAL.md",
    "QUICK_DEMO_GUIDE.md",
    "QUICK_START.md",
    "READY_TO_WIN.md",
    "RL_CLARITY_FIXES.md",
    "RL_FIXES_COMPLETE.md",
    "RUN_TRAINING.md",
    "SETUP_COMPLETE.md",
    "SHANNON_IMPROVEMENTS_COMPLETE.md",
    "SHANNON_UPGRADE.md",
    "START_HERE_FINAL.md",
    "START_HERE_NOW.md",
    "START_HERE_ULTIMATE.md",
    "START_HERE.md",
    "SYSTEM_ARCHITECTURE_VISUAL.md",
    "SYSTEM_READY.md",
    "TRAINING_FIXED.md",
    "TRAINING_GUIDE.md",
    "TRAINING_IN_PROGRESS.md",
    "ULTIMATE_STATUS_NOW.md",
    "WHAT_YOU_SEE_NOW.md",
    "WINDOWS_SETUP.md",
    "WINNING_STRATEGY.md",
    "YOU_ARE_READY.md",
    "YOUR_GPU_IS_READY.md",
    "test_final_polish.py",
    "test_final_simple.py",
    "test_shannon_improvements.py",
    "quick_demo.py",
    "rebel_agent.py",
    "CivicMind_Colab.py",
    "run_local.bat",
    "run_local.sh",
    "RUN_ULTIMATE_DEMO.bat",
    "verify_setup.py"
)

$movedCount = 0
$notFoundCount = 0

foreach ($file in $filesToMove) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "archive_old_docs/" -Force
        Write-Host "Moved: $file" -ForegroundColor Yellow
        $movedCount++
    } else {
        $notFoundCount++
    }
}

# Move unused demo files
$demoFiles = @(
    "demo/dashboard.py",
    "demo/dashboard_live.py",
    "demo/dashboard_control_room.py",
    "demo/control_room_ultimate.py",
    "demo/shannon_demo.py"
)

foreach ($file in $demoFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "archive_old_docs/" -Force
        Write-Host "Moved: $file" -ForegroundColor Yellow
        $movedCount++
    } else {
        $notFoundCount++
    }
}

Write-Host "`nCleanup complete!" -ForegroundColor Green
Write-Host "Files moved: $movedCount" -ForegroundColor Cyan
Write-Host "Files not found: $notFoundCount" -ForegroundColor Gray
Write-Host "`nOld files are now in: archive_old_docs/" -ForegroundColor Green
Write-Host "You can delete this folder after the hackathon." -ForegroundColor Yellow
