# Replace YOUR_GITHUB_USERNAME with your actual GitHub username
# Run this after creating the repository on GitHub

$username = Read-Host "Enter your GitHub username"
$repo_url = "https://github.com/$username/earnings-drift-scanner.git"

Write-Host "Adding remote origin: $repo_url" -ForegroundColor Green
git remote add origin $repo_url

Write-Host "Renaming branch to main..." -ForegroundColor Green
git branch -M main

Write-Host "Pushing to GitHub..." -ForegroundColor Green
git push -u origin main

Write-Host "`nDone! Your code is now on GitHub." -ForegroundColor Cyan
Write-Host "Next: Go to DigitalOcean App Platform to deploy" -ForegroundColor Yellow