@echo off
echo Syncing with GitHub...
echo.
echo Enter your GitHub personal access token:
set /p token=

echo.
echo Pulling latest changes from GitHub...
git pull https://%token%@github.com/adamherning1/earnings-drift-scanner.git main

echo.
echo Pushing your fixes...
git push https://%token%@github.com/adamherning1/earnings-drift-scanner.git main

echo.
echo Done! DigitalOcean will automatically rebuild.
pause