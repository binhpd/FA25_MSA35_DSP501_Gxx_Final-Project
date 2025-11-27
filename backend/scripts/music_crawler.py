#!/usr/bin/env python3
"""
Music Crawler - Tool để crawl và tải dữ liệu nhạc MP3
Bao gồm: file MP3, metadata, hình ảnh album, thông tin chi tiết

Các tính năng:
1. Tải MP3 từ YouTube (sử dụng yt-dlp)
2. Trích xuất metadata từ file MP3 hiện có
3. Lấy metadata từ APIs (Last.fm, MusicBrainz, Discogs)
4. Tải hình ảnh album
5. Tổ chức file với metadata đầy đủ
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from urllib.parse import quote
import time

try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TPE2, APIC, TCON, TCOM
    from mutagen.easyid3 import EasyID3
except ImportError:
    print("⚠️  mutagen chưa được cài đặt. Chạy: pip install mutagen")
    MP3 = None

try:
    import yt_dlp
except ImportError:
    print("⚠️  yt-dlp chưa được cài đặt. Chạy: pip install yt-dlp")
    yt_dlp = None


@dataclass
class SongMetadata:
    """Cấu trúc metadata cho bài hát"""
    title: str
    artist: str
    album: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    composer: Optional[str] = None
    album_artist: Optional[str] = None
    track_number: Optional[int] = None
    cover_image_url: Optional[str] = None
    cover_image_path: Optional[str] = None
    spotify_url: Optional[str] = None
    youtube_url: Optional[str] = None
    duration: Optional[float] = None
    file_path: Optional[str] = None


class MusicCrawler:
    """Class chính để crawl và quản lý dữ liệu nhạc"""
    
    def __init__(self, output_dir: str = "downloaded_music"):
        """
        Khởi tạo crawler
        
        Args:
            output_dir: Thư mục lưu file đã tải
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Tạo các thư mục con
        self.music_dir = self.output_dir / "music"
        self.images_dir = self.output_dir / "images"
        self.metadata_dir = self.output_dir / "metadata"
        
        self.music_dir.mkdir(exist_ok=True)
        self.images_dir.mkdir(exist_ok=True)
        self.metadata_dir.mkdir(exist_ok=True)
    
    def download_from_youtube(self, url: str, metadata: Optional[SongMetadata] = None) -> Optional[str]:
        """
        Tải MP3 từ YouTube URL
        
        Args:
            url: YouTube URL
            metadata: Metadata tùy chọn để gán vào file
            
        Returns:
            Đường dẫn file MP3 đã tải, hoặc None nếu lỗi
        """
        if yt_dlp is None:
            print("❌ yt-dlp chưa được cài đặt")
            return None
        
        print(f"📥 Đang tải từ YouTube: {url}")
        
        # Cấu hình yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.music_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'no_warnings': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Lấy thông tin video
                info = ydl.extract_info(url, download=True)
                
                # Tìm file đã tải
                title = info.get('title', 'Unknown')
                filename = ydl.prepare_filename(info)
                mp3_file = Path(filename).with_suffix('.mp3')
                
                if not mp3_file.exists():
                    # Tìm file MP3 mới nhất trong thư mục
                    mp3_files = list(self.music_dir.glob('*.mp3'))
                    if mp3_files:
                        mp3_file = max(mp3_files, key=lambda p: p.stat().st_mtime)
                    else:
                        print("❌ Không tìm thấy file MP3 đã tải")
                        return None
                
                print(f"✅ Đã tải: {mp3_file.name}")
                
                # Gán metadata nếu có
                if metadata:
                    self.set_mp3_metadata(str(mp3_file), metadata)
                else:
                    # Tự động tạo metadata từ thông tin YouTube
                    auto_metadata = SongMetadata(
                        title=title,
                        artist=info.get('uploader', 'Unknown'),
                        youtube_url=url,
                        duration=info.get('duration', 0)
                    )
                    self.set_mp3_metadata(str(mp3_file), auto_metadata)
                
                return str(mp3_file)
                
        except Exception as e:
            print(f"❌ Lỗi khi tải từ YouTube: {e}")
            return None
    
    def get_metadata_from_lastfm(self, artist: str, track: str) -> Optional[SongMetadata]:
        """
        Lấy metadata từ Last.fm API
        
        Args:
            artist: Tên nghệ sĩ
            track: Tên bài hát
            
        Returns:
            SongMetadata hoặc None
        """
        print(f"🔍 Đang tìm metadata từ Last.fm: {artist} - {track}")
        
        try:
            # Last.fm API (không cần API key cho basic search)
            url = f"http://ws.audioscrobbler.com/2.0/"
            params = {
                'method': 'track.getInfo',
                'api_key': 'YOUR_API_KEY',  # Có thể bỏ qua cho search
                'artist': artist,
                'track': track,
                'format': 'json'
            }
            
            # Thử search trước (không cần API key)
            search_url = f"http://ws.audioscrobbler.com/2.0/"
            search_params = {
                'method': 'track.search',
                'track': f"{artist} {track}",
                'format': 'json',
                'limit': 1
            }
            
            response = requests.get(search_url, params=search_params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                tracks = data.get('results', {}).get('trackmatches', {}).get('track', [])
                
                if tracks:
                    track_info = tracks[0]
                    metadata = SongMetadata(
                        title=track_info.get('name', track),
                        artist=track_info.get('artist', artist),
                        cover_image_url=track_info.get('image', [{}])[-1].get('#text', '')
                    )
                    print(f"✅ Tìm thấy trên Last.fm")
                    return metadata
            
        except Exception as e:
            print(f"⚠️  Lỗi khi query Last.fm: {e}")
        
        return None
    
    def get_metadata_from_musicbrainz(self, artist: str, track: str) -> Optional[SongMetadata]:
        """
        Lấy metadata từ MusicBrainz API
        
        Args:
            artist: Tên nghệ sĩ
            track: Tên bài hát
            
        Returns:
            SongMetadata hoặc None
        """
        print(f"🔍 Đang tìm metadata từ MusicBrainz: {artist} - {track}")
        
        try:
            # MusicBrainz API
            search_url = "https://musicbrainz.org/ws/2/recording/"
            params = {
                'query': f'artist:"{artist}" AND recording:"{track}"',
                'fmt': 'json',
                'limit': 1
            }
            
            headers = {
                'User-Agent': 'MusicCrawler/1.0 (https://example.com)',
                'Accept': 'application/json'
            }
            
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                recordings = data.get('recordings', [])
                
                if recordings:
                    recording = recordings[0]
                    releases = recording.get('releases', [])
                    
                    metadata = SongMetadata(
                        title=recording.get('title', track),
                        artist=artist,
                        year=None
                    )
                    
                    if releases:
                        release = releases[0]
                        metadata.album = release.get('title')
                        date = release.get('date')
                        if date:
                            try:
                                metadata.year = int(date.split('-')[0])
                            except:
                                pass
                    
                    print(f"✅ Tìm thấy trên MusicBrainz")
                    return metadata
            
        except Exception as e:
            print(f"⚠️  Lỗi khi query MusicBrainz: {e}")
        
        return None
    
    def download_cover_image(self, image_url: str, song_title: str, artist: str) -> Optional[str]:
        """
        Tải hình ảnh album cover
        
        Args:
            image_url: URL hình ảnh
            song_title: Tên bài hát (để đặt tên file)
            artist: Tên nghệ sĩ
            
        Returns:
            Đường dẫn file hình ảnh, hoặc None
        """
        if not image_url:
            return None
        
        try:
            print(f"🖼️  Đang tải cover image...")
            response = requests.get(image_url, timeout=10)
            
            if response.status_code == 200:
                # Tạo tên file
                safe_title = "".join(c for c in f"{artist}_{song_title}" if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_title = safe_title.replace(' ', '_')[:50]
                
                # Xác định extension
                ext = '.jpg'
                if 'png' in response.headers.get('content-type', ''):
                    ext = '.png'
                
                image_path = self.images_dir / f"{safe_title}{ext}"
                
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ Đã tải cover: {image_path.name}")
                return str(image_path)
            
        except Exception as e:
            print(f"⚠️  Lỗi khi tải cover image: {e}")
        
        return None
    
    def set_mp3_metadata(self, file_path: str, metadata: SongMetadata) -> bool:
        """
        Gán metadata vào file MP3
        
        Args:
            file_path: Đường dẫn file MP3
            metadata: Metadata cần gán
            
        Returns:
            True nếu thành công
        """
        if MP3 is None:
            print("⚠️  mutagen chưa được cài đặt, không thể gán metadata")
            return False
        
        try:
            audio = MP3(file_path, ID3=ID3)
            
            # Tạo ID3 tags nếu chưa có
            try:
                audio.add_tags()
            except:
                pass
            
            # Gán metadata
            if metadata.title:
                audio['TIT2'] = TIT2(encoding=3, text=metadata.title)
            if metadata.artist:
                audio['TPE1'] = TPE1(encoding=3, text=metadata.artist)
            if metadata.album:
                audio['TALB'] = TALB(encoding=3, text=metadata.album)
            if metadata.year:
                audio['TDRC'] = TDRC(encoding=3, text=str(metadata.year))
            if metadata.genre:
                audio['TCON'] = TCON(encoding=3, text=metadata.genre)
            if metadata.composer:
                audio['TCOM'] = TCOM(encoding=3, text=metadata.composer)
            if metadata.album_artist:
                audio['TPE2'] = TPE2(encoding=3, text=metadata.album_artist)
            
            # Gán cover image nếu có
            if metadata.cover_image_path and os.path.exists(metadata.cover_image_path):
                with open(metadata.cover_image_path, 'rb') as f:
                    audio['APIC'] = APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,  # Cover (front)
                        desc='Cover',
                        data=f.read()
                    )
            
            audio.save()
            print(f"✅ Đã gán metadata vào file")
            return True
            
        except Exception as e:
            print(f"⚠️  Lỗi khi gán metadata: {e}")
            return False
    
    def extract_mp3_metadata(self, file_path: str) -> Optional[SongMetadata]:
        """
        Trích xuất metadata từ file MP3 hiện có
        
        Args:
            file_path: Đường dẫn file MP3
            
        Returns:
            SongMetadata hoặc None
        """
        if MP3 is None:
            return None
        
        try:
            audio = MP3(file_path, ID3=ID3)
            
            metadata = SongMetadata(
                title=audio.get('TIT2', [None])[0] if 'TIT2' in audio else None,
                artist=audio.get('TPE1', [None])[0] if 'TPE1' in audio else None,
                album=audio.get('TALB', [None])[0] if 'TALB' in audio else None,
                year=int(audio.get('TDRC', [None])[0].text) if 'TDRC' in audio and audio['TDRC'][0].text else None,
                genre=audio.get('TCON', [None])[0] if 'TCON' in audio else None,
                composer=audio.get('TCOM', [None])[0] if 'TCOM' in audio else None,
                album_artist=audio.get('TPE2', [None])[0] if 'TPE2' in audio else None,
                duration=audio.info.length if hasattr(audio, 'info') else None,
                file_path=file_path
            )
            
            # Trích xuất cover image nếu có
            if 'APIC:' in audio:
                cover_data = audio['APIC:'].data
                cover_path = self.images_dir / f"{Path(file_path).stem}_cover.jpg"
                with open(cover_path, 'wb') as f:
                    f.write(cover_data)
                metadata.cover_image_path = str(cover_path)
            
            return metadata
            
        except Exception as e:
            print(f"⚠️  Lỗi khi trích xuất metadata: {e}")
            return None
    
    def enrich_metadata(self, metadata: SongMetadata) -> SongMetadata:
        """
        Làm giàu metadata bằng cách query các APIs
        
        Args:
            metadata: Metadata ban đầu
            
        Returns:
            Metadata đã được làm giàu
        """
        if not metadata.title or not metadata.artist:
            return metadata
        
        # Thử Last.fm
        lastfm_meta = self.get_metadata_from_lastfm(metadata.artist, metadata.title)
        if lastfm_meta:
            if not metadata.album and lastfm_meta.album:
                metadata.album = lastfm_meta.album
            if not metadata.cover_image_url and lastfm_meta.cover_image_url:
                metadata.cover_image_url = lastfm_meta.cover_image_url
        
        # Thử MusicBrainz
        musicbrainz_meta = self.get_metadata_from_musicbrainz(metadata.artist, metadata.title)
        if musicbrainz_meta:
            if not metadata.album and musicbrainz_meta.album:
                metadata.album = musicbrainz_meta.album
            if not metadata.year and musicbrainz_meta.year:
                metadata.year = musicbrainz_meta.year
        
        # Tải cover image nếu có URL
        if metadata.cover_image_url and not metadata.cover_image_path:
            cover_path = self.download_cover_image(
                metadata.cover_image_url,
                metadata.title,
                metadata.artist
            )
            if cover_path:
                metadata.cover_image_path = cover_path
        
        return metadata
    
    def save_metadata_json(self, metadata: SongMetadata, filename: str = None):
        """
        Lưu metadata ra file JSON
        
        Args:
            metadata: Metadata cần lưu
            filename: Tên file (nếu None sẽ tự động tạo)
        """
        if filename is None:
            safe_name = "".join(c for c in f"{metadata.artist}_{metadata.title}" if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')[:50]
            filename = f"{safe_name}.json"
        
        file_path = self.metadata_dir / filename
        
        # Convert to dict và loại bỏ None values
        metadata_dict = {k: v for k, v in asdict(metadata).items() if v is not None}
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Đã lưu metadata: {file_path.name}")
    
    def process_directory(self, directory: str, enrich: bool = True):
        """
        Xử lý tất cả file MP3 trong thư mục
        
        Args:
            directory: Thư mục chứa file MP3
            enrich: Có làm giàu metadata từ APIs không
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"❌ Thư mục không tồn tại: {directory}")
            return
        
        mp3_files = list(dir_path.glob('*.mp3')) + list(dir_path.glob('*.MP3'))
        
        print(f"📁 Tìm thấy {len(mp3_files)} file MP3")
        
        for i, mp3_file in enumerate(mp3_files, 1):
            print(f"\n[{i}/{len(mp3_files)}] Xử lý: {mp3_file.name}")
            
            # Trích xuất metadata
            metadata = self.extract_mp3_metadata(str(mp3_file))
            
            if metadata:
                # Làm giàu metadata nếu cần
                if enrich:
                    metadata = self.enrich_metadata(metadata)
                    # Cập nhật lại file MP3 với metadata mới
                    self.set_mp3_metadata(str(mp3_file), metadata)
                
                # Lưu metadata JSON
                self.save_metadata_json(metadata)
            else:
                print(f"⚠️  Không thể trích xuất metadata từ {mp3_file.name}")


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Music Crawler - Tải và quản lý dữ liệu nhạc MP3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:

1. Tải từ YouTube:
   python music_crawler.py --youtube "https://www.youtube.com/watch?v=VIDEO_ID"

2. Xử lý thư mục MP3:
   python music_crawler.py --directory ./music_folder

3. Trích xuất metadata từ file:
   python music_crawler.py --extract song.mp3
        """
    )
    
    parser.add_argument('--youtube', type=str, help='YouTube URL để tải')
    parser.add_argument('--directory', type=str, help='Thư mục chứa file MP3 cần xử lý')
    parser.add_argument('--extract', type=str, help='File MP3 để trích xuất metadata')
    parser.add_argument('--output', type=str, default='downloaded_music', help='Thư mục output (default: downloaded_music)')
    parser.add_argument('--no-enrich', action='store_true', help='Không làm giàu metadata từ APIs')
    
    args = parser.parse_args()
    
    crawler = MusicCrawler(output_dir=args.output)
    
    if args.youtube:
        # Tải từ YouTube
        file_path = crawler.download_from_youtube(args.youtube)
        if file_path:
            # Trích xuất và làm giàu metadata
            metadata = crawler.extract_mp3_metadata(file_path)
            if metadata and not args.no_enrich:
                metadata = crawler.enrich_metadata(metadata)
                crawler.set_mp3_metadata(file_path, metadata)
                crawler.save_metadata_json(metadata)
    
    elif args.directory:
        # Xử lý thư mục
        crawler.process_directory(args.directory, enrich=not args.no_enrich)
    
    elif args.extract:
        # Trích xuất từ file đơn
        metadata = crawler.extract_mp3_metadata(args.extract)
        if metadata:
            if not args.no_enrich:
                metadata = crawler.enrich_metadata(metadata)
            crawler.save_metadata_json(metadata)
            print("\n📋 Metadata:")
            print(json.dumps(asdict(metadata), indent=2, ensure_ascii=False, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

