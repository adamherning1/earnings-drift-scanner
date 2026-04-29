@echo off
cd C:\Users\adamh\.openclaw\workspace\earnings-push
echo Checking current status...
git status
echo.
echo Pushing to earnings remote on main branch...
git push earnings main
echo Done!