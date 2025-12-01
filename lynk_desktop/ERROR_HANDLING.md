# Error Handling Guide - Lynk Desktop

## Xử lý lỗi Server

### Lỗi 500 Internal Server Error

Khi server trả về lỗi 500, ứng dụng sẽ:

1. **Hiển thị thông báo lỗi chi tiết** với các nguyên nhân có thể:
   - File audio không hợp lệ hoặc bị hỏng
   - Server đang gặp sự cố
   - Database có vấn đề

2. **Tự động reset UI** về trạng thái sẵn sàng

3. **Ghi log** chi tiết để debug

#### Cách xử lý:

1. **Kiểm tra logs server:**
   ```bash
   # Xem logs của backend server
   # Thường hiển thị trong terminal nơi chạy server
   ```

2. **Kiểm tra file audio:**
   - Đảm bảo file WAV hợp lệ
   - Kiểm tra kích thước file (không quá lớn)
   - Thử với file audio khác

3. **Kiểm tra database:**
   ```bash
   curl http://localhost:8000/stats
   ```

4. **Khởi động lại server:**
   ```bash
   cd backend
   python -m app.main
   ```

### Lỗi 400 Bad Request

- **Nguyên nhân:** File audio không đúng định dạng hoặc quá lớn
- **Giải pháp:** Kiểm tra file audio, đảm bảo là WAV/MP3 hợp lệ

### Lỗi 404 Not Found

Khi server trả về lỗi 404, ứng dụng sẽ hiển thị thông báo chi tiết.

**Nguyên nhân:**
- Endpoint `/recognize` không tồn tại trên server
- URL server không đúng trong `config.py`
- Backend server đang chạy version cũ không có endpoint này

**Giải pháp:**

1. **Kiểm tra endpoint có tồn tại:**
   ```bash
   curl http://localhost:8000/
   # Kiểm tra xem response có liệt kê endpoint /recognize không
   ```

2. **Kiểm tra URL trong config:**
   ```python
   # Trong lynk_desktop/config.py
   BASE_URL = "http://localhost:8000"  # Đảm bảo đúng
   ```

3. **Kiểm tra backend server version:**
   - Đảm bảo backend server đang chạy phiên bản mới nhất
   - Kiểm tra file `backend/app/api/routes.py` có endpoint `/recognize`

4. **Test endpoint:**
   ```bash
   cd lynk_desktop
   source venv/bin/activate
   python test_connection.py
   ```

5. **Khởi động lại backend server:**
   ```bash
   cd backend
   python -m app.main
   ```

### Lỗi Connection Error

- **Nguyên nhân:** Không thể kết nối đến server
- **Giải pháp:**
  1. Kiểm tra server có đang chạy: `curl http://localhost:8000/`
  2. Kiểm tra firewall
  3. Kiểm tra URL trong `config.py`

### Lỗi Timeout

- **Nguyên nhân:** Server không phản hồi trong 30 giây
- **Giải pháp:**
  1. Kiểm tra server có đang xử lý request khác
  2. Tăng timeout trong `api_client.py` (nếu cần)
  3. Kiểm tra hiệu năng server

## Debug Mode

Để xem logs chi tiết, kiểm tra output trong terminal khi chạy ứng dụng:

```bash
python main.py
```

Logs sẽ hiển thị:
- Request details (file size, URL)
- Response status code
- Error messages
- Server response details

## Best Practices

1. **Luôn kiểm tra response status code** trước khi xử lý
2. **Hiển thị thông báo lỗi rõ ràng** cho người dùng
3. **Reset UI state** sau mỗi lỗi
4. **Log chi tiết** để debug
5. **Không crash app** khi server lỗi

