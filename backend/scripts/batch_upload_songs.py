#!/usr/bin/env python3
"""
Script để batch upload nhiều bài hát vào database
Tự động lấy danh sách bài hát từ thư mục và upload lên server
"""

import os
import requests
import json
from pathlib import Path
from typing import List, Dict
import time

# API Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 60  # seconds per file


def get_audio_files(directory: str, extensions: List[str] = None) -> List[Path]:
    """
    Lấy danh sách tất cả file audio trong thư mục
    
    Args:
        directory: Đường dẫn thư mục chứa file audio
        extensions: List các extension cần tìm (mặc định: .wav, .mp3, .m4a, .flac)
        
    Returns:
        List các file audio tìm được
    """
    if extensions is None:
        extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
    
    directory_path = Path(directory)
    if not directory_path.exists():
        print(f"❌ Thư mục không tồn tại: {directory}")
        return []
    
    audio_files = []
    for ext in extensions:
        audio_files.extend(directory_path.glob(f"*{ext}"))
        audio_files.extend(directory_path.glob(f"*{ext.upper()}"))
    
    return sorted(audio_files)


def extract_song_name(file_path: Path) -> str:
    """
    Trích xuất tên bài hát từ tên file
    
    Args:
        file_path: Đường dẫn file
        
    Returns:
        Tên bài hát (đã loại bỏ extension và ký tự đặc biệt)
    """
    # Lấy tên file không có extension
    name = file_path.stem
    
    # Loại bỏ các ký tự đặc biệt, thay thế bằng underscore
    import re
    name = re.sub(r'[^\w\s-]', '_', name)
    name = re.sub(r'[\s_-]+', '_', name)
    
    # Giới hạn độ dài
    if len(name) > 100:
        name = name[:100]
    
    return name.strip('_')


def upload_song(file_path: Path, song_name: str = None) -> Dict:
    """
    Upload một bài hát lên server
    
    Args:
        file_path: Đường dẫn file audio
        song_name: Tên bài hát (nếu None sẽ tự động lấy từ tên file)
        
    Returns:
        Dict chứa kết quả upload
    """
    if song_name is None:
        song_name = extract_song_name(file_path)
    
    print(f"\n📤 Uploading: {file_path.name}")
    print(f"   Song Name: {song_name}")
    print(f"   File Size: {file_path.stat().st_size / 1024:.1f} KB")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'audio/wav')}
            data = {'song_name': song_name}
            
            response = requests.post(
                f"{BASE_URL}/learn",
                files=files,
                data=data,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {result.get('fingerprints_count')} fingerprints")
                return {
                    'success': True,
                    'file': str(file_path),
                    'song_name': song_name,
                    'fingerprints': result.get('fingerprints_count', 0),
                    'message': result.get('message', '')
                }
            else:
                error_msg = response.text
                print(f"   ❌ Error {response.status_code}: {error_msg}")
                return {
                    'success': False,
                    'file': str(file_path),
                    'song_name': song_name,
                    'error': error_msg
                }
                
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return {
            'success': False,
            'file': str(file_path),
            'song_name': song_name,
            'error': str(e)
        }


def batch_upload(directory: str, song_names: Dict[str, str] = None) -> Dict:
    """
    Upload tất cả bài hát trong thư mục
    
    Args:
        directory: Đường dẫn thư mục chứa file audio
        song_names: Dict mapping file_name -> song_name (optional)
        
    Returns:
        Dict chứa kết quả tổng hợp
    """
    print("="*60)
    print("BATCH UPLOAD SONGS TO DATABASE")
    print("="*60)
    
    # Check server
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server không phản hồi đúng: {response.status_code}")
            return {'success': False, 'error': 'Server not responding'}
    except Exception as e:
        print(f"❌ Không thể kết nối đến server: {e}")
        print(f"   Đảm bảo server đang chạy tại {BASE_URL}")
        return {'success': False, 'error': str(e)}
    
    print("✅ Server đang chạy\n")
    
    # Get audio files
    audio_files = get_audio_files(directory)
    
    if not audio_files:
        print(f"❌ Không tìm thấy file audio trong: {directory}")
        return {'success': False, 'error': 'No audio files found'}
    
    print(f"📁 Tìm thấy {len(audio_files)} file audio\n")
    
    # Upload each file
    results = {
        'total': len(audio_files),
        'success': 0,
        'failed': 0,
        'songs': []
    }
    
    for i, file_path in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] Processing...")
        
        # Get song name from mapping or extract from filename
        song_name = None
        if song_names and file_path.name in song_names:
            song_name = song_names[file_path.name]
        
        result = upload_song(file_path, song_name)
        results['songs'].append(result)
        
        if result['success']:
            results['success'] += 1
        else:
            results['failed'] += 1
        
        # Small delay to avoid overwhelming server
        time.sleep(0.5)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total files: {results['total']}")
    print(f"✅ Success: {results['success']}")
    print(f"❌ Failed: {results['failed']}")
    
    if results['success'] > 0:
        total_fingerprints = sum(s.get('fingerprints', 0) for s in results['songs'] if s.get('success'))
        print(f"📊 Total fingerprints: {total_fingerprints:,}")
    
    # Get final stats
    try:
        stats_response = requests.get(f"{BASE_URL}/stats", timeout=5)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"\n📈 Database Stats:")
            print(f"   Songs: {stats.get('song_count', 0)}")
            print(f"   Fingerprints: {stats.get('fingerprint_count', 0):,}")
    except:
        pass
    
    return results


def load_song_mapping(file_path: str) -> Dict[str, str]:
    """
    Load song name mapping từ file JSON
    
    Format JSON:
    {
        "song1.mp3": "Song Name 1",
        "song2.wav": "Song Name 2"
    }
    
    Args:
        file_path: Đường dẫn file JSON
        
    Returns:
        Dict mapping file_name -> song_name
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Không thể load mapping file: {e}")
        return {}


def main():
    """Main function với CLI interface"""
    import argparse
    global BASE_URL
    
    parser = argparse.ArgumentParser(
        description='Batch upload songs to Music Recognition API'
    )
    parser.add_argument(
        'directory',
        type=str,
        help='Đường dẫn thư mục chứa file audio'
    )
    parser.add_argument(
        '--mapping',
        type=str,
        help='File JSON chứa mapping file_name -> song_name (optional)'
    )
    parser.add_argument(
        '--url',
        type=str,
        default='http://localhost:8000',
        help='API base URL (default: http://localhost:8000)'
    )
    
    args = parser.parse_args()
    
    # Update base URL if provided
    BASE_URL = args.url
    
    # Load song mapping if provided
    song_names = {}
    if args.mapping:
        song_names = load_song_mapping(args.mapping)
        print(f"📋 Loaded {len(song_names)} song name mappings")
    
    # Run batch upload
    results = batch_upload(args.directory, song_names)
    
    # Save results to file
    output_file = Path(args.directory) / 'upload_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file}")


if __name__ == "__main__":
    main()

