@echo off
echo Pushing trades page updates...
git add app/trades/page.js
git commit -m "Update paper trades with war market crash stop loss prices"
git push earnings master
echo Trades page pushed!