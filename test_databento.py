"""Test Databento connection and data access"""
import os
from dotenv import load_dotenv

load_dotenv()

# First check if databento is installed
try:
    import databento as db
    print("[OK] Databento library installed")
except ImportError:
    print("[ERROR] Databento not installed. Run: pip install databento")
    exit(1)

# Check API key
api_key = os.getenv('DATABENTO_API_KEY')
if api_key:
    print(f"[OK] Found API key: {api_key[:10]}...")
else:
    print("[ERROR] DATABENTO_API_KEY not found in .env")
    exit(1)

# Test connection
print("\n[TESTING] Databento connection...")
try:
    client = db.Historical(api_key)
    
    # Test 1: Get metadata (cheapest call)
    print("\nTest 1: Checking available datasets...")
    datasets = client.metadata.list_datasets()
    if datasets:
        print(f"[OK] Connected! Found {len(datasets)} datasets")
        for ds in datasets[:3]:
            print(f"  - {ds.dataset}")
    
    # Test 2: Get a tiny amount of data
    print("\nTest 2: Fetching sample AAPL data...")
    try:
        # Get 1 day of AAPL trades
        data = client.timeseries.get_range(
            dataset='XNAS.ITCH',  # NASDAQ
            symbols=['AAPL'],
            schema='trades',
            start='2026-04-23',
            end='2026-04-23',
            limit=5  # Just 5 trades to test
        )
        
        trades = list(data)
        if trades:
            print(f"[OK] Got {len(trades)} trades")
            print(f"  Sample: AAPL @ ${trades[0].price/1e9:.2f}")
        else:
            print("[WARNING] No trades returned")
            
    except Exception as e:
        print(f"[INFO] Trades test failed: {e}")
        print("  (This is OK if you don't have NASDAQ subscription)")
    
    # Test 3: Check what we actually need
    print("\nTest 3: Checking requirements for earnings scanner...")
    print("  [ ] Corporate Actions dataset - for earnings dates")
    print("  [ ] OPRA dataset - for options chains")
    print("  [ ] Equities data - for price/volume")
    
    print("\n[SUMMARY]")
    print("✅ Databento connection working!")
    print("⚠️  Note: Earnings scanner needs Corporate Actions subscription")
    print("💡 For MVP, we'll use manual earnings calendar + Yahoo for prices")
    
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    print("\nPossible issues:")
    print("1. API key might be expired")
    print("2. Network connection issue")
    print("3. Databento API down")