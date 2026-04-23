@echo off
REM CivicMind — Local Development Runner (Windows)
REM Usage: run_local.bat [train|eval|api|dashboard|all]

setlocal enabledelayedexpansion

set MODE=%1
if "%MODE%"=="" set MODE=all

echo 🏛 CivicMind — Local Runner
echo Mode: %MODE%
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

if "%MODE%"=="train" (
    echo 📊 Generating training dataset...
    python training\data_generator.py --n_samples 500
    
    echo.
    echo 🚀 Starting GRPO training...
    python training\train_grpo.py --mode train --epochs 2 --max_weeks 12
    goto :end
)

if "%MODE%"=="eval" (
    echo 📈 Running evaluation...
    python evaluate.py --mode compare --n_episodes 3 --difficulty 3
    goto :end
)

if "%MODE%"=="api" (
    echo 🌐 Starting API server on port 8080...
    uvicorn apis.mock_apis:app --host 0.0.0.0 --port 8080 --reload
    goto :end
)

if "%MODE%"=="dashboard" (
    echo 📊 Starting Streamlit dashboard on port 8501...
    streamlit run demo\dashboard.py
    goto :end
)

if "%MODE%"=="all" (
    echo 🚀 Starting full stack...
    
    echo   [1/3] Starting API server...
    start /B uvicorn apis.mock_apis:app --host 0.0.0.0 --port 8080
    
    timeout /t 3 /nobreak >nul
    
    echo   [2/3] Running quick evaluation...
    python evaluate.py --mode compare --n_episodes 1 --difficulty 3
    
    echo   [3/3] Starting dashboard...
    start /B streamlit run demo\dashboard.py
    
    echo.
    echo ✅ All services running:
    echo    API:       http://localhost:8080
    echo    Dashboard: http://localhost:8501
    echo.
    echo Press Ctrl+C to stop all services
    
    pause
    goto :end
)

echo ❌ Unknown mode: %MODE%
echo Usage: run_local.bat [train^|eval^|api^|dashboard^|all]
exit /b 1

:end
echo.
echo ✅ Done!
