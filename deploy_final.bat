@echo off
echo Final Deployment to DigitalOcean
echo ================================
echo.
echo Using your existing DigitalOcean token...
echo.
C:\Users\adamh\AppData\Local\Microsoft\WinGet\Packages\DigitalOcean.Doctl_Microsoft.Winget.Source_8wekyb3d8bbwe\doctl.exe apps create --spec minimal-deploy.yaml
echo.
echo Deployment started! Check progress at:
echo https://cloud.digitalocean.com/apps
echo.
pause