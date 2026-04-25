# Manual authentication and deployment

$doctl = "C:\Users\adamh\AppData\Local\Microsoft\WinGet\Packages\DigitalOcean.Doctl_Microsoft.Winget.Source_8wekyb3d8bbwe\doctl.exe"

Write-Host "Paste your DigitalOcean token below and press Enter:" -ForegroundColor Yellow
$token = Read-Host -AsSecureString "Token"
$tokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($token))

Write-Host "`nAuthenticating with DigitalOcean..." -ForegroundColor Cyan
& $doctl auth init --access-token $tokenPlain

Write-Host "`nChecking authentication..." -ForegroundColor Yellow
& $doctl account get

Write-Host "`nPress any key to deploy your app..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')