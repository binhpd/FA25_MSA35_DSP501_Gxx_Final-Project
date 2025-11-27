"""
Script to test the Music Recognition API
Tests both /learn and /recognize endpoints
"""

import requests
import os
from pathlib import Path
import time

# API base URL
BASE_URL = "http://localhost:8000"

# Test data directory
test_data_dir = Path(__file__).parent


def test_server_connection():
    """Test if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✓ Server is running")
            print(f"  Response: {response.json()}")
            return True
    except Exception as e:
        print(f"✗ Cannot connect to server: {e}")
        print(f"  Make sure the server is running at {BASE_URL}")
        return False
    return False


def learn_song(file_path: str, song_name: str):
    """Add a song to the database"""
    print(f"\nLearning song: {song_name}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'audio/wav')}
            data = {'song_name': song_name}
            
            response = requests.post(
                f"{BASE_URL}/learn",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Success: {result['message']}")
                print(f"  Fingerprints: {result['fingerprints_count']}")
                return True
            else:
                print(f"✗ Error: {response.status_code}")
                print(f"  {response.text}")
                return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


def recognize_song(file_path: str):
    """Recognize a song from audio sample"""
    print(f"\nRecognizing song from: {os.path.basename(file_path)}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'audio/wav')}
            
            response = requests.post(
                f"{BASE_URL}/recognize",
                files=files
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"✓ Recognized: {result['song']}")
                    print(f"  Confidence: {result['confidence']}%")
                    print(f"  Matches: {result['matches']}")
                else:
                    print(f"✗ Not recognized: {result['message']}")
                return result
            else:
                print(f"✗ Error: {response.status_code}")
                print(f"  {response.text}")
                return None
    except Exception as e:
        print(f"✗ Exception: {e}")
        return None


def get_stats():
    """Get database statistics"""
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"\nDatabase Stats:")
            print(f"  Songs: {stats['song_count']}")
            print(f"  Fingerprints: {stats['fingerprint_count']}")
            print(f"  Song list: {stats['songs']}")
            return stats
    except Exception as e:
        print(f"✗ Error getting stats: {e}")
    return None


def main():
    """Run API tests"""
    print("=" * 60)
    print("Testing Music Recognition API")
    print("=" * 60)
    
    # Test server connection
    if not test_server_connection():
        return
    
    # Get initial stats
    print("\n" + "-" * 60)
    print("Initial Database State:")
    get_stats()
    
    # Find test audio files
    audio_files = list(test_data_dir.glob("*.wav")) + list(test_data_dir.glob("*.mp3"))
    
    if not audio_files:
        print("\n⚠ No audio files found in test_data/ directory")
        print("Please run create_test_audio.py or download_test_songs.py first")
        return
    
    print(f"\nFound {len(audio_files)} audio file(s)")
    
    # Learn songs
    print("\n" + "=" * 60)
    print("PHASE 1: Learning Songs")
    print("=" * 60)
    
    for i, audio_file in enumerate(audio_files, 1):
        song_name = f"test_song_{i}"
        learn_song(str(audio_file), song_name)
        time.sleep(0.5)  # Small delay between requests
    
    # Get stats after learning
    print("\n" + "-" * 60)
    print("Database State After Learning:")
    get_stats()
    
    # Recognize songs
    print("\n" + "=" * 60)
    print("PHASE 2: Recognizing Songs")
    print("=" * 60)
    
    # Test recognition with the same files (should match)
    for i, audio_file in enumerate(audio_files, 1):
        song_name = f"test_song_{i}"
        print(f"\nTesting recognition of {song_name}...")
        recognize_song(str(audio_file))
        time.sleep(0.5)
    
    # Test with partial sample (first 3 seconds)
    print("\n" + "=" * 60)
    print("PHASE 3: Testing with Partial Samples")
    print("=" * 60)
    
    if audio_files:
        # Use first file as test
        test_file = audio_files[0]
        print(f"\nTesting with partial sample from {test_file.name}...")
        recognize_song(str(test_file))
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

