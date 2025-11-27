# 📱 Hướng dẫn kết nối Android Device đến Backend Local

## 🎯 Tổng quan

Khi phát triển Flutter app với backend local, bạn cần cấu hình URL khác nhau tùy thuộc vào:
- **Android Emulator**: Sử dụng `10.0.2.2` thay cho `localhost`
- **Android Physical Device**: Sử dụng IP address của máy tính
- **iOS Simulator**: Sử dụng `127.0.0.1`

## 🔧 Cách 1: Tự động detect (Đã được cấu hình)

Code đã được cập nhật để tự động detect platform. Mặc định:
- **Android Emulator**: `http://10.0.2.2:8000`
- **iOS Simulator**: `http://127.0.0.1:8000`

## 📱 Cách 2: Kết nối từ Physical Android Device

### Bước 1: Lấy IP address của máy tính

#### macOS/Linux:
```bash
# Cách 1: Sử dụng ifconfig
ifconfig | grep "inet " | grep -v 127.0.0.1

# Cách 2: Sử dụng ipconfig (macOS)
ipconfig getifaddr en0  # WiFi
ipconfig getifaddr en1  # Ethernet

# Cách 3: Sử dụng hostname
hostname -I  # Linux
```

#### Windows:
```bash
ipconfig
# Tìm "IPv4 Address" trong phần "Wireless LAN adapter Wi-Fi" hoặc "Ethernet adapter"
```

Ví dụ IP address: `192.168.1.5`

### Bước 2: Cập nhật IP trong code

Mở file `lib/core/utils/api_config.dart` và cập nhật:

```dart
static const String physicalDeviceHost = '192.168.1.5'; // ⚠️ Thay bằng IP của bạn
```

### Bước 3: Sử dụng URL cho physical device

Mở file `lib/core/constants/api_constants.dart` và thay đổi:

```dart
// Thay dòng này:
static String get baseUrl => ApiConfig.getBaseUrl();

// Bằng dòng này:
static String get baseUrl => ApiConfig.getPhysicalDeviceUrl();
```

### Bước 4: Đảm bảo backend chạy với host 0.0.0.0

Backend đã được cấu hình để chạy với `host="0.0.0.0"` trong `backend/app/main.py`, điều này cho phép truy cập từ network.

Chạy backend:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Bước 5: Kiểm tra kết nối

1. **Đảm bảo Android device và máy tính cùng mạng WiFi**
2. **Kiểm tra firewall**: Tắt firewall hoặc cho phép port 8000
3. **Test từ browser trên Android device**: Mở `http://<your-ip>:8000/docs` để xem Swagger UI
4. **Test từ Flutter app**: Chạy app và thử tính năng nhận diện nhạc

## 🔥 Troubleshooting

### Lỗi: "Connection refused" hoặc "Cannot connect to server"

**Nguyên nhân có thể:**
1. Backend chưa chạy hoặc chạy sai host
2. IP address không đúng
3. Firewall chặn port 8000
4. Android device và máy tính không cùng mạng WiFi

**Giải pháp:**
```bash
# 1. Kiểm tra backend đang chạy
curl http://localhost:8000/stats

# 2. Kiểm tra từ máy tính với IP
curl http://192.168.1.5:8000/stats  # Thay bằng IP của bạn

# 3. Kiểm tra firewall (macOS)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# 4. Tắt firewall tạm thời để test (macOS)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
```

### Lỗi: "Network is unreachable"

**Nguyên nhân:** Android device và máy tính không cùng mạng

**Giải pháp:**
- Đảm bảo cả hai đều kết nối cùng WiFi
- Kiểm tra IP address của cả hai thiết bị

### Lỗi: "Connection timeout"

**Nguyên nhân:** Firewall hoặc router chặn

**Giải pháp:**
- Tắt firewall tạm thời
- Kiểm tra router settings
- Thử dùng hotspot từ điện thoại khác

## 🧪 Test kết nối

### Test từ terminal:
```bash
# Test từ máy tính
curl http://localhost:8000/stats

# Test với IP (từ máy tính)
curl http://192.168.1.5:8000/stats

# Test từ Android device (sử dụng ADB)
adb shell
curl http://192.168.1.5:8000/stats
```

### Test từ Flutter app:
1. Mở app trên Android device
2. Vào màn hình nhận diện nhạc
3. Nhấn nút record
4. Kiểm tra log trong terminal để xem request có đến backend không

## 📝 Quick Reference

| Platform | URL |
|----------|-----|
| Android Emulator | `http://10.0.2.2:8000` |
| iOS Simulator | `http://127.0.0.1:8000` |
| Physical Android Device | `http://<your-ip>:8000` |
| Physical iOS Device | `http://<your-ip>:8000` |

## 🔐 Security Note

⚠️ **Lưu ý:** Cấu hình hiện tại cho phép truy cập từ mọi nguồn (`allow_origins=["*"]`). Trong production, bạn nên:
- Chỉ định rõ các origin được phép
- Sử dụng HTTPS
- Thêm authentication

