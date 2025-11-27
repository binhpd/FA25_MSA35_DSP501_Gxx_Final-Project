#!/usr/bin/env python3
"""
Test script để test các API xóa bài hát
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_delete_song(song_name: str):
    """Test xóa một bài hát cụ thể"""
    print(f"\n{'='*60}")
    print(f"Testing DELETE /songs/{song_name}")
    print(f"{'='*60}")
    
    try:
        response = requests.delete(f"{BASE_URL}/songs/{song_name}", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('success'):
            print(f"\n✅ Success!")
            print(f"  Deleted: {result.get('deleted_fingerprints')} fingerprints")
        else:
            print(f"\n⚠️  {result.get('message')}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return None


def test_clear_all():
    """Test xóa toàn bộ database"""
    print(f"\n{'='*60}")
    print(f"Testing DELETE /songs (clear all)")
    print(f"{'='*60}")
    
    try:
        response = requests.delete(f"{BASE_URL}/songs", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('success'):
            print(f"\n✅ Success!")
            print(f"  Deleted: {result.get('deleted_songs')} songs")
            print(f"  Deleted: {result.get('deleted_fingerprints')} fingerprints")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return None


def get_stats():
    """Lấy stats hiện tại"""
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        return None


def main():
    """Run tests"""
    print("="*60)
    print("TEST DELETE SONGS API")
    print("="*60)
    
    # Check server
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server không phản hồi đúng")
            return
    except Exception as e:
        print(f"❌ Không thể kết nối đến server: {e}")
        return
    
    print("✅ Server đang chạy\n")
    
    # Get current stats
    print("📊 Database hiện tại:")
    stats = get_stats()
    if stats:
        print(f"  Songs: {stats.get('song_count', 0)}")
        print(f"  Fingerprints: {stats.get('fingerprint_count', 0):,}")
        print(f"  Song List: {stats.get('songs', [])}")
    
    if not stats or stats.get('song_count', 0) == 0:
        print("\n⚠️  Database trống. Vui lòng thêm bài hát trước.")
        return
    
    # Test 1: Delete specific song
    if stats.get('songs'):
        first_song = stats['songs'][0]
        print(f"\n{'='*60}")
        print("PHASE 1: Delete Specific Song")
        print(f"{'='*60}")
        test_delete_song(first_song)
        
        # Check stats after deletion
        print("\n📊 Database sau khi xóa:")
        new_stats = get_stats()
        if new_stats:
            print(f"  Songs: {new_stats.get('song_count', 0)}")
            print(f"  Fingerprints: {new_stats.get('fingerprint_count', 0):,}")
    
    # Test 2: Clear all (optional - uncomment to test)
    print(f"\n{'='*60}")
    print("PHASE 2: Clear All Songs (Optional)")
    print(f"{'='*60}")
    print("⚠️  Uncomment trong code để test clear all")
    # test_clear_all()
    
    print("\n" + "="*60)
    print("TEST COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()

