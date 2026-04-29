@echo off
cd C:\Users\adamh\.openclaw\workspace\earnings-push
echo Current branch and status:
git branch --show-current
echo.
echo Last 3 commits:
git log --oneline -3
echo.
echo Pushing to GitHub...
git push origin main -v
echo Push complete!