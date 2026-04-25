@echo off
REM CivicMind - Reproduce Results (Windows)
REM Run this to regenerate all evidence

echo ================================================================================
echo CIVICMIND - REPRODUCING RESULTS
echo ================================================================================
echo.

echo [1/3] Running Model vs Baseline Comparison...
python evaluation/model_vs_baseline.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Model comparison failed
    exit /b 1
)
echo.

echo [2/3] Generating Plots...
python evaluation/plot_results.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Plot generation failed
    exit /b 1
)
echo.

echo [3/3] Running Anti-Hacking Validation...
python evaluation/anti_hacking_validation.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Anti-hacking validation failed
    exit /b 1
)
echo.

echo ================================================================================
echo SUCCESS! All evidence regenerated
echo ================================================================================
echo.
echo Results location:
echo   - evidence/eval/model_vs_baseline.json
echo   - evidence/plots/*.png
echo   - evidence/eval/anti_hacking_validation.json
echo.
echo ================================================================================
