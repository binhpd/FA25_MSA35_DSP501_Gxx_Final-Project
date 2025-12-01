"""
Test script to verify connection to backend server
"""

from api_client import APIClient
import config

def test_connection():
    """Test connection to backend server"""
    print("🔍 Testing connection to backend server...")
    print(f"📍 Server URL: {config.BASE_URL}")
    
    client = APIClient(base_url=config.BASE_URL)
    
    if client.test_connection():
        print("✅ Connection successful! Backend server is running.")
        
        # Test recognize endpoint exists
        endpoint_exists, endpoint_msg = client.test_recognize_endpoint()
        if endpoint_exists:
            print(f"✅ {endpoint_msg}")
        else:
            print(f"⚠️  {endpoint_msg}")
            print("💡 Endpoint /recognize might not exist. Check backend server version.")
        
        # Test stats endpoint
        try:
            import requests
            response = requests.get(f"{config.BASE_URL}/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                print(f"📊 Database stats:")
                print(f"   - Songs: {stats.get('song_count', 0)}")
                print(f"   - Fingerprints: {stats.get('fingerprint_count', 0)}")
            elif response.status_code == 404:
                print("⚠️  /stats endpoint not found (404)")
            else:
                print(f"⚠️  /stats returned status {response.status_code}")
        except Exception as e:
            print(f"⚠️  Could not fetch stats: {e}")
        
        return True
    else:
        print("❌ Connection failed! Make sure backend server is running.")
        print(f"   Start backend with: cd ../backend && python -m app.main")
        return False

if __name__ == "__main__":
    test_connection()

