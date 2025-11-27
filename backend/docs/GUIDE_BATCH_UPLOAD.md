# Hướng Dẫn Tạo Dữ Liệu Bài Hát Từ Danh Sách Có Sẵn

## 📋 Tổng Quan

Hướng dẫn này giúp bạn tự động upload nhiều bài hát vào database từ một thư mục chứa file audio.

---

## 🎯 Các Cách Tạo Dữ Liệu

### Cách 1: Upload Tự Động Từ Thư Mục (Đơn Giản Nhất)

**Bước 1:** Chuẩn bị thư mục chứa file audio
```bash
mkdir -p ~/Music/songs
# Copy các file .wav, .mp3 vào thư mục này
```

**Bước 2:** Chạy script batch upload
```bash
cd backend
source venv/bin/activate
python3 batch_upload_songs.py ~/Music/songs
```

**Kết quả:**
- Script sẽ tự động:
  - Tìm tất cả file audio (.wav, .mp3, .m4a, .flac)
  - Tự động đặt tên bài hát từ tên file
  - Upload từng file lên server
  - Hiển thị progress và kết quả

---

### Cách 2: Upload Với Tên Bài Hát Tùy Chỉnh

**Bước 1:** Tạo file mapping (tùy chọn)
```bash
# Tự động tạo mapping từ tên file
python3 create_song_mapping.py ~/Music/songs

# Hoặc tạo thủ công file song_mapping.json:
```

**Format file `song_mapping.json`:**
```json
{
  "song1.mp3": "Tên Bài Hát 1",
  "song2.wav": "Tên Bài Hát 2",
  "artist - song.mp3": "Song Name - Artist Name"
}
```

**Bước 2:** Upload với mapping
```bash
python3 batch_upload_songs.py ~/Music/songs --mapping song_mapping.json
```

---

### Cách 3: Upload Từ Danh Sách File

**Bước 1:** Tạo file danh sách
```bash
# Tạo file list_songs.txt
cat > list_songs.txt << EOF
/path/to/song1.mp3|Song Name 1
/path/to/song2.wav|Song Name 2
/path/to/song3.mp3|Song Name 3
EOF
```

**Bước 2:** Sử dụng script Python
```python
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000"

with open('list_songs.txt', 'r') as f:
    for line in f:
        file_path, song_name = line.strip().split('|')
        
        with open(file_path, 'rb') as audio_file:
            files = {'file': (Path(file_path).name, audio_file, 'audio/mpeg')}
            data = {'song_name': song_name}
            
            response = requests.post(
                f"{BASE_URL}/learn",
                files=files,
                data=data
            )
            
            print(f"{song_name}: {response.json()}")
```

---

## 📝 Ví Dụ Cụ Thể

### Ví Dụ 1: Upload Từ Thư Mục Test

```bash
# 1. Đảm bảo server đang chạy
cd backend
source venv/bin/activate
python3 main.py &
# (Server chạy ở background)

# 2. Upload từ thư mục test_data
python3 batch_upload_songs.py test_data

# Kết quả:
# ✅ Uploaded test_song_1.wav → Test_Song_1 (6166 fingerprints)
# ✅ Uploaded test_song_2.wav → Test_Song_2 (2368 fingerprints)
```

### Ví Dụ 2: Upload Với Tên Tùy Chỉnh

```bash
# 1. Tạo mapping file
python3 create_song_mapping.py ~/Music/my_songs

# 2. Chỉnh sửa song_mapping.json nếu cần
nano ~/Music/my_songs/song_mapping.json

# 3. Upload với mapping
python3 batch_upload_songs.py ~/Music/my_songs --mapping ~/Music/my_songs/song_mapping.json
```

### Ví Dụ 3: Upload Từ Nhiều Thư Mục

```bash
# Tạo script upload nhiều thư mục
cat > upload_all.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate

python3 batch_upload_songs.py ~/Music/pop_songs
python3 batch_upload_songs.py ~/Music/rock_songs
python3 batch_upload_songs.py ~/Music/jazz_songs
EOF

chmod +x upload_all.sh
./upload_all.sh
```

---

## 🔧 Tùy Chỉnh Script

### Thay Đổi API URL

```python
# Trong batch_upload_songs.py hoặc khi chạy:
python3 batch_upload_songs.py ~/Music/songs --url http://192.168.1.100:8000
```

### Lọc File Theo Extension

Sửa trong `batch_upload_songs.py`:
```python
extensions = ['.wav', '.mp3']  # Chỉ upload WAV và MP3
```

### Thêm Delay Giữa Các Upload

Sửa trong `batch_upload_songs.py`:
```python
time.sleep(2)  # Delay 2 giây giữa mỗi file
```

---

## 📊 Kiểm Tra Kết Quả

### Xem Database Stats

```bash
curl http://localhost:8000/stats | python3 -m json.tool
```

### Xem Danh Sách Bài Hát

```bash
curl http://localhost:8000/songs | python3 -m json.tool
```

### Test Recognition

```bash
# Upload một file test
curl -X POST "http://localhost:8000/recognize" \
  -F "file=@test_recording.wav" | python3 -m json.tool
```

---

## ⚠️ Lưu Ý

### 1. File Format
- ✅ Hỗ trợ: WAV, MP3, M4A, FLAC
- ⚠️ File phải có chất lượng tốt (không bị méo)
- ⚠️ File quá lớn (>100MB) có thể mất nhiều thời gian

### 2. Tên Bài Hát
- Tên bài hát sẽ được dùng làm ID trong database
- Nên dùng tên unique cho mỗi bài hát
- Tránh ký tự đặc biệt: `/, \, :, *, ?, ", <, >, |`

### 3. Server Performance
- Upload nhiều file lớn có thể làm server chậm
- Nên upload từng batch nhỏ (10-20 files)
- Có thể tăng timeout nếu file lớn

### 4. Storage
- Database hiện tại là in-memory
- Mất dữ liệu khi restart server
- Nên backup hoặc export database định kỳ

---

## 🚀 Workflow Khuyến Nghị

### 1. Chuẩn Bị
```bash
# Tạo thư mục chứa bài hát
mkdir -p ~/Music/database_songs

# Copy file audio vào thư mục
cp *.mp3 ~/Music/database_songs/
```

### 2. Tạo Mapping (Tùy chọn)
```bash
cd backend
source venv/bin/activate
python3 create_song_mapping.py ~/Music/database_songs
# Chỉnh sửa song_mapping.json nếu cần
```

### 3. Upload
```bash
# Đảm bảo server đang chạy
python3 main.py &

# Upload
python3 batch_upload_songs.py ~/Music/database_songs --mapping ~/Music/database_songs/song_mapping.json
```

### 4. Verify
```bash
# Kiểm tra stats
curl http://localhost:8000/stats | python3 -m json.tool

# Test recognition
python3 test_data/test_upload_wav.py
```

---

## 📁 Cấu Trúc File

```
backend/
├── batch_upload_songs.py      # Script upload batch
├── create_song_mapping.py     # Script tạo mapping
├── test_data/
│   ├── test_song_1.wav
│   ├── test_song_2.wav
│   └── song_mapping.json      # Mapping file (optional)
└── GUIDE_BATCH_UPLOAD.md      # File này
```

---

## 💡 Tips

1. **Đặt tên file rõ ràng:**
   - `Artist - Song Name.mp3` → Tự động extract được artist và song
   - `01 Song Name.mp3` → Sẽ loại bỏ số track

2. **Upload theo batch:**
   - Upload 10-20 files mỗi lần
   - Kiểm tra stats sau mỗi batch

3. **Backup database:**
   - Export stats định kỳ
   - Lưu danh sách bài hát đã upload

4. **Monitor server:**
   - Xem logs khi upload
   - Kiểm tra memory usage nếu upload nhiều

---

## 🐛 Troubleshooting

### Lỗi: "Connection refused"
- Đảm bảo server đang chạy: `curl http://localhost:8000/`

### Lỗi: "Timeout"
- File quá lớn, tăng timeout trong script
- Hoặc giảm kích thước file

### Lỗi: "Failed to generate fingerprints"
- File có thể bị hỏng hoặc format không đúng
- Thử convert sang WAV 22050Hz mono

### Lỗi: "No module named 'soundfile'"
- Cài đặt: `pip install soundfile`

---

## 📚 Tài Liệu Tham Khảo

- [API Documentation](./README.md)
- [Server Architecture](../SERVER_ARCHITECTURE.md)
- [Test Scripts](./test_data/README.md)

