@echo off
REM CivicMind GitHub Push Helper (Windows Batch Version)
REM Double-click this file to run the push helper

echo.
echo ========================================
echo   CivicMind GitHub Push Helper
echo ========================================
echo.

REM Check if PowerShell is available
where pwsh >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Running with PowerShell Core...
    pwsh -ExecutionPolicy Bypass -File "%~dp0push_to_github.ps1"
) else (
    where powershell >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo Running with Windows PowerShell...
        powershell -ExecutionPolicy Bypass -File "%~dp0push_to_github.ps1"
    ) else (
        echo ERROR: PowerShell not found!
        echo Please install PowerShell or run the commands manually.
        echo See PUSH_TO_GITHUB.md for instructions.
        pause
        exit /b 1
    )
)

echo.
pause
