@echo off
echo Enter your GitHub personal access token:
set /p token=
git push https://%token%@github.com/adamherning1/earnings-drift-scanner.git main
echo.
echo Fix pushed! DigitalOcean will automatically rebuild.
pause