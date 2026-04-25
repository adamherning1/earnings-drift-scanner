# Simple DigitalOcean deployment

$doctl = "C:\Users\adamh\AppData\Local\Microsoft\WinGet\Packages\DigitalOcean.Doctl_Microsoft.Winget.Source_8wekyb3d8bbwe\doctl.exe"

Write-Host "`nDigitalOcean Deployment" -ForegroundColor Cyan

# Update app.yaml
(Get-Content .do/app.yaml -Raw) -replace 'YOUR_GITHUB_USERNAME', 'adamherning1' | Set-Content .do/app.yaml

Write-Host "`n1. Go to: https://cloud.digitalocean.com/account/api/tokens" -ForegroundColor Yellow
Write-Host "2. Create a token with 'write' permissions" -ForegroundColor Yellow
Write-Host "3. Copy it (shown only once!)" -ForegroundColor Yellow

Start-Process "https://cloud.digitalocean.com/account/api/tokens"

$token = Read-Host "`nPaste token here"

# Auth
& $doctl auth init --access-token $token

# Deploy
Write-Host "`nDeploying..." -ForegroundColor Green
& $doctl apps create --spec .do/app.yaml

Write-Host "`nDone! Check: https://cloud.digitalocean.com/apps" -ForegroundColor Cyan