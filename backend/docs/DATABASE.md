# Database Documentation - Persistent Storage

## 📋 Tổng Quan

Backend đã được chuyển từ **In-Memory Storage** sang **Persistent Storage** sử dụng **SQLite**.

### Thay Đổi Chính
- ✅ Dữ liệu được lưu vào file `music_recognition.db` (SQLite)
- ✅ Dữ liệu **không bị mất** khi restart server
- ✅ Dữ liệu được **lưu ngay** sau khi learn song
- ✅ Dữ liệu được **tự động load** khi server khởi động

---

## 🗄️ Database Schema

### Bảng: `songs`
Lưu thông tin bài hát

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto increment |
| name | TEXT | Tên bài hát (unique) |
| created_at | TIMESTAMP | Thời gian tạo (auto) |

### Bảng: `fingerprints`
Lưu fingerprints của các bài hát

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto increment |
| hash_token | TEXT | Hash token dạng "f1\|f2\|dt" |
| song_id | INTEGER | Foreign key đến songs.id |
| absolute_time | REAL | Thời gian tuyệt đối (giây) |

### Indexes
- `idx_hash_token`: Index trên `hash_token` để query nhanh
- `idx_song_id`: Index trên `song_id` để join nhanh

### Foreign Key Constraint
- `fingerprints.song_id` → `songs.id` với `ON DELETE CASCADE`
- Khi xóa song, tất cả fingerprints sẽ tự động bị xóa

---

## 🔧 Sử Dụng

### Khởi Tạo Database
Database sẽ **tự động được tạo** khi server khởi động lần đầu.

```python
from app.core.database import PersistentDB

# Tạo database (mặc định: music_recognition.db)
db = PersistentDB(db_path="music_recognition.db")
```

### Thêm Bài Hát
```python
fingerprints = [
    ((440, 523, 10), 0.5),   # (hash_token, absolute_time)
    ((523, 659, 15), 0.5),
    ...
]

count = db.add_song("Song_Name", fingerprints)
# Dữ liệu được lưu ngay vào database
```

### Query
```python
result = db.query(query_fingerprints, min_matches=5)
# result = (song_name, match_count, confidence) hoặc None
```

### Xóa Bài Hát
```python
success, deleted_count = db.delete_song("Song_Name")
# Xóa song và tất cả fingerprints (CASCADE)
```

---

## 📁 File Database

### Vị Trí
- **Mặc định:** `music_recognition.db` (trong thư mục backend)
- **Có thể thay đổi:** Truyền `db_path` khi khởi tạo

### Backup
```bash
# Backup database
cp music_recognition.db music_recognition.db.backup

# Restore database
cp music_recognition.db.backup music_recognition.db
```

### Xem Database
Sử dụng SQLite command line:
```bash
sqlite3 music_recognition.db

# Xem tables
.tables

# Xem số lượng songs
SELECT COUNT(*) FROM songs;

# Xem số lượng fingerprints
SELECT COUNT(*) FROM fingerprints;

# Xem danh sách songs
SELECT * FROM songs;

# Xem fingerprints của một song
SELECT f.*, s.name 
FROM fingerprints f 
JOIN songs s ON f.song_id = s.id 
WHERE s.name = 'Song_Name' 
LIMIT 10;
```

---

## 🔄 Migration từ In-Memory

### Trước (In-Memory)
```python
db = InMemoryDB()  # Dữ liệu mất khi restart
```

### Sau (Persistent)
```python
db = PersistentDB()  # Dữ liệu được lưu vào SQLite
```

### Tương Thích Ngược
Code đã được cập nhật để sử dụng `PersistentDB` thay vì `InMemoryDB`. 
Tất cả API endpoints hoạt động giống như trước, nhưng dữ liệu được lưu persistent.

---

## ⚡ Performance

### Batch Insert
Fingerprints được insert theo batch để tối ưu performance:
```python
cursor.executemany("""
    INSERT INTO fingerprints (hash_token, song_id, absolute_time)
    VALUES (?, ?, ?)
""", fingerprint_data)
```

### Indexes
- Index trên `hash_token` giúp query nhanh khi recognize
- Index trên `song_id` giúp join và delete nhanh

### Transaction
- Mỗi `add_song()` là một transaction
- Commit ngay sau khi insert để đảm bảo dữ liệu được lưu

---

## 🔒 Lưu Ý

### File Database
- File `music_recognition.db` chứa tất cả dữ liệu
- **Nên backup** định kỳ
- File có thể lớn nếu có nhiều bài hát

### Concurrency
- SQLite hỗ trợ concurrent reads tốt
- Concurrent writes có thể chậm hơn (nhưng đủ cho use case này)

### Production
- Có thể chuyển sang PostgreSQL nếu cần scale lớn
- Hiện tại SQLite đủ cho development và small production

---

## 📊 So Sánh

| Feature | In-Memory | Persistent (SQLite) |
|---------|-----------|---------------------|
| Dữ liệu sau restart | ❌ Mất | ✅ Giữ nguyên |
| Tốc độ | ⚡ Rất nhanh | ⚡ Nhanh |
| Dung lượng | 💾 RAM | 💾 Disk |
| Backup | ❌ Không thể | ✅ Dễ dàng |
| Scale | ❌ Giới hạn RAM | ✅ Giới hạn disk |

---

## 🐛 Troubleshooting

### Lỗi: "database is locked"
**Nguyên nhân:** Nhiều process đang truy cập database cùng lúc

**Giải pháp:**
- Đảm bảo chỉ một instance server chạy
- Kiểm tra xem có process nào khác đang dùng database không

### Lỗi: "no such table"
**Nguyên nhân:** Database chưa được khởi tạo

**Giải pháp:**
- Xóa file `music_recognition.db` cũ
- Restart server để tạo lại schema

### Database file quá lớn
**Giải pháp:**
- Xóa các bài hát không cần thiết
- Vacuum database: `VACUUM;` trong SQLite

---

## 📚 Tài Liệu Tham Khảo

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Python sqlite3 Module](https://docs.python.org/3/library/sqlite3.html)



