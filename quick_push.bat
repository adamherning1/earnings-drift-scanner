@echo off
echo Paste your GitHub token and press Enter:
set /p token=
git remote set-url origin https://%token%@github.com/adamherning1/earnings-drift-scanner.git
git push origin main
echo.
echo Done! Check your GitHub page to see the files.
pause