# Hướng Dẫn Khởi Chạy Server Local và Kết Nối Từ Thiết Bị Thật

## 📋 Mục Lục
1. [Khởi Chạy Server Local](#1-khởi-chạy-server-local)
2. [Lấy Địa Chỉ IP Local](#2-lấy-địa-chỉ-ip-local)
3. [Kiểm Tra Server Đang Chạy](#3-kiểm-tra-server-đang-chạy)
4. [Kết Nối Từ Thiết Bị Thật](#4-kết-nối-từ-thiết-bị-thật)
5. [Xử Lý Sự Cố](#5-xử-lý-sự-cố)

---

## 1. Khởi Chạy Server Local

### Bước 1: Mở Terminal và Di Chuyển Đến Thư Mục Backend

```bash
cd "/Users/binhpham/Documents/Study/MSE/Xử lý tín hiệu số/FA25_MSA35_DSP501_G8_Final Projec/backend"
```

### Bước 2: Kích Hoạt Virtual Environment (Nếu Có)

```bash
# Nếu bạn đã tạo virtual environment
source venv/bin/activate  # macOS/Linux
# hoặc
venv\Scripts\activate  # Windows
```

### Bước 3: Cài Đặt Dependencies (Nếu Chưa Cài)

```bash
pip install -r requirements.txt
```

### Bước 4: Khởi Chạy Server

Có 2 cách để khởi chạy server:

#### Cách 1: Sử Dụng Python Script (Khuyến Nghị)

```bash
# Chạy từ thư mục backend
python3 app/main.py
```

Hoặc nếu có file `main.py` ở root:

```bash
python3 main.py
```

#### Cách 2: Sử Dụng Uvicorn Trực Tiếp

```bash
# Từ thư mục backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Kết Quả Mong Đợi

Bạn sẽ thấy output tương tự:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx]
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Lưu Ý Quan Trọng:**
- Server đang chạy trên `0.0.0.0` (tất cả network interfaces)
- Port: `8000`
- **KHÔNG đóng terminal này** - server sẽ dừng nếu bạn đóng

---

## 2. Lấy Địa Chỉ IP Local

Để thiết bị thật có thể kết nối, bạn cần biết địa chỉ IP của máy tính trên mạng WiFi.

### Trên macOS:

#### Cách 1: Sử Dụng Terminal

```bash
# Lấy IP của WiFi interface (thường là en0 hoặc en1)
ifconfig | grep "inet " | grep -v 127.0.0.1

# Hoặc cụ thể hơn:
ipconfig getifaddr en0  # WiFi interface
```

#### Cách 2: Sử Dụng System Preferences

1. Mở **System Preferences** (hoặc **System Settings** trên macOS mới)
2. Chọn **Network**
3. Chọn WiFi connection
4. Xem địa chỉ IP (thường là `192.168.x.x` hoặc `10.0.x.x`)

#### Cách 3: Sử Dụng Network Utility

```bash
# Lệnh đơn giản nhất
ifconfig en0 | grep inet
```

### Trên Windows:

```bash
# Mở Command Prompt hoặc PowerShell
ipconfig

# Tìm "Wireless LAN adapter Wi-Fi" hoặc "Ethernet adapter"
# Xem dòng "IPv4 Address" - đây là IP của bạn
```

### Trên Linux:

```bash
# Sử dụng ip command
ip addr show

# Hoặc
hostname -I
```

### Ví Dụ IP Thường Gặp:

- `192.168.1.100`
- `192.168.0.50`
- `10.0.0.5`
- `172.16.0.10`

**Lưu Ý:** IP này có thể thay đổi mỗi khi bạn kết nối lại WiFi. Hãy kiểm tra lại nếu không kết nối được.

---

## 3. Kiểm Tra Server Đang Chạy

### Kiểm Tra Trên Máy Tính:

#### Test 1: Kiểm Tra Localhost

Mở trình duyệt và truy cập:

```
http://localhost:8000
```

Hoặc:

```
http://127.0.0.1:8000
```

Bạn sẽ thấy JSON response:
```json
{
  "message": "Music Recognition API",
  "version": "1.0.0",
  "endpoints": {...}
}
```

#### Test 2: Kiểm Tra API Documentation

```
http://localhost:8000/docs
```

Đây là Swagger UI - bạn sẽ thấy tất cả các API endpoints.

#### Test 3: Kiểm Tra Bằng cURL

```bash
curl http://localhost:8000/
```

#### Test 4: Kiểm Tra Bằng IP Local

Thay `YOUR_IP` bằng IP bạn đã lấy ở bước 2:

```bash
curl http://YOUR_IP:8000/
```

Ví dụ:
```bash
curl http://192.168.1.100:8000/
```

### Kiểm Tra Firewall:

#### Trên macOS:

1. Mở **System Preferences** → **Security & Privacy** → **Firewall**
2. Đảm bảo Firewall không chặn Python hoặc Terminal
3. Nếu cần, click **Firewall Options** và thêm exception cho Python

#### Trên Windows:

1. Mở **Windows Defender Firewall**
2. Cho phép Python hoặc Uvicorn qua firewall
3. Hoặc tạm thời tắt firewall để test (chỉ trong môi trường local)

---

## 4. Kết Nối Từ Thiết Bị Thật

### Yêu Cầu:

1. ✅ Máy tính và thiết bị thật **cùng mạng WiFi**
2. ✅ Server đang chạy trên máy tính
3. ✅ Đã biết IP của máy tính
4. ✅ Firewall không chặn port 8000

### Bước 1: Cập Nhật Base URL Trong Flutter App

Bạn cần cập nhật base URL trong Flutter app để trỏ đến IP của máy tính.

#### Tìm File Cấu Hình:

Tìm file chứa base URL (thường là):
- `lib/core/constants/api_constants.dart`
- `lib/core/constants/constants.dart`
- Hoặc file tương tự trong `lib/core/constants/`

#### Cập Nhật URL:

Thay đổi từ:
```dart
static const String baseUrl = 'http://localhost:8000';
// hoặc
static const String baseUrl = 'http://127.0.0.1:8000';
```

Thành:
```dart
static const String baseUrl = 'http://YOUR_IP:8000';
```

**Ví dụ:**
```dart
static const String baseUrl = 'http://192.168.1.100:8000';
```

### Bước 2: Rebuild Flutter App

```bash
# Từ thư mục lynk
cd lynk
flutter clean
flutter pub get
flutter run
```

### Bước 3: Test Kết Nối

#### Test 1: Từ Trình Duyệt Trên Thiết Bị

Mở trình duyệt trên thiết bị thật (Safari/Chrome) và truy cập:

```
http://YOUR_IP:8000
```

Ví dụ:
```
http://192.168.1.100:8000
```

Nếu thấy JSON response → Server đang hoạt động!

#### Test 2: Test API Endpoint

```
http://YOUR_IP:8000/stats
```

#### Test 3: Test Từ Flutter App

Chạy app trên thiết bị và thử các chức năng:
- Upload bài hát (`/learn`)
- Nhận diện bài hát (`/recognize`)
- Xem danh sách bài hát (`/songs`)

---

## 5. Xử Lý Sự Cố

### Vấn Đề 1: Không Kết Nối Được Từ Thiết Bị

#### Kiểm Tra:

1. **Cùng mạng WiFi?**
   ```bash
   # Trên máy tính, ping thiết bị
   ping <device_ip>
   ```

2. **Server đang chạy?**
   ```bash
   # Kiểm tra process
   lsof -i :8000
   # hoặc
   netstat -an | grep 8000
   ```

3. **Firewall chặn?**
   - Tạm thời tắt firewall để test
   - Hoặc thêm exception cho port 8000

4. **IP đúng chưa?**
   - Kiểm tra lại IP: `ifconfig` hoặc `ipconfig`
   - Đảm bảo IP không thay đổi

5. **URL trong app đúng chưa?**
   - Kiểm tra lại base URL trong Flutter code
   - Đảm bảo không có `localhost` hoặc `127.0.0.1`

### Vấn Đề 2: Connection Refused

**Nguyên nhân:** Server không lắng nghe trên interface đó

**Giải pháp:**
- Đảm bảo server chạy với `--host 0.0.0.0`
- Kiểm tra file `app/main.py` có dòng:
  ```python
  uvicorn.run(..., host="0.0.0.0", ...)
  ```

### Vấn Đề 3: Timeout

**Nguyên nhân:** Firewall hoặc network issue

**Giải pháp:**
1. Kiểm tra firewall settings
2. Thử ping từ thiết bị đến máy tính
3. Kiểm tra router không chặn local traffic

### Vấn Đề 4: CORS Error

**Nguyên nhân:** CORS middleware chưa được cấu hình đúng

**Kiểm tra:**
- File `app/main.py` có CORS middleware:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      ...
  )
  ```

### Vấn Đề 5: IP Thay Đổi

**Giải pháp:**
- Ghi nhớ IP mới mỗi lần kết nối WiFi
- Hoặc cấu hình static IP trong router settings
- Hoặc sử dụng hostname (nếu router hỗ trợ)

---

## 📝 Checklist Nhanh

Trước khi test:

- [ ] Server đang chạy (`python3 app/main.py`)
- [ ] Server hiển thị: `Uvicorn running on http://0.0.0.0:8000`
- [ ] Đã lấy IP local của máy tính
- [ ] Test thành công `http://localhost:8000` trên máy tính
- [ ] Test thành công `http://YOUR_IP:8000` trên máy tính
- [ ] Máy tính và thiết bị cùng WiFi
- [ ] Firewall không chặn port 8000
- [ ] Đã cập nhật base URL trong Flutter app
- [ ] Đã rebuild Flutter app
- [ ] Test `http://YOUR_IP:8000` trên trình duyệt thiết bị

---

## 🔧 Tips & Tricks

### 1. Tạo Script Khởi Động Nhanh

Tạo file `start_server.sh`:

```bash
#!/bin/bash
cd "/Users/binhpham/Documents/Study/MSE/Xử lý tín hiệu số/FA25_MSA35_DSP501_G8_Final Projec/backend"
source venv/bin/activate  # Nếu có venv
python3 app/main.py
```

Chạy:
```bash
chmod +x start_server.sh
./start_server.sh
```

### 2. Hiển Thị IP Tự Động

Thêm vào script khởi động:

```bash
echo "Server starting..."
echo "Your local IP: $(ipconfig getifaddr en0)"
echo "Access at: http://$(ipconfig getifaddr en0):8000"
```

### 3. Sử Dụng Ngrok (Nếu Cần Test Từ Xa)

Nếu muốn test từ mạng khác (không cùng WiFi):

```bash
# Cài đặt ngrok
brew install ngrok  # macOS
# hoặc download từ ngrok.com

# Tạo tunnel
ngrok http 8000
```

Ngrok sẽ cung cấp URL công khai (ví dụ: `https://abc123.ngrok.io`)

**Lưu Ý:** Chỉ dùng cho testing, không dùng cho production!

---

## 📞 Test API Từ Thiết Bị

### Sử Dụng Postman/Insomnia Trên Thiết Bị:

1. Cài app Postman hoặc Insomnia trên thiết bị
2. Tạo request mới
3. URL: `http://YOUR_IP:8000/stats`
4. Method: GET
5. Send request

### Sử Dụng cURL Từ Terminal (Nếu Có SSH):

```bash
curl http://YOUR_IP:8000/stats
```

---

## ✅ Kết Luận

Sau khi hoàn thành các bước trên:

1. ✅ Server chạy trên máy tính
2. ✅ Thiết bị thật có thể truy cập `http://YOUR_IP:8000`
3. ✅ Flutter app kết nối thành công
4. ✅ Có thể test tất cả API endpoints

**Lưu Ý:** Mỗi lần kết nối WiFi mới, hãy kiểm tra lại IP và cập nhật trong Flutter app nếu cần.

