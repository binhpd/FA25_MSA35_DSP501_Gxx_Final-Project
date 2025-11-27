"""
Script to download sample audio files for testing
Note: This script downloads royalty-free music samples for testing purposes
"""

import os
import urllib.request
from pathlib import Path

# Create test_data directory
test_data_dir = Path(__file__).parent
test_data_dir.mkdir(exist_ok=True)

# Sample audio URLs (royalty-free test samples)
# These are short audio clips suitable for testing
TEST_SONGS = [
    {
        "name": "test_song_1",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "filename": "test_song_1.mp3"
    },
    {
        "name": "test_song_2", 
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        "filename": "test_song_2.mp3"
    },
    {
        "name": "test_song_3",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
        "filename": "test_song_3.mp3"
    }
]


def download_file(url: str, filepath: Path):
    """Download a file from URL"""
    try:
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, filepath)
        print(f"✓ Downloaded: {filepath.name}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {url}: {e}")
        return False


def main():
    """Download test audio files"""
    print("=" * 60)
    print("Downloading Test Audio Files")
    print("=" * 60)
    
    downloaded = 0
    for song in TEST_SONGS:
        filepath = test_data_dir / song["filename"]
        
        if filepath.exists():
            print(f"⚠ {song['filename']} already exists, skipping...")
            continue
        
        if download_file(song["url"], filepath):
            downloaded += 1
    
    print("\n" + "=" * 60)
    print(f"Downloaded {downloaded} files")
    print(f"Test data directory: {test_data_dir}")
    print("=" * 60)
    
    if downloaded == 0:
        print("\n⚠ No files downloaded. You may need to:")
        print("1. Add your own audio files to the test_data/ directory")
        print("2. Or use the create_test_audio.py script to generate test tones")


if __name__ == "__main__":
    main()

