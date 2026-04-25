@echo off
echo.
echo DigitalOcean Deployment Script
echo ==============================
echo.
echo You need to paste your API token when prompted.
echo.
set /p token="Paste your DigitalOcean API token here: "
echo.
echo Authenticating...
C:\Users\adamh\AppData\Local\Microsoft\WinGet\Packages\DigitalOcean.Doctl_Microsoft.Winget.Source_8wekyb3d8bbwe\doctl.exe auth init --access-token %token%
echo.
echo Deploying your app...
C:\Users\adamh\AppData\Local\Microsoft\WinGet\Packages\DigitalOcean.Doctl_Microsoft.Winget.Source_8wekyb3d8bbwe\doctl.exe apps create --spec .do/app.yaml
echo.
echo Deployment complete! Check https://cloud.digitalocean.com/apps
echo.
pause