# DigitalOcean CLI deployment script - Fixed path version

$doctlPath = "C:\Users\adamh\AppData\Local\Microsoft\WinGet\Packages\DigitalOcean.Doctl_Microsoft.Winget.Source_8wekyb3d8bbwe\doctl.exe"

Write-Host "DigitalOcean CLI Deployment" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

# First update app.yaml with your username
Write-Host "`nUpdating app configuration..." -ForegroundColor Yellow
$appYaml = Get-Content -Path ".do/app.yaml" -Raw
$appYaml = $appYaml -replace 'YOUR_GITHUB_USERNAME', 'adamherning1'
Set-Content -Path ".do/app.yaml" -Value $appYaml -NoNewline

Write-Host "✓ Configuration updated" -ForegroundColor Green

# Get API token
Write-Host "`nYou need a DigitalOcean API token to continue." -ForegroundColor Yellow
Write-Host "`nSteps to get your token:" -ForegroundColor White
Write-Host "1. I'll open the DigitalOcean API page" -ForegroundColor White
Write-Host "2. Click 'Generate New Token'" -ForegroundColor White
Write-Host "3. Name it: 'Earnings Scanner Deployment'" -ForegroundColor White
Write-Host "4. Select 'Write' scope (important!)" -ForegroundColor White
Write-Host "5. Click 'Generate Token'" -ForegroundColor White
Write-Host "6. Copy the token immediately (shown only once!)" -ForegroundColor White

Write-Host "`nPress Enter to open DigitalOcean API page..." -ForegroundColor Yellow
Read-Host

Start-Process "https://cloud.digitalocean.com/account/api/tokens"

Write-Host "`nAfter you've copied your token..." -ForegroundColor Yellow
$token = Read-Host "Paste your DigitalOcean API token here (it will be hidden)"

# Authenticate
Write-Host "`nAuthenticating..." -ForegroundColor Yellow
& $doctlPath auth init --access-token $token

# Create the app
Write-Host "`nCreating your app on DigitalOcean..." -ForegroundColor Green
& $doctlPath apps create --spec .do/app.yaml

Write-Host "`n✅ Deployment started!" -ForegroundColor Green
Write-Host "`nYour app is being built and deployed. This takes 5-10 minutes." -ForegroundColor Cyan
Write-Host "`nCheck deployment status at:" -ForegroundColor White
Write-Host "https://cloud.digitalocean.com/apps" -ForegroundColor Yellow

Write-Host "`nTo view your app details, run:" -ForegroundColor White
Write-Host "doctl apps list" -ForegroundColor Gray