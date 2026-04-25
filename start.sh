#!/bin/bash
cd api
python -m uvicorn main_v3_no_databento:app --host 0.0.0.0 --port $PORT