# 🚀 QUICK START - Music Crawler

## Cài đặt nhanh

```bash
cd backend
pip install mutagen yt-dlp requests
brew install ffmpeg  # macOS
```

## Sử dụng cơ bản

### 1. Tải từ YouTube
```bash
python music_crawler.py --youtube "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 2. Xử lý thư mục MP3
```bash
python music_crawler.py --directory ./music_folder
```

### 3. Trích xuất metadata
```bash
python music_crawler.py --extract song.mp3
```

## Kết quả

Sau khi chạy, bạn sẽ có:
- ✅ File MP3 trong `downloaded_music/music/`
- ✅ Hình ảnh cover trong `downloaded_music/images/`
- ✅ Metadata JSON trong `downloaded_music/metadata/`

## Upload lên server

```bash
python batch_upload_songs.py downloaded_music/music
```

## Xem hướng dẫn chi tiết

Xem file `MUSIC_CRAWLER_GUIDE.md` để biết thêm chi tiết.





