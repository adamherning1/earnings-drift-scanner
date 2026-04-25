# DigitalOcean CLI deployment script

Write-Host "This script will deploy your app using DigitalOcean CLI" -ForegroundColor Cyan

# First, check if doctl is installed
if (-not (Get-Command doctl -ErrorAction SilentlyContinue)) {
    Write-Host "Installing DigitalOcean CLI..." -ForegroundColor Yellow
    winget install DigitalOcean.Doctl
}

# Update the app.yaml with your GitHub username
$appYaml = Get-Content -Path ".do/app.yaml" -Raw
$appYaml = $appYaml -replace 'YOUR_GITHUB_USERNAME', 'adamherning1'
Set-Content -Path ".do/app.yaml" -Value $appYaml

Write-Host "`nTo continue, you'll need a DigitalOcean API token:" -ForegroundColor Yellow
Write-Host "1. Go to: https://cloud.digitalocean.com/account/api/tokens" -ForegroundColor White
Write-Host "2. Generate a new token with 'write' scope" -ForegroundColor White
Write-Host "3. Copy the token (you'll only see it once!)" -ForegroundColor White

$token = Read-Host "`nPaste your DigitalOcean API token here"

# Authenticate
doctl auth init --access-token $token

# Create the app
Write-Host "`nDeploying your app..." -ForegroundColor Green
doctl apps create --spec .do/app.yaml

Write-Host "`nDeployment started! Check status at:" -ForegroundColor Cyan
Write-Host "https://cloud.digitalocean.com/apps" -ForegroundColor White