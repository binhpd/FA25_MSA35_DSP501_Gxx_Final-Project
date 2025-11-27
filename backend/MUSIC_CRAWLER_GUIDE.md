# 🎵 HƯỚNG DẪN CRAWL DỮ LIỆU NHẠC MP3

## 📋 Tổng Quan

Script `music_crawler.py` giúp bạn:
- ✅ Tải file MP3 từ YouTube
- ✅ Trích xuất metadata từ file MP3 hiện có
- ✅ Lấy thông tin bổ sung từ APIs (Last.fm, MusicBrainz)
- ✅ Tải hình ảnh album cover
- ✅ Tổ chức file với metadata đầy đủ

## 🔧 Cài Đặt

### 1. Cài đặt Python packages

```bash
cd backend
pip install -r requirements.txt
pip install mutagen yt-dlp requests
```

Hoặc cài đặt riêng:
```bash
pip install mutagen  # Để đọc/ghi metadata MP3
pip install yt-dlp   # Để tải từ YouTube
pip install requests # Để query APIs
```

### 2. Cài đặt FFmpeg (cần cho yt-dlp)

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Tải từ https://ffmpeg.org/download.html

## 🚀 Cách Sử Dụng

### 1. Tải MP3 từ YouTube

```bash
python music_crawler.py --youtube "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Ví dụ:**
```bash
python music_crawler.py --youtube "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

Script sẽ:
- Tải video từ YouTube
- Chuyển đổi sang MP3 (192kbps)
- Tự động trích xuất metadata từ YouTube
- Lưu vào thư mục `downloaded_music/music/`

### 2. Trích xuất metadata từ file MP3 hiện có

```bash
python music_crawler.py --extract path/to/song.mp3
```

Hoặc xử lý toàn bộ thư mục:
```bash
python music_crawler.py --directory ./my_music_folder
```

### 3. Làm giàu metadata từ APIs

Mặc định, script sẽ tự động query các APIs để bổ sung thông tin:
- Album name
- Release year
- Genre
- Cover image

Để tắt tính năng này:
```bash
python music_crawler.py --directory ./music --no-enrich
```

### 4. Tùy chỉnh thư mục output

```bash
python music_crawler.py --youtube "URL" --output ./my_output_folder
```

## 📁 Cấu Trúc Thư Mục Output

```
downloaded_music/
├── music/           # File MP3 đã tải
│   ├── song1.mp3
│   └── song2.mp3
├── images/          # Hình ảnh album cover
│   ├── artist_song1.jpg
│   └── artist_song2.jpg
└── metadata/        # File JSON chứa metadata
    ├── artist_song1.json
    └── artist_song2.json
```

## 📊 Cấu Trúc Metadata

File JSON metadata có dạng:

```json
{
  "title": "Tên bài hát",
  "artist": "Tên nghệ sĩ",
  "album": "Tên album",
  "year": 2023,
  "genre": "Pop",
  "composer": "Tên nhạc sĩ",
  "album_artist": "Nghệ sĩ album",
  "track_number": 1,
  "cover_image_url": "https://...",
  "cover_image_path": "./images/artist_song.jpg",
  "spotify_url": "https://...",
  "youtube_url": "https://...",
  "duration": 180.5,
  "file_path": "./music/song.mp3"
}
```

## 🔍 Các Nguồn Metadata

### 1. Last.fm API
- Tìm kiếm bài hát
- Lấy thông tin album
- Hình ảnh cover

**Lưu ý:** Có thể cần API key cho một số tính năng nâng cao.

### 2. MusicBrainz API
- Thông tin chi tiết về bài hát
- Năm phát hành
- Thông tin album

**Lưu ý:** Cần User-Agent hợp lệ (đã được cấu hình sẵn).

### 3. Từ file MP3 (ID3 tags)
- Title, Artist, Album
- Year, Genre
- Composer, Album Artist
- Cover image (nếu có)

## 💡 Ví Dụ Sử Dụng Nâng Cao

### 1. Tải nhiều bài hát từ YouTube

