@echo off
echo Starting MGC Bot on Dell (localhost connection)...
cd /d C:\Users\adam\mgc_trader
python -c "import fileinput; [print(line.replace('192.168.0.58', '127.0.0.1') if 'IB_HOST' in line else line, end='') for line in fileinput.input('config.py', inplace=True)]"
python adaptive_trading_bot.py
pause