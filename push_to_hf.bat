@echo off
echo ========================================
echo PUSHING TO HUGGINGFACE SPACE
echo ========================================
echo.
echo This will push your code to:
echo https://huggingface.co/spaces/baidurjya09/Civicmind
echo.
echo You may be asked for credentials:
echo Username: baidurjya09
echo Password: [Your HuggingFace Token]
echo.
echo Get token from: https://huggingface.co/settings/tokens
echo.
pause

git push hf main --force

echo.
echo ========================================
echo DONE!
echo ========================================
echo.
echo Check your space at:
echo https://huggingface.co/spaces/baidurjya09/Civicmind
echo.
pause