Tạo file `download_list.txt`:
```
https://www.youtube.com/watch?v=VIDEO1
https://www.youtube.com/watch?v=VIDEO2
https://www.youtube.com/watch?v=VIDEO3
```

Script Python:
```python
from music_crawler import MusicCrawler

crawler = MusicCrawler()

with open('download_list.txt', 'r') as f:
    for url in f:
        url = url.strip()
        if url:
            crawler.download_from_youtube(url)
```

### 2. Xử lý và làm giàu metadata hàng loạt

```python
from music_crawler import MusicCrawler

crawler = MusicCrawler(output_dir='./my_music')

# Xử lý thư mục
crawler.process_directory('./music_folder', enrich=True)
```

### 3. Tích hợp với hệ thống nhận diện nhạc

Sau khi tải và có metadata, upload lên server:

```bash
# Tải từ YouTube
python music_crawler.py --youtube "URL" --output ./songs

# Upload lên server
python batch_upload_songs.py ./songs/music
```

## ⚠️ Lưu Ý Quan Trọng

### 1. Bản quyền
- Chỉ tải nhạc cho mục đích cá nhân và học tập
- Tuân thủ Terms of Service của YouTube
- Không phân phối lại file đã tải

### 2. Chất lượng audio
- Mặc định: 192kbps MP3
- Có thể chỉnh trong code: `'preferredquality': '192'` → `'320'` hoặc `'best'`

### 3. Rate limiting
- APIs có giới hạn số request
- Script tự động delay giữa các request
- Nếu gặp lỗi 429 (Too Many Requests), đợi vài phút

### 4. FFmpeg
- Bắt buộc phải có FFmpeg để chuyển đổi audio
- Kiểm tra: `ffmpeg -version`

## 🐛 Xử Lý Lỗi

### Lỗi: "yt-dlp chưa được cài đặt"
```bash
pip install yt-dlp
```

### Lỗi: "mutagen chưa được cài đặt"
```bash
pip install mutagen
```

### Lỗi: "FFmpeg not found"
- Cài đặt FFmpeg (xem phần Cài Đặt)
- Đảm bảo FFmpeg trong PATH

### Lỗi: "No matching song found"
- Kiểm tra tên bài hát và nghệ sĩ
- Thử tìm kiếm thủ công trên Last.fm/MusicBrainz

## 📚 Tài Liệu Tham Khảo

- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [mutagen Documentation](https://mutagen.readthedocs.io/)
- [Last.fm API](https://www.last.fm/api)
- [MusicBrainz API](https://musicbrainz.org/doc/MusicBrainz_API)

## 🔄 Tích Hợp Với Hệ Thống Hiện Tại

Sau khi crawl dữ liệu, bạn có thể:

1. **Upload lên database nhận diện:**
```bash
python batch_upload_songs.py downloaded_music/music
```

2. **Sử dụng metadata trong Flutter app:**
- Đọc file JSON từ `metadata/`
- Hiển thị thông tin bài hát
- Load hình ảnh từ `images/`

3. **Tạo mapping file:**
```python
import json
from pathlib import Path

metadata_dir = Path('downloaded_music/metadata')
mapping = {}

for json_file in metadata_dir.glob('*.json'):
    with open(json_file) as f:
        data = json.load(f)
        # Tạo mapping file_name -> song_name
        # ...

with open('song_mapping.json', 'w') as f:
    json.dump(mapping, f, indent=2)
```

## 🎯 Best Practices

1. **Tổ chức file:**
   - Đặt tên file rõ ràng: `Artist_Title.mp3`
   - Lưu metadata JSON cùng tên với file MP3

2. **Metadata:**
   - Luôn làm giàu metadata từ APIs
   - Kiểm tra và sửa metadata thủ công nếu cần
   - Lưu cover image với chất lượng tốt

3. **Backup:**
   - Backup thư mục `downloaded_music/` định kỳ
   - Lưu file JSON metadata riêng

4. **Performance:**
   - Xử lý theo batch để tránh quá tải
   - Sử dụng `--no-enrich` nếu chỉ cần metadata cơ bản





