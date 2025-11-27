# Hướng Dẫn Xóa Dữ Liệu Database

## 📋 Tổng Quan

Script `clear_database.py` cho phép bạn:
- ✅ Xóa toàn bộ dữ liệu trong database
- ✅ Xóa một bài hát cụ thể
- ✅ Xem danh sách tất cả bài hát

---

## 🚀 Cách Sử Dụng

### 1. Xóa Toàn Bộ Database

#### Với xác nhận (an toàn):
```bash
cd backend
python3 scripts/clear_database.py --clear
```

Script sẽ hiển thị:
- Số lượng songs và fingerprints hiện tại
- Yêu cầu xác nhận trước khi xóa

#### Không cần xác nhận (tự động):
```bash
python3 scripts/clear_database.py --clear --yes
# hoặc
python3 scripts/clear_database.py --clear -y
```

### 2. Xóa Một Bài Hát Cụ Thể

```bash
python3 scripts/clear_database.py --delete "Song_Name"
```

Ví dụ:
```bash
python3 scripts/clear_database.py --delete "Test_Song_1"
```

#### Không cần xác nhận:
```bash
python3 scripts/clear_database.py --delete "Song_Name" --yes
```

### 3. Xem Danh Sách Bài Hát

```bash
python3 scripts/clear_database.py --list
```

Output:
```
============================================================
📊 Database Status:
   Total Songs: 5
   Total Fingerprints: 125430
============================================================

📝 Songs in database:
   1. Song_1
   2. Song_2
   3. Song_3
   4. Song_4
   5. Song_5
```

### 4. Sử Dụng Database Path Tùy Chỉnh

```bash
python3 scripts/clear_database.py --clear --db-path /path/to/custom.db
```

---

## 📝 Ví Dụ Cụ Thể

### Ví Dụ 1: Xóa Toàn Bộ Database

```bash
cd backend
python3 scripts/clear_database.py --clear
```

Output:
```
============================================================
📊 Current Database Status:
   Songs: 10
   Fingerprints: 125430
============================================================

⚠️  Are you sure you want to delete ALL data? (yes/no): yes

✅ Database cleared successfully!
   Deleted: 10 songs, 125430 fingerprints
```

### Ví Dụ 2: Xóa Một Bài Hát

```bash
python3 scripts/clear_database.py --delete "Test_Song_1"
```

Output:
```
⚠️  Are you sure you want to delete 'Test_Song_1'? (yes/no): yes

✅ Song 'Test_Song_1' deleted successfully!
   Deleted: 6166 fingerprints
```

### Ví Dụ 3: Xem Danh Sách Trước Khi Xóa

```bash
# 1. Xem danh sách
python3 scripts/clear_database.py --list

# 2. Xóa bài hát cụ thể
python3 scripts/clear_database.py --delete "Song_Name" --yes
```

---

## ⚠️ Lưu Ý

### 1. Không Thể Hoàn Tác
- ⚠️ Xóa dữ liệu là **vĩnh viễn**
- ⚠️ Không có backup tự động
- ✅ Nên backup database trước khi xóa

### 2. Backup Database

```bash
# Backup trước khi xóa
cp music_recognition.db music_recognition.db.backup

# Xóa database
python3 scripts/clear_database.py --clear --yes

# Restore nếu cần
cp music_recognition.db.backup music_recognition.db
```

### 3. Database File Location
- **Mặc định:** `backend/music_recognition.db`
- Script tự động tìm file trong thư mục backend

---

## 🔧 Tùy Chọn

### Tất Cả Các Tùy Chọn

```bash
python3 scripts/clear_database.py --help
```

**Options:**
- `--clear`: Xóa toàn bộ database
- `--delete SONG_NAME`: Xóa một bài hát cụ thể
- `--list`: Xem danh sách bài hát
- `--db-path PATH`: Đường dẫn đến database file
- `--yes, -y`: Bỏ qua xác nhận

---

## 🆚 So Sánh với API

### API Endpoint
```bash
# Xóa toàn bộ (API)
curl -X DELETE "http://localhost:8000/songs"

# Xóa một bài hát (API)
curl -X DELETE "http://localhost:8000/songs/Song_Name"
```

### Script
```bash
# Xóa toàn bộ (Script)
python3 scripts/clear_database.py --clear

# Xóa một bài hát (Script)
python3 scripts/clear_database.py --delete "Song_Name"
```

**Ưu điểm của Script:**
- ✅ Không cần server đang chạy
- ✅ Có xác nhận trước khi xóa
- ✅ Hiển thị thông tin chi tiết
- ✅ Có thể dùng trong automation

---

## 🐛 Troubleshooting

### Lỗi: "Database file not found"
**Nguyên nhân:** Database chưa được tạo hoặc đường dẫn sai

**Giải pháp:**
```bash
# Kiểm tra file có tồn tại không
ls -la backend/music_recognition.db

# Hoặc chỉ định đường dẫn đầy đủ
python3 scripts/clear_database.py --list --db-path /full/path/to/music_recognition.db
```

### Lỗi: "Song not found"
**Nguyên nhân:** Tên bài hát không đúng

**Giải pháp:**
```bash
# Xem danh sách bài hát trước
python3 scripts/clear_database.py --list

# Sử dụng đúng tên bài hát (phân biệt hoa thường)
python3 scripts/clear_database.py --delete "Exact_Song_Name"
```

---

## 📚 Related Files

- `backend/scripts/clear_database.py` - Script chính
- `backend/app/core/database.py` - Database implementation
- `backend/docs/DATABASE.md` - Database documentation

