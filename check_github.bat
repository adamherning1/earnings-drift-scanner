@echo off
echo Checking what's on GitHub...
powershell -Command "(Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/adamherning1/earnings-drift-scanner/main/api/requirements.txt').Content" | findstr /C:"scipy" /C:"gunicorn"
pause