"""
Test script for chiec-khan-gio-am_test1.mp3
"""
import requests
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"

# Path to test file
TEST_FILE = Path(__file__).parent.parent.parent / "source_test" / "chiec-khan-gio-am_test1.mp3"
SONG_NAME = "chiec-khan-gio-am"

def test_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print(f"   Make sure server is running at {BASE_URL}")
        return False
    return False

def learn_song():
    """Add song to database"""
    print(f"\n{'='*60}")
    print(f"PHASE 1: Learning song '{SONG_NAME}'")
    print(f"{'='*60}")
    
    if not TEST_FILE.exists():
        print(f"❌ File not found: {TEST_FILE}")
        return False
    
    print(f"📁 File: {TEST_FILE.name}")
    print(f"📊 Size: {TEST_FILE.stat().st_size / 1024 / 1024:.2f} MB")
    
    try:
        with open(TEST_FILE, 'rb') as f:
            files = {'file': (TEST_FILE.name, f, 'audio/mpeg')}
            data = {'song_name': SONG_NAME}
            
            print(f"\n📤 Uploading to {BASE_URL}/learn...")
            response = requests.post(
                f"{BASE_URL}/learn",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success!")
                print(f"   Song: {result.get('song_name')}")
                print(f"   Fingerprints: {result.get('fingerprints_count')}")
                print(f"   Message: {result.get('message')}")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   {response.text}")
                return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def recognize_song():
    """Test recognition"""
    print(f"\n{'='*60}")
    print(f"PHASE 2: Recognizing song from sample")
    print(f"{'='*60}")
    
    try:
        with open(TEST_FILE, 'rb') as f:
            files = {'file': (TEST_FILE.name, f, 'audio/mpeg')}
            
            print(f"\n📤 Uploading to {BASE_URL}/recognize...")
            response = requests.post(
                f"{BASE_URL}/recognize",
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ Recognized!")
                    print(f"   Song: {result.get('song')}")
                    print(f"   Confidence: {result.get('confidence')}%")
                    print(f"   Matches: {result.get('matches')}")
                    print(f"   Message: {result.get('message')}")
                else:
                    print(f"⚠️  Not recognized: {result.get('message')}")
                return result
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   {response.text}")
                return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def get_stats():
    """Get database stats"""
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"\n📊 Database Stats:")
            print(f"   Songs: {stats.get('song_count', 0)}")
            print(f"   Fingerprints: {stats.get('fingerprint_count', 0)}")
            if stats.get('songs'):
                print(f"   Song list: {stats.get('songs')}")
            return stats
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def main():
    print("="*60)
    print("TEST: chiec-khan-gio-am_test1.mp3")
    print("="*60)
    
    if not test_server():
        return
    
    # Check initial stats
    print("\n📊 Initial Database State:")
    get_stats()
    
    # Learn the song
    if not learn_song():
        print("\n❌ Failed to learn song. Cannot proceed with recognition test.")
        return
    
    # Check stats after learning
    print("\n📊 Database State After Learning:")
    get_stats()
    
    # Test recognition
    recognize_song()
    
    print("\n" + "="*60)
    print("TEST COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    main()