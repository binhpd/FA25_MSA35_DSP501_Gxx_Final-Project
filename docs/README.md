# 📚 Tài Liệu Dự Án - Music Recognition System

## 🎯 Tổng Quan

Dự án **Music Recognition System** là một ứng dụng nhận diện bài hát tương tự Shazam, được phát triển cho môn học Digital Signal Processing (DSP).

## 📖 Tài Liệu Chính

### [📘 PROJECT_DOCUMENTATION.md](./PROJECT_DOCUMENTATION.md)
**Tài liệu tổng hợp đầy đủ về dự án**

Bao gồm:
- Tổng quan dự án và mô tả bài toán
- Kiến trúc hệ thống (Backend + Frontend)
- Cấu trúc project chi tiết
- Công nghệ sử dụng
- Thuật toán DSP (Audio Fingerprinting)
- API Endpoints đầy đủ
- Hướng dẫn setup và sử dụng
- Cấu trúc Backend và Frontend

**👉 Đọc file này đầu tiên để hiểu toàn bộ dự án**

---

## 📁 Các Tài Liệu Bổ Sung

### Hướng Dẫn Cụ Thể
- [Android Connection Guide](./ANDROID_CONNECTION_GUIDE.md) - Hướng dẫn kết nối Android device đến backend local

### Backend (Chi Tiết)
- [Backend Documentation](../backend/docs/BACKEND_DOCUMENTATION.md) - Tài liệu chi tiết về backend (đầy đủ hơn)
- [Batch Upload Guide](../backend/docs/GUIDE_BATCH_UPLOAD.md) - Hướng dẫn upload nhiều bài hát
- [Delete Songs Guide](../backend/docs/DELETE_SONGS_GUIDE.md) - Hướng dẫn xóa bài hát

---

## 🚀 Quick Start

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app/main.py
```

### Frontend
```bash
cd lynk
flutter pub get
flutter run
```

---

## 📝 Lưu ý

- **Tài liệu chính:** [PROJECT_DOCUMENTATION.md](./PROJECT_DOCUMENTATION.md) - Đọc file này để có cái nhìn tổng quan đầy đủ
- Các tài liệu khác là bổ sung cho các mục đích cụ thể
