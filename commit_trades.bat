@echo off
cd C:\Users\adamh\.openclaw\workspace\earnings-push
echo Adding trades page...
git add app\trades\page.js
git commit -m "Update paper trades with war market crash stop loss prices - all positions stopped at -5%"
git push earnings master
echo Done!