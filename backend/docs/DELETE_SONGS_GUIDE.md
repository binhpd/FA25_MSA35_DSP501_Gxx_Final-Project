# Hướng Dẫn Xóa Dữ Liệu Bài Hát

## 📋 Tổng Quan

API hỗ trợ 2 cách xóa dữ liệu:
1. **Xóa một bài hát cụ thể** - Xóa bài hát và tất cả fingerprints của nó
2. **Xóa toàn bộ database** - Xóa tất cả bài hát và fingerprints

---

## 🗑️ API Endpoints

### 1. DELETE /songs/{song_name}
Xóa một bài hát cụ thể

**Request:**
```http
DELETE http://localhost:8000/songs/{song_name}
```

**Response (Success):**
```json
{
  "success": true,
  "song_name": "Test_Song_1",
  "deleted_fingerprints": 6166,
  "message": "Song 'Test_Song_1' deleted successfully. Removed 6166 fingerprints."
}
```

**Response (Not Found):**
```json
{
  "success": false,
  "song_name": "NonExistent_Song",
  "deleted_fingerprints": 0,
  "message": "Song 'NonExistent_Song' not found in database."
}
```

### 2. DELETE /songs
Xóa toàn bộ database

**Request:**
```http
DELETE http://localhost:8000/songs
```

**Response:**
```json
{
  "success": true,
  "deleted_songs": 3,
  "deleted_fingerprints": 9786,
  "message": "Database cleared. Deleted 3 songs and 9786 fingerprints."
}
```

---

## 💻 Cách Sử Dụng

### Cách 1: Sử Dụng cURL

#### Xóa một bài hát:
```bash
# URL encode tên bài hát nếu có khoảng trắng
curl -X DELETE "http://localhost:8000/songs/Test_Song_1"

# Hoặc với URL encoding
curl -X DELETE "http://localhost:8000/songs/test%20song%201"
```

#### Xóa toàn bộ database:
```bash
curl -X DELETE "http://localhost:8000/songs"
```

### Cách 2: Sử Dụng Python

#### Xóa một bài hát:
```python
import requests

song_name = "Test_Song_1"
response = requests.delete(f"http://localhost:8000/songs/{song_name}")
print(response.json())
```

#### Xóa toàn bộ database:
```python
import requests

response = requests.delete("http://localhost:8000/songs")
print(response.json())
```

### Cách 3: Sử Dụng Script Test

```bash
cd backend
source venv/bin/activate
python3 test_data/test_delete_songs.py
```

---

## 📝 Ví Dụ Cụ Thể

### Ví Dụ 1: Xóa Một Bài Hát

```bash
# 1. Xem danh sách bài hát hiện tại
curl http://localhost:8000/songs | python3 -m json.tool

# Output:
# {
#   "songs": ["Test_Song_1", "Test_Song_2", "Test_Song_3"],
#   "count": 3
# }

# 2. Xóa bài hát "Test_Song_1"
curl -X DELETE "http://localhost:8000/songs/Test_Song_1" | python3 -m json.tool

# Output:
# {
#   "success": true,
#   "song_name": "Test_Song_1",
#   "deleted_fingerprints": 6166,
#   "message": "Song 'Test_Song_1' deleted successfully..."
# }

# 3. Kiểm tra lại
curl http://localhost:8000/songs | python3 -m json.tool

# Output:
# {
#   "songs": ["Test_Song_2", "Test_Song_3"],
#   "count": 2
# }
```

### Ví Dụ 2: Xóa Toàn Bộ Database

```bash
# 1. Xem stats trước khi xóa
curl http://localhost:8000/stats | python3 -m json.tool

# 2. Xóa toàn bộ
curl -X DELETE "http://localhost:8000/songs" | python3 -m json.tool

# 3. Kiểm tra lại
curl http://localhost:8000/stats | python3 -m json.tool
# {
#   "song_count": 0,
#   "fingerprint_count": 0,
#   "songs": []
# }
```

### Ví Dụ 3: Xóa Nhiều Bài Hát (Script)

```python
import requests

BASE_URL = "http://localhost:8000"

# Lấy danh sách bài hát
songs = requests.get(f"{BASE_URL}/songs").json()['songs']

# Xóa từng bài hát
for song in songs:
    response = requests.delete(f"{BASE_URL}/songs/{song}")
    print(f"Deleted {song}: {response.json()}")
```

---

## 🔧 Implementation Details

### Database Method: `delete_song()`

```python
def delete_song(self, song_name: str) -> Tuple[bool, int]:
    """
    Delete a specific song from the database
    
    Process:
    1. Check if song exists
    2. Remove song from all hash entries
    3. Remove empty hash entries
    4. Remove from song list
    5. Return success status and deleted count
    """
```

**Algorithm:**
1. Iterate qua tất cả hash entries trong database
2. Filter out các entries có `song_name` matching
3. Xóa các hash entries trở nên empty
4. Remove song từ `song_list`
5. Return số fingerprints đã xóa

### API Endpoint: `DELETE /songs/{song_name}`

- **Method:** DELETE
- **Path Parameter:** `song_name` (URL encoded nếu có khoảng trắng)
- **Response:** JSON với success status và số fingerprints đã xóa

### API Endpoint: `DELETE /songs`

- **Method:** DELETE
- **No Parameters**
- **Response:** JSON với số songs và fingerprints đã xóa

---

## ⚠️ Lưu Ý

### 1. URL Encoding
- Tên bài hát có khoảng trắng cần URL encode
- Ví dụ: `"test song 1"` → `"test%20song%201"`
- Python `requests` tự động encode

### 2. Không Thể Hoàn Tác
- Xóa là vĩnh viễn (in-memory database)
- Không có backup tự động
- Nên export stats trước khi xóa

### 3. Performance
- Xóa một bài hát: O(n) với n là số fingerprints
- Xóa toàn bộ: O(1) - rất nhanh

### 4. Case Sensitivity
- Tên bài hát phân biệt hoa thường
- `"Test_Song"` ≠ `"test_song"`

---

## 🧪 Test Results

### Test 1: Xóa Một Bài Hát
```
✅ Success
- Deleted: "test song 2"
- Removed: 2,368 fingerprints
- Database: 3 → 2 songs
```

### Test 2: Xóa Toàn Bộ
```
✅ Success
- Deleted: All songs
- Database cleared
- Stats: 0 songs, 0 fingerprints
```

---

## 📚 Tài Liệu API

Xem thêm tại: `http://localhost:8000/docs` (Swagger UI)

---

## 🔗 Related Files

- `backend/database.py` - Method `delete_song()` và `clear_all()`
- `backend/main.py` - API endpoints `DELETE /songs/{song_name}` và `DELETE /songs`
- `backend/test_data/test_delete_songs.py` - Script test

