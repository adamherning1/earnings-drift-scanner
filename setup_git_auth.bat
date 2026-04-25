@echo off
echo Setting up GitHub authentication...
echo.
echo You'll need a Personal Access Token from GitHub:
echo 1. Go to: https://github.com/settings/tokens/new
echo 2. Give it a name like "Earnings Scanner Deploy"
echo 3. Select scopes: "repo" (full control)
echo 4. Click "Generate token"
echo 5. Copy the token (starts with ghp_)
echo.
start https://github.com/settings/tokens/new
echo.
set /p token="Paste your GitHub token here: "
echo.
git remote set-url origin https://%token%@github.com/adamherning1/earnings-drift-scanner.git
echo.
echo Pushing code to GitHub...
git push origin main
echo.
echo Done! Your code should now be on GitHub.
pause