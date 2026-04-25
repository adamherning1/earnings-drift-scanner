import sys
import os
sys.path.append('api')

try:
    from main_v3_no_databento import app
    print("✅ App imported successfully!")
    print(f"App title: {app.title}")
    print(f"App version: {app.version}")
    print("Ready to start with uvicorn!")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()