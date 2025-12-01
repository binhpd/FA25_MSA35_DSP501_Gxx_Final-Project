# Troubleshooting Guide - Lynk Desktop

## Lỗi Microphone / Audio Recording

### Lỗi: `[Errno -9986] Internal PortAudio error` hoặc `Audio Unit: Invalid Property Value`

Đây là lỗi phổ biến trên macOS khi PyAudio không thể truy cập microphone.

#### Giải pháp:

1. **Cấp quyền truy cập Microphone:**
   - Mở **System Settings** (Cài đặt hệ thống)
   - Vào **Privacy & Security** (Quyền riêng tư & Bảo mật)
   - Chọn **Microphone** (Microphone)
   - Tìm ứng dụng Python hoặc Terminal trong danh sách
   - Bật quyền truy cập microphone

2. **Kiểm tra Terminal/IDE permissions:**
   - Nếu chạy từ Terminal, Terminal cần có quyền truy cập microphone
   - Nếu chạy từ IDE (VS Code, PyCharm), IDE cần có quyền truy cập microphone

3. **Đảm bảo không có ứng dụng khác đang sử dụng microphone:**
   - Đóng các ứng dụng như Zoom, Teams, Skype, etc.
   - Kiểm tra Activity Monitor để tìm process đang sử dụng microphone

4. **Khởi động lại ứng dụng:**
   - Đóng ứng dụng hoàn toàn
   - Khởi động lại

5. **Kiểm tra audio device:**
   ```bash
   # Kiểm tra audio devices có sẵn
   python -c "import pyaudio; p = pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"
   ```

### Lỗi: `NameError: cannot access free variable 'e'`

Lỗi này đã được sửa trong phiên bản mới nhất. Nếu vẫn gặp lỗi:
- Đảm bảo bạn đang sử dụng phiên bản mới nhất của code
- Thử khởi động lại ứng dụng

### Lỗi: `Cannot connect to server`

1. **Kiểm tra backend server:**
   ```bash
   curl http://localhost:8000/
   ```

2. **Khởi động backend server:**
   ```bash
   cd ../backend
   python -m app.main
   ```

3. **Kiểm tra firewall:**
   - Đảm bảo port 8000 không bị chặn

### Lỗi: `No module named 'pyaudio'`

1. **Cài đặt PortAudio (macOS):**
   ```bash
   brew install portaudio
   ```

2. **Cài đặt PyAudio:**
   ```bash
   source venv/bin/activate
   pip install pyaudio
   ```

### Lỗi: `No matching song found`

1. **Kiểm tra database có bài hát:**
   ```bash
   curl http://localhost:8000/stats
   ```

2. **Thêm bài hát vào database:**
   - Sử dụng script `batch_upload_songs.py` trong thư mục `backend/scripts/`
   - Hoặc sử dụng API endpoint `/learn`

## Test Microphone

Để test microphone có hoạt động không:

```python
import pyaudio
import wave

# Test recording
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
print("Recording... Speak now!")
frames = []
for i in range(0, int(44100 / 1024 * 2)):  # 2 seconds
    data = stream.read(1024)
    frames.append(data)
print("Finished recording")
stream.stop_stream()
stream.close()
p.terminate()
print("✅ Microphone works!")
```

## Liên hệ

Nếu vẫn gặp vấn đề, vui lòng:
1. Kiểm tra logs trong terminal
2. Cung cấp thông tin về hệ điều hành và Python version
3. Mô tả chi tiết các bước đã thử



