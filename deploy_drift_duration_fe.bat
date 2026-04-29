@echo off
cd C:\Users\adamh\.openclaw\workspace\earnings-push
echo Deploying frontend drift duration update...
git add .
git commit -m "Update drift duration display to 3-30 days for accurate trading timeframes"
git push origin main
echo Frontend deployed!