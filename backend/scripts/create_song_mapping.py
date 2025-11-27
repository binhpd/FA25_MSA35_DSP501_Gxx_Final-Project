#!/usr/bin/env python3
"""
Script để tạo file mapping song names từ danh sách file audio
Giúp đặt tên bài hát đẹp hơn thay vì dùng tên file
"""

import json
from pathlib import Path
import re


def extract_song_info_from_filename(filename: str) -> dict:
    """
    Trích xuất thông tin bài hát từ tên file
    
    Format phổ biến:
    - "Artist - Song Name.mp3"
    - "Song Name (feat. Artist).mp3"
    - "01 Song Name.mp3"
    - "Song_Name_2024.mp3"
    """
    # Remove extension
    name = Path(filename).stem
    
    # Try to extract artist and song name
    # Pattern: "Artist - Song Name"
    if ' - ' in name:
        parts = name.split(' - ', 1)
        return {
            'artist': parts[0].strip(),
            'song': parts[1].strip(),
            'full_name': name
        }
    
    # Pattern: "Song Name (feat. Artist)"
    if ' (feat.' in name or ' (ft.' in name:
        match = re.match(r'(.+?)\s*\(feat\.\s*(.+?)\)', name, re.IGNORECASE)
        if not match:
            match = re.match(r'(.+?)\s*\(ft\.\s*(.+?)\)', name, re.IGNORECASE)
        if match:
            return {
                'song': match.group(1).strip(),
                'artist': match.group(2).strip(),
                'full_name': f"{match.group(1).strip()} (feat. {match.group(2).strip()})"
            }
    
    # Remove track numbers: "01 Song Name" -> "Song Name"
    name = re.sub(r'^\d+\s*[-.]?\s*', '', name)
    
    # Replace underscores/hyphens with spaces
    name = re.sub(r'[_-]+', ' ', name)
    
    # Clean up
    name = name.strip()
    
    return {
        'song': name,
        'full_name': name
    }


def create_mapping_from_directory(directory: str, output_file: str = None) -> dict:
    """
    Tạo mapping file từ thư mục chứa audio files
    
    Args:
        directory: Đường dẫn thư mục
        output_file: File output (nếu None sẽ tạo song_mapping.json)
        
    Returns:
        Dict mapping
    """
    directory_path = Path(directory)
    if not directory_path.exists():
        print(f"❌ Thư mục không tồn tại: {directory}")
        return {}
    
    # Find all audio files
    extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
    audio_files = []
    for ext in extensions:
        audio_files.extend(directory_path.glob(f"*{ext}"))
        audio_files.extend(directory_path.glob(f"*{ext.upper()}"))
    
    if not audio_files:
        print(f"❌ Không tìm thấy file audio trong: {directory}")
        return {}
    
    print(f"📁 Tìm thấy {len(audio_files)} file audio\n")
    
    mapping = {}
    
    for file_path in sorted(audio_files):
        info = extract_song_info_from_filename(file_path.name)
        
        # Create nice song name
        if 'artist' in info and 'song' in info:
            song_name = f"{info['song']} - {info['artist']}"
        else:
            song_name = info.get('song', info.get('full_name', file_path.stem))
        
        # Clean up song name
        song_name = re.sub(r'\s+', ' ', song_name).strip()
        
        mapping[file_path.name] = song_name
        print(f"  {file_path.name}")
        print(f"    → {song_name}")
    
    # Save to file
    if output_file is None:
        output_file = directory_path / 'song_mapping.json'
    else:
        output_file = Path(output_file)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Đã tạo mapping file: {output_file}")
    print(f"   {len(mapping)} songs mapped")
    
    return mapping


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Tạo file mapping song names từ thư mục audio files'
    )
    parser.add_argument(
        'directory',
        type=str,
        help='Đường dẫn thư mục chứa file audio'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='File output (default: song_mapping.json trong thư mục)'
    )
    
    args = parser.parse_args()
    
    create_mapping_from_directory(args.directory, args.output)


if __name__ == "__main__":
    main()

