#!/usr/bin/env python3
"""
Ví dụ sử dụng Music Crawler
"""

from music_crawler import MusicCrawler, SongMetadata
from pathlib import Path

def example_1_download_from_youtube():
    """Ví dụ 1: Tải từ YouTube"""
    print("=" * 60)
    print("VÍ DỤ 1: Tải MP3 từ YouTube")
    print("=" * 60)
    
    crawler = MusicCrawler(output_dir='./downloaded_music')
    
    # Tải từ YouTube
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Thay bằng URL thật
    file_path = crawler.download_from_youtube(youtube_url)
    
    if file_path:
        print(f"✅ Đã tải thành công: {file_path}")
        
        # Trích xuất metadata
        metadata = crawler.extract_mp3_metadata(file_path)
        if metadata:
            print(f"📋 Metadata: {metadata.title} - {metadata.artist}")


def example_2_enrich_metadata():
    """Ví dụ 2: Làm giàu metadata"""
    print("\n" + "=" * 60)
    print("VÍ DỤ 2: Làm giàu metadata từ APIs")
    print("=" * 60)
    
    crawler = MusicCrawler()
    
    # Tạo metadata ban đầu
    metadata = SongMetadata(
        title="Bohemian Rhapsody",
        artist="Queen"
    )
    
    # Làm giàu từ APIs
    enriched = crawler.enrich_metadata(metadata)
    
    print(f"📋 Metadata sau khi làm giàu:")
    print(f"   Title: {enriched.title}")
    print(f"   Artist: {enriched.artist}")
    print(f"   Album: {enriched.album}")
    print(f"   Year: {enriched.year}")
    print(f"   Cover: {enriched.cover_image_path}")


def example_3_process_directory():
    """Ví dụ 3: Xử lý thư mục"""
    print("\n" + "=" * 60)
    print("VÍ DỤ 3: Xử lý thư mục MP3")
    print("=" * 60)
    
    crawler = MusicCrawler()
    
    # Xử lý tất cả file MP3 trong thư mục
    music_folder = "./music_folder"  # Thay bằng đường dẫn thật
    
    if Path(music_folder).exists():
        crawler.process_directory(music_folder, enrich=True)
    else:
        print(f"⚠️  Thư mục không tồn tại: {music_folder}")


def example_4_extract_from_file():
    """Ví dụ 4: Trích xuất từ file đơn"""
    print("\n" + "=" * 60)
    print("VÍ DỤ 4: Trích xuất metadata từ file")
    print("=" * 60)
    
    crawler = MusicCrawler()
    
    # Trích xuất metadata
    mp3_file = "./song.mp3"  # Thay bằng đường dẫn file thật
    
    if Path(mp3_file).exists():
        metadata = crawler.extract_mp3_metadata(mp3_file)
        
        if metadata:
            print(f"📋 Metadata:")
            print(f"   Title: {metadata.title}")
            print(f"   Artist: {metadata.artist}")
            print(f"   Album: {metadata.album}")
            print(f"   Year: {metadata.year}")
            print(f"   Duration: {metadata.duration:.2f}s")
            
            # Lưu ra JSON
            crawler.save_metadata_json(metadata)
    else:
        print(f"⚠️  File không tồn tại: {mp3_file}")


def example_5_batch_download():
    """Ví dụ 5: Tải hàng loạt từ danh sách"""
    print("\n" + "=" * 60)
    print("VÍ DỤ 5: Tải hàng loạt từ danh sách")
    print("=" * 60)
    
    crawler = MusicCrawler()
    
    # Danh sách YouTube URLs
    youtube_urls = [
        "https://www.youtube.com/watch?v=VIDEO1",
        "https://www.youtube.com/watch?v=VIDEO2",
        "https://www.youtube.com/watch?v=VIDEO3",
    ]
    
    print(f"📥 Sẽ tải {len(youtube_urls)} bài hát...")
    
    for i, url in enumerate(youtube_urls, 1):
        print(f"\n[{i}/{len(youtube_urls)}] Đang tải...")
        file_path = crawler.download_from_youtube(url)
        
        if file_path:
            # Làm giàu metadata
            metadata = crawler.extract_mp3_metadata(file_path)
            if metadata:
                metadata = crawler.enrich_metadata(metadata)
                crawler.set_mp3_metadata(file_path, metadata)
                crawler.save_metadata_json(metadata)


def example_6_custom_metadata():
    """Ví dụ 6: Gán metadata tùy chỉnh"""
    print("\n" + "=" * 60)
    print("VÍ DỤ 6: Gán metadata tùy chỉnh")
    print("=" * 60)
    
    crawler = MusicCrawler()
    
    # Tạo metadata tùy chỉnh
    custom_metadata = SongMetadata(
        title="My Custom Song",
        artist="My Artist",
        album="My Album",
        year=2024,
        genre="Pop",
        composer="Composer Name",
        album_artist="Album Artist",
        track_number=1
    )
    
    # Tải cover image
    cover_url = "https://example.com/cover.jpg"  # Thay bằng URL thật
    cover_path = crawler.download_cover_image(
        cover_url,
        custom_metadata.title,
        custom_metadata.artist
    )
    
    if cover_path:
        custom_metadata.cover_image_path = cover_path
    
    # Gán vào file MP3 (cần có file MP3 trước)
    mp3_file = "./song.mp3"  # Thay bằng đường dẫn file thật
    
    if Path(mp3_file).exists():
        success = crawler.set_mp3_metadata(mp3_file, custom_metadata)
        if success:
            print("✅ Đã gán metadata thành công")
        
        # Lưu metadata JSON
        crawler.save_metadata_json(custom_metadata)
    else:
        print(f"⚠️  File không tồn tại: {mp3_file}")


if __name__ == "__main__":
    print("🎵 VÍ DỤ SỬ DỤNG MUSIC CRAWLER\n")
    
    # Chạy các ví dụ (bỏ comment để chạy)
    
    # example_1_download_from_youtube()
    # example_2_enrich_metadata()
    # example_3_process_directory()
    # example_4_extract_from_file()
    # example_5_batch_download()
    # example_6_custom_metadata()
    
    print("\n" + "=" * 60)
    print("💡 Bỏ comment trong code để chạy các ví dụ")
    print("=" * 60)

