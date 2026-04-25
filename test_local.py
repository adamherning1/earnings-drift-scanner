import subprocess
import time
import requests

print("Testing API locally...")

# Start the API
process = subprocess.Popen(
    ["python", "-m", "uvicorn", "app.main:app", "--reload", "--port", "8001"],
    cwd="api"
)

# Wait for startup
print("Waiting for API to start...")
time.sleep(5)

try:
    # Test the API
    response = requests.get("http://localhost:8001/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    response = requests.get("http://localhost:8001/health")
    print(f"Health check: {response.json()}")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    # Stop the process
    process.terminate()
    print("\nAPI test complete!")