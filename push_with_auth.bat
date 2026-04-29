@echo off
cd C:\Users\adamh\.openclaw\workspace\earnings-push
echo Setting up credentials...
git config credential.helper manager
echo.
echo Attempting push with credentials...
git push origin main
echo.
echo If prompted, please enter your GitHub credentials.
echo Push attempt complete!