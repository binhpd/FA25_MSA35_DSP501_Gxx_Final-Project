# Backend Documentation

Thư mục này chứa tất cả tài liệu chi tiết về backend của hệ thống Music Recognition.

## 📚 Tài Liệu

### 1. [BACKEND_DOCUMENTATION.md](./BACKEND_DOCUMENTATION.md)
**Tài liệu chi tiết đầy đủ về backend**

Bao gồm:
- Tổng quan và kiến trúc hệ thống
- Cấu trúc thư mục
- Thiết kế database chi tiết
- DSP Engine - Audio Fingerprinting
- API Endpoints đầy đủ
- Workflow và luồng xử lý
- Công cụ và scripts
- Deployment và configuration

**📖 Đọc đầu tiên để hiểu toàn bộ hệ thống**

---

### 2. [GUIDE_BATCH_UPLOAD.md](./GUIDE_BATCH_UPLOAD.md)
**Hướng dẫn upload nhiều bài hát vào database**

Bao gồm:
- Các cách upload bài hát
- Sử dụng batch_upload_songs.py
- Tạo và sử dụng mapping file
- Tips và troubleshooting

**💡 Dùng khi cần upload nhiều bài hát**

---

### 3. [DELETE_SONGS_GUIDE.md](./DELETE_SONGS_GUIDE.md)
**Hướng dẫn xóa dữ liệu bài hát**

Bao gồm:
- API endpoints để xóa bài hát
- Xóa một bài hát cụ thể
- Xóa toàn bộ database
- Examples và best practices

**🗑️ Dùng khi cần quản lý database**

---

### 4. [QUICK_UPLOAD_GUIDE.md](./QUICK_UPLOAD_GUIDE.md)
**Hướng dẫn nhanh upload bài hát**

Tóm tắt nhanh cách upload bài hát vào database.

**⚡ Quick reference**

---

## 🗂️ Cấu Trúc

```
docs/
├── README.md                      # File này
├── BACKEND_DOCUMENTATION.md       # Tài liệu chi tiết đầy đủ
├── GUIDE_BATCH_UPLOAD.md          # Hướng dẫn upload batch
├── DELETE_SONGS_GUIDE.md          # Hướng dẫn xóa bài hát
└── QUICK_UPLOAD_GUIDE.md          # Hướng dẫn nhanh
```

---

## 🚀 Bắt Đầu

1. **Mới bắt đầu?** → Đọc [BACKEND_DOCUMENTATION.md](./BACKEND_DOCUMENTATION.md)
2. **Cần upload bài hát?** → Xem [GUIDE_BATCH_UPLOAD.md](./GUIDE_BATCH_UPLOAD.md)
3. **Cần xóa dữ liệu?** → Xem [DELETE_SONGS_GUIDE.md](./DELETE_SONGS_GUIDE.md)
4. **Cần quick reference?** → Xem [QUICK_UPLOAD_GUIDE.md](./QUICK_UPLOAD_GUIDE.md)

---

## 📝 Ghi Chú

- Tất cả tài liệu được viết bằng tiếng Việt
- Code examples có cả cURL và Python
- Tài liệu được cập nhật thường xuyên

---

## 🔗 Links

- [Backend README](../README.md) - Quick start guide
- [Main Project](../..) - Root project directory

