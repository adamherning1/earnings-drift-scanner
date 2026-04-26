@echo off
echo Starting Earnings History Pipeline with REAL Massive/Benzinga data...
echo.

REM Set the API key
set MASSIVE_API_KEY=W9yf_4m5NsX89ZNS5jGSfYkVorDBPiGfN

REM Test the endpoint first
echo Step 1: Testing Benzinga earnings endpoint...
python test_benzinga_earnings.py

echo.
echo Step 2: Running full pipeline...
python earnings_history_pipeline.py

echo.
echo Pipeline complete! Check these files:
echo - earnings_history.json (raw earnings data)
echo - drift_patterns.json (calculated patterns)
echo - drift_analysis_report.md (summary report)
pause