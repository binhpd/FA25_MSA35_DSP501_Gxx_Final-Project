# Lynk Desktop - Ứng dụng nhận diện bài hát trên Desktop

Ứng dụng desktop Python để ghi âm và nhận diện bài hát, tương tự như ứng dụng Flutter mobile.

## Tính năng

- 🎤 **Ghi âm**: Ghi âm 10 giây để nhận diện bài hát
- 🔍 **Nhận diện**: Gửi file âm thanh lên server để nhận diện
- 📊 **Hiển thị kết quả**: Hiển thị tên bài hát, độ chính xác và số matches
- 🎨 **Giao diện đẹp**: UI hiện đại với tkinter

## Yêu cầu

- Python 3.7 trở lên
- Backend server đang chạy (port 8000)
- Microphone để ghi âm

## Cài đặt

### 1. Tạo virtual environment (khuyến nghị)

```bash
cd lynk_desktop
python3 -m venv venv
source venv/bin/activate  # Trên macOS/Linux
# hoặc
venv\Scripts\activate  # Trên Windows
```

### 2. Cài đặt dependencies

**Trên macOS:**

```bash
# Cài đặt PortAudio (bắt buộc)
brew install portaudio

# Cài đặt Python packages
pip install -r requirements.txt
```

**Trên Linux (Ubuntu/Debian):**

```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install -r requirements.txt
```

**Trên Windows:**

```bash
pip install -r requirements.txt
```

### 2. Đảm bảo backend server đang chạy

Backend server phải đang chạy trên `http://localhost:8000`. 

Để khởi động backend:
```bash
cd ../backend
python -m app.main
```

## Sử dụng

### Chạy ứng dụng

**Cách 1: Sử dụng script (khuyến nghị)**

```bash
./run.sh
```

**Cách 2: Chạy thủ công**

```bash
# Kích hoạt virtual environment
source venv/bin/activate  # macOS/Linux
# hoặc
venv\Scripts\activate  # Windows

# Chạy ứng dụng
python main.py
```

**Cách 3: Test kết nối trước**

```bash
source venv/bin/activate
python test_connection.py  # Kiểm tra backend server
python main.py             # Chạy ứng dụng
```

### Quy trình sử dụng

1. **Khởi động ứng dụng**: Chạy `python main.py`
2. **Ghi âm**: Nhấn nút "🎤 Ghi âm" để bắt đầu ghi âm
   - Ứng dụng sẽ tự động ghi âm trong 10 giây
   - Bạn có thể nhấn "⏹ Dừng" để dừng sớm hơn
3. **Nhận diện**: Sau khi ghi âm xong, file sẽ tự động được gửi lên server
4. **Xem kết quả**: Kết quả sẽ hiển thị:
   - Tên bài hát
   - Độ chính xác (%)
   - Số matches
5. **Ghi âm lại**: Nhấn "Ghi âm lại" để thử lại

## Cấu trúc project

```
lynk_desktop/
├── main.py              # Main application với UI
├── audio_recorder.py    # Module ghi âm
├── api_client.py        # Module giao tiếp với API
├── config.py            # File cấu hình
├── requirements.txt     # Dependencies
├── .gitignore          # Git ignore file
├── test_connection.py   # Script test kết nối
├── run.sh              # Script chạy ứng dụng
├── TROUBLESHOOTING.md  # Hướng dẫn xử lý lỗi
└── README.md           # Tài liệu này
```

## Cấu hình

Tất cả cấu hình được quản lý trong file `config.py`:

### Thay đổi server URL

Mặc định ứng dụng kết nối đến `http://localhost:8000`. 

Để thay đổi, sửa trong `config.py`:

```python
SERVER_HOST = "your-server-ip"
SERVER_PORT = 8000
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"
```

### Thay đổi thời gian ghi âm

Mặc định ghi âm 10 giây. Để thay đổi:

```python
RECORDING_DURATION = 15  # seconds
```

### Thay đổi màu sắc UI

```python
PRIMARY_COLOR = "#673AB7"  # Màu chính
SUCCESS_COLOR = "#4CAF50"   # Màu thành công
ERROR_COLOR = "#F44336"     # Màu lỗi
ACCENT_COLOR = "#FF9800"    # Màu nhấn
```

### Thay đổi kích thước cửa sổ

```python
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700
```

## Xử lý lỗi

### Lỗi: "Cannot connect to server"
- Đảm bảo backend server đang chạy
- Kiểm tra URL trong `api_client.py`
- Kiểm tra firewall/network settings

### Lỗi: "No module named 'pyaudio'"
- Cài đặt lại PyAudio: `pip install pyaudio`
- Trên macOS: `brew install portaudio` trước
- Trên Linux: `sudo apt-get install portaudio19-dev`

### Lỗi: "Cannot record audio" hoặc "[Errno -9986] Internal PortAudio error"

**Trên macOS:**
1. Cấp quyền truy cập microphone:
   - System Settings > Privacy & Security > Microphone
   - Bật quyền cho Terminal/Python/IDE bạn đang dùng
2. Đảm bảo không có ứng dụng khác đang dùng microphone
3. Khởi động lại ứng dụng

Xem thêm chi tiết trong [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Lỗi: "No matching song found"
- Đảm bảo database có bài hát (sử dụng `/learn` endpoint)
- Thử ghi âm lại với âm thanh rõ hơn
- Kiểm tra xem bài hát có trong database không

### Lỗi: "500 Internal Server Error"

Khi server trả về lỗi 500, ứng dụng sẽ hiển thị thông báo chi tiết. Xem [ERROR_HANDLING.md](ERROR_HANDLING.md) để biết cách xử lý.

### Lỗi: "404 Not Found"

Khi server trả về lỗi 404, có nghĩa là endpoint `/recognize` không tồn tại.

**Nguyên nhân:**
- Backend server không có endpoint này
- URL server không đúng

**Giải pháp:**
1. Kiểm tra endpoint: `curl http://localhost:8000/`
2. Kiểm tra URL trong `config.py`
3. Đảm bảo backend server đang chạy phiên bản đúng
4. Xem [ERROR_HANDLING.md](ERROR_HANDLING.md) để biết chi tiết

**Nguyên nhân thường gặp:**
- File audio không hợp lệ
- Server đang gặp sự cố
- Database có vấn đề

**Giải pháp:**
1. Kiểm tra logs server
2. Thử với file audio khác
3. Khởi động lại server

## So sánh với Flutter app

| Tính năng | Flutter App | Desktop App |
|-----------|-------------|-------------|
| Ghi âm | ✅ | ✅ |
| Gửi lên server | ✅ | ✅ |
| Hiển thị kết quả | ✅ | ✅ |
| Animation | ✅ | ⚠️ (Cơ bản) |
| Spotify/YouTube links | ✅ | ❌ (Có thể thêm) |

## Phát triển thêm

Các tính năng có thể thêm:

- [ ] Thêm links Spotify/YouTube
- [ ] Hiển thị lịch sử nhận diện
- [ ] Cho phép chọn file audio từ máy tính
- [ ] Cấu hình thời gian ghi âm
- [ ] Hiển thị waveform khi ghi âm
- [ ] Dark mode

## License

Cùng license với project chính.

