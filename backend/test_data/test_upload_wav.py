#!/usr/bin/env python3
"""
Test script to upload WAV files to the API
"""

import requests
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"
test_data_dir = Path(__file__).parent


def test_learn_song(file_path: str, song_name: str):
    """Test /learn endpoint with WAV file"""
    print(f"\n{'='*60}")
    print(f"Testing /learn endpoint")
    print(f"{'='*60}")
    print(f"File: {os.path.basename(file_path)}")
    print(f"Song Name: {song_name}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'audio/wav')}
            data = {'song_name': song_name}
            
            print(f"\nUploading to {BASE_URL}/learn...")
            response = requests.post(
                f"{BASE_URL}/learn",
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Success!")
                print(f"  Song: {result.get('song_name')}")
                print(f"  Fingerprints: {result.get('fingerprints_count')}")
                return True
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(f"  {response.text}")
                return False
                
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return False


def test_recognize_song(file_path: str):
    """Test /recognize endpoint with WAV file"""
    print(f"\n{'='*60}")
    print(f"Testing /recognize endpoint")
    print(f"{'='*60}")
    print(f"File: {os.path.basename(file_path)}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'audio/wav')}
            
            print(f"\nUploading to {BASE_URL}/recognize...")
            response = requests.post(
                f"{BASE_URL}/recognize",
                files=files,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"\n✅ Recognized!")
                    print(f"  Song: {result.get('song')}")
                    print(f"  Confidence: {result.get('confidence')}%")
                    print(f"  Matches: {result.get('matches')}")
                else:
                    print(f"\n⚠️  Not recognized: {result.get('message')}")
                return result
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(f"  {response.text}")
                return None
                
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return None


def test_stats():
    """Test /stats endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing /stats endpoint")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"\n✅ Database Stats:")
            print(f"  Songs: {stats.get('song_count')}")
            print(f"  Fingerprints: {stats.get('fingerprint_count')}")
            print(f"  Song List: {stats.get('songs')}")
            return stats
        else:
            print(f"❌ Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def main():
    """Run all tests"""
    print("="*60)
    print("TEST API UPLOAD .WAV FILES")
    print("="*60)
    
    # Check server
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server không phản hồi đúng: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Không thể kết nối đến server: {e}")
        print(f"   Đảm bảo server đang chạy tại {BASE_URL}")
        return
    
    print("✅ Server đang chạy")
    
    # Find WAV files
    wav_files = list(test_data_dir.glob("*.wav"))
    if not wav_files:
        print("\n❌ Không tìm thấy file .wav trong test_data/")
        print("   Chạy: python3 create_test_audio.py")
        return
    
    print(f"\n✅ Tìm thấy {len(wav_files)} file .wav")
    
    # Test 1: Learn songs
    print("\n" + "="*60)
    print("PHASE 1: Learning Songs")
    print("="*60)
    
    for i, wav_file in enumerate(wav_files[:2], 1):  # Test 2 files
        song_name = f"Test_Song_{i}"
        test_learn_song(str(wav_file), song_name)
    
    # Test 2: Check stats
    test_stats()
    
    # Test 3: Recognize songs
    print("\n" + "="*60)
    print("PHASE 2: Recognizing Songs")
    print("="*60)
    
    # Test recognition with same file (should match)
    if wav_files:
        test_recognize_song(str(wav_files[0]))
    
    # Test recognition with different file (might not match)
    if len(wav_files) > 1:
        test_recognize_song(str(wav_files[1]))
    
    print("\n" + "="*60)
    print("TEST COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()

