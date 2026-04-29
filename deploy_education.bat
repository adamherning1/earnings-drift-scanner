@echo off
cd C:\Users\adamh\.openclaw\workspace\earnings-push
echo Deploying education page...
git add .
git commit -m "Add comprehensive trading education page with position sizing, options vs stocks, and risk management"
git push origin main
echo Education page deployed! Check the site in a few minutes.