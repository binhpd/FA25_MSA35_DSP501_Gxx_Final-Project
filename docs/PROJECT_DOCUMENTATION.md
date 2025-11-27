# 📚 Tài Liệu Tổng Hợp - Music Recognition System

## 📋 Mục Lục

1. [Tổng Quan Dự Án](#tổng-quan-dự-án)
2. [Mô Tả Bài Toán](#mô-tả-bài-toán)
3. [Kiến Trúc Hệ Thống](#kiến-trúc-hệ-thống)
4. [Cấu Trúc Project](#cấu-trúc-project)
5. [Công Nghệ Sử Dụng](#công-nghệ-sử-dụng)
6. [Thuật Toán DSP - Audio Fingerprinting](#thuật-toán-dsp---audio-fingerprinting)
7. [API Endpoints](#api-endpoints)
8. [Hướng Dẫn Setup và Sử Dụng](#hướng-dẫn-setup-và-sử-dụng)
9. [Cấu Trúc Backend](#cấu-trúc-backend)
10. [Cấu Trúc Frontend](#cấu-trúc-frontend)

---

## 🎯 Tổng Quan Dự Án

**Music Recognition System** là một ứng dụng nhận diện bài hát tương tự Shazam, được phát triển cho môn học Digital Signal Processing (DSP).

### Đặc Điểm Chính
- **Thin Client (Flutter)** - Ghi âm và gửi request
- **Fat Server (Python)** - Xử lý DSP và matching
- **Audio Fingerprinting** - Sử dụng thuật toán của Avery Wang (Shazam)
- **Real-time Recognition** - Nhận diện bài hát trong 5-10 giây

---

## 📖 Mô Tả Bài Toán

### Mục Tiêu
Xây dựng ứng dụng mobile cho phép người dùng:
- Ghi âm một đoạn nhạc đang phát trong môi trường xung quanh (5-10 giây)
- Tạo fingerprint từ đoạn ghi âm
- Gửi fingerprint lên server để đối chiếu với cơ sở dữ liệu
- Nhận về kết quả bài hát (tên, ca sĩ, album)
- Hiển thị thông tin bài hát và các gợi ý liên quan

### Yêu Cầu Kỹ Thuật
- **Thời gian xử lý:** Tổng không vượt quá 7 giây (ghi âm + gửi + nhận kết quả)
- **Độ chính xác:** Nhận diện đúng bài hát với confidence > 80%
- **Giao diện:** Đẹp, có hiệu ứng động khi ghi âm
- **Hiệu năng:** Mượt 60fps, đồng bộ với nhịp sóng âm

---

## 🏗️ Kiến Trúc Hệ Thống

### High-Level Architecture

```
┌─────────────────┐
│  Flutter App    │  (Client - Mobile)
│  - Ghi âm       │
│  - UI/UX        │
└────────┬────────┘
         │ HTTP/REST
         │ Multipart Form Data
         ▼
┌─────────────────────────────────┐
│  FastAPI Server                 │  (Backend - Python)
│  - API Endpoints                │
│  - CORS Middleware              │
│  - File Upload Handling         │
└────────┬────────────────────────┘
         │
         ├─────────────────┬─────────────────┐
         ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ DSP Engine   │  │  Database    │  │  File Temp  │
│ (Fingerprint)│  │ (In-Memory)  │  │  Storage    │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Component Flow

```
[Client] Record Audio (5-10s)
    │
    ├─> Generate WAV file
    │
    ├─> POST /recognize (multipart/form-data)
    │
    ▼
[Server] Receive file
    │
    ├─> Validate file type
    │
    ├─> [DSP Engine] Process audio
    │   ├─> Load & preprocess
    │   ├─> Generate spectrogram
    │   ├─> Find peaks
    │   └─> Create fingerprints
    │
    ├─> [Database] Query fingerprints
    │   ├─> Lookup hashes
    │   ├─> Calculate offsets
    │   └─> Time coherency analysis
    │
    └─> Return result (song name, confidence)
```

---

## 📁 Cấu Trúc Project

```
FA25_MSA35_DSP501_G8_Final Project/
├── backend/                    # Backend Server (Python/FastAPI)
│   ├── app/
│   │   ├── main.py            # FastAPI application
│   │   ├── api/
│   │   │   └── routes.py      # API routes
│   │   └── core/
│   │       ├── dsp_engine.py   # Audio fingerprinting engine
│   │       └── database.py    # In-memory database
│   ├── docs/                   # Backend documentation
│   ├── scripts/                # Utility scripts
│   ├── test_data/              # Test files
│   └── requirements.txt        # Python dependencies
│
├── lynk/                       # Frontend App (Flutter)
│   ├── lib/
│   │   ├── core/              # Core functionality
│   │   │   ├── constants/     # App constants
│   │   │   ├── di/            # Dependency Injection
│   │   │   └── utils/        # Utilities
│   │   ├── data/              # Data Layer
│   │   │   ├── datasources/  # API & Local data sources
│   │   │   └── repositories/  # Repository implementations
│   │   ├── domain/            # Domain Layer
│   │   │   ├── entities/      # Business entities
│   │   │   └── repositories/  # Repository interfaces
│   │   └── presentation/       # Presentation Layer
│   │       ├── pages/        # UI screens
│   │       └── providers/    # State management
│   ├── android/               # Android configuration
│   ├── ios/                   # iOS configuration
│   └── pubspec.yaml          # Flutter dependencies
│
└── docs/                      # Project documentation
    └── PROJECT_DOCUMENTATION.md  # File này
```

---

## 💻 Công Nghệ Sử Dụng

### Backend
- **Language:** Python 3.9+
- **Framework:** FastAPI (Uvicorn server)
- **DSP Libraries:**
  - `scipy`: STFT và Peak Finding
  - `numpy`: Matrix operations
  - `soundfile`: Audio loading
- **Storage:** In-Memory Dictionary (Python `dict`)

### Frontend
- **Framework:** Flutter (Dart)
- **Packages:**
  - `record`: Audio recording
  - `dio`: HTTP requests
  - `permission_handler`: Microphone permissions
  - `provider`: State management

---

## 🎵 Thuật Toán DSP - Audio Fingerprinting

### 1. Signal Pre-processing
- **Input:** Raw Audio (WAV/MP3)
- **Channels:** Convert to **Mono** (1 channel)
- **Sample Rate:** Downsample to **22,050 Hz**
  - *Lý do:* Nyquist frequency ~11kHz, đủ cho thông tin âm nhạc, giảm kích thước dữ liệu

### 2. Spectrogram Generation
- **Transform:** Discrete Fourier Transform via STFT
- **Window Function:** Hanning Window
- **N_FFT (Window Size):** 4096 samples
  - *Lý do:* Độ phân giải tần số tốt (~5Hz per bin)
- **Hop Length:** 1024 samples (75% overlap)

### 3. Constellation Map (Feature Extraction)
Thay vì match toàn bộ waveform, ta match các "Peaks" (điểm năng lượng cao).

**Algorithm:**
1. Xem Spectrogram như ảnh 2D (Time × Frequency)
2. Áp dụng max-filter với neighborhood 20×20
3. Một điểm (t, f) là "Peak" nếu:
   - Magnitude là maximum trong neighborhood
   - Vượt qua ngưỡng noise (75th percentile)

### 4. Combinatorial Hashing (Fingerprint Generation)
Để làm cho match unique và nhanh, ta ghép các điểm thành cặp.

**Algorithm:**
- **Anchor Point:** Lặp qua mỗi Peak (t₁, f₁)
- **Target Zone:** Cửa sổ phía trước anchor
  - Time: Giữa +1s và +5s sau anchor
- **Hash Function:**
  - Với mỗi Anchor (t₁, f₁) và Target (t₂, f₂) trong zone:
  - `Hash = (f1, f2, t2 - t1)`  *(Cặp tần số và delta thời gian)*
  - `Value = (Song_ID, t1)` *(Lưu thời gian tuyệt đối của anchor)*

### 5. Matching Strategy (Time Coherency)
Cách phân biệt match thật với collision ngẫu nhiên:

1. **Query:** Gửi sample hashes lên DB
2. **Retrieve:** Nhận danh sách matching `(Song_ID, t_db)`
3. **Calculate Offset:** Với mỗi match, tính `delta = t_db - t_sample`
4. **Histogram Analysis:**
   - Nhóm matches theo `Song_ID`
   - Với bài hát đúng, `delta` sẽ constant (tạo peak trong histogram)
   - Với bài hát sai, `delta` sẽ random
   - **Score:** Số lượng của `delta` xuất hiện nhiều nhất

---

## 🌐 API Endpoints

### Base URL
```
http://localhost:8000
```

### API Documentation
```
http://localhost:8000/docs (Swagger UI)
http://localhost:8000/redoc (ReDoc)
```

### Endpoints

#### 1. GET /
**Mô tả:** Root endpoint - API information

**Response:**
```json
{
  "message": "Music Recognition API",
  "version": "1.0.0",
  "endpoints": {
    "POST /learn": "Add a song to the database",
    "POST /recognize": "Recognize a song from audio sample",
    "GET /stats": "Get database statistics",
    "GET /songs": "List all songs in database",
    "DELETE /songs/{song_name}": "Delete a specific song",
    "DELETE /songs": "Clear all songs"
  }
}
```

#### 2. POST /learn
**Mô tả:** Thêm bài hát vào database

**Request:**
- `file` (file, required): Audio file (WAV/MP3/M4A/FLAC)
- `song_name` (string, required): Tên/ID của bài hát

**Response (Success - 200):**
```json
{
  "success": true,
  "song_name": "Test_Song_1",
  "fingerprints_count": 6166,
  "message": "Song 'Test_Song_1' added successfully with 6166 fingerprints"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/learn" \
  -F "file=@song.mp3" \
  -F "song_name=My_Song"
```

#### 3. POST /recognize
**Mô tả:** Nhận diện bài hát từ audio sample

**Request:**
- `file` (file, required): Audio file (WAV/MP3) - thường là recording 5-10 giây

**Response (Success - 200):**
```json
{
  "success": true,
  "song": "Test_Song_1",
  "confidence": 85.5,
  "matches": 42,
  "message": "Recognized as 'Test_Song_1' with 85.50% confidence"
}
```

**Response (Not Found - 200):**
```json
{
  "success": false,
  "song": null,
  "confidence": 0.0,
  "matches": 0,
  "message": "No matching song found in database."
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/recognize" \
  -F "file=@recording.wav"
```

#### 4. GET /stats
**Mô tả:** Lấy thống kê database

**Response:**
```json
{
  "song_count": 10,
  "fingerprint_count": 125430,
  "songs": ["Song_1", "Song_2", ...]
}
```

#### 5. GET /songs
**Mô tả:** Liệt kê tất cả bài hát trong database

**Response:**
```json
{
  "songs": ["Song_1", "Song_2", "Song_3"],
  "count": 3
}
```

#### 6. DELETE /songs/{song_name}
**Mô tả:** Xóa một bài hát cụ thể

**Response:**
```json
{
  "success": true,
  "song_name": "Test_Song_1",
  "deleted_fingerprints": 6166,
  "message": "Song 'Test_Song_1' deleted successfully..."
}
```

#### 7. DELETE /songs
**Mô tả:** Xóa toàn bộ database

**Response:**
```json
{
  "success": true,
  "deleted_songs": 10,
  "deleted_fingerprints": 125430,
  "message": "Database cleared..."
}
```

⚠️ **Warning:** Thao tác này xóa vĩnh viễn tất cả dữ liệu!

---

## 🚀 Hướng Dẫn Setup và Sử Dụng

### Backend Setup

#### 1. Installation
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# hoặc: venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

#### 2. Running Server
```bash
# Development Mode
python3 app/main.py

# Production Mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Server sẽ chạy tại: `http://localhost:8000`

#### 3. Upload Bài Hát
```bash
# Upload từng file
curl -X POST "http://localhost:8000/learn" \
  -F "file=@song.mp3" \
  -F "song_name=My_Song"

# Hoặc upload batch từ thư mục
python3 scripts/batch_upload_songs.py ~/Music/songs
```

### Frontend Setup

#### 1. Installation
```bash
cd lynk
flutter pub get
```

#### 2. Configuration
Cập nhật API URL trong `lib/core/constants/api_constants.dart`:
- **Android Emulator:** `http://10.0.2.2:8000`
- **iOS Simulator:** `http://127.0.0.1:8000`
- **Physical Device:** `http://<your-ip>:8000`

#### 3. Running App
```bash
flutter run
```

### Kết Nối Android Device

Xem chi tiết tại: [ANDROID_CONNECTION_GUIDE.md](./ANDROID_CONNECTION_GUIDE.md)

**Tóm tắt:**
1. Lấy IP address của máy tính: `ipconfig getifaddr en0` (macOS)
2. Cập nhật IP trong code
3. Đảm bảo backend chạy với `--host 0.0.0.0`
4. Đảm bảo device và máy tính cùng mạng WiFi

---

## 🔧 Cấu Trúc Backend

### Module: DSP Engine (`app/core/dsp_engine.py`)

**Class:** `AudioFingerprinter`

**Methods:**
- `load_audio(file_path)`: Load và preprocess audio
- `_compute_spectrogram(audio)`: Tạo spectrogram bằng STFT
- `_find_peaks(spectrogram)`: Tìm peaks bằng 2D max filter
- `generate_fingerprints(audio)`: Tạo fingerprints từ audio

**Parameters:**
- `sample_rate`: 22050 Hz
- `n_fft`: 4096 samples
- `hop_length`: 1024 samples
- `target_zone_bin_min`: 1 second
- `target_zone_bin_max`: 5 seconds

### Module: Database (`app/core/database.py`)

**Class:** `InMemoryDB`

**Data Structure:**
```python
{
  hash_token: [(song_name, absolute_time), ...],
  ...
}
```

**Methods:**
- `add_song(song_name, fingerprints)`: Thêm bài hát
- `query(query_fingerprints)`: Query với time coherency
- `delete_song(song_name)`: Xóa một bài hát
- `clear_all()`: Xóa toàn bộ database
- `get_stats()`: Lấy thống kê

**Hash Token Format:**
- `(f1, f2, dt)` - f1, f2 là tần số (Hz), dt là time delta (bins)

### Module: API Routes (`app/api/routes.py`)

**Endpoints:**
- `POST /learn`: Thêm bài hát
- `POST /recognize`: Nhận diện bài hát
- `GET /stats`: Thống kê database
- `GET /songs`: Danh sách bài hát
- `DELETE /songs/{song_name}`: Xóa một bài hát
- `DELETE /songs`: Xóa toàn bộ

### Scripts

**batch_upload_songs.py:**
- Upload nhiều bài hát từ thư mục
- Hỗ trợ mapping file để đặt tên tùy chỉnh

**create_song_mapping.py:**
- Tạo file mapping từ tên file
- Parse "Artist - Song" format

---

## 📱 Cấu Trúc Frontend

### Clean Architecture

```
Presentation Layer (UI)
    ↓
Domain Layer (Business Logic)
    ↓
Data Layer (API & Local Storage)
```

### Domain Layer

**Entities:**
- `Song`: Thông tin bài hát
- `User`: Thông tin người dùng
- `Message`: Message entity

**Repositories (Interfaces):**
- `MusicRepository`: Interface cho music recognition
- `AuthRepository`: Interface cho authentication
- `MessageRepository`: Interface cho messages

### Data Layer

**Data Sources:**
- `MusicRemoteDataSource`: API calls với Dio
- `AuthLocalDataSource`: Local storage

**Repository Implementations:**
- `MusicRepositoryImpl`: Triển khai MusicRepository
- `AuthRepositoryImpl`: Triển khai AuthRepository
- `MessageRepositoryImpl`: Triển khai MessageRepository

### Presentation Layer

**Pages:**
- `SplashPage`: Màn hình intro với animation
- `MusicHomePage`: Màn hình nhận diện chính
- `RecognitionResultPage`: Màn hình kết quả chi tiết
- `MainPage`: Màn hình chính với tabs
- `HomeTabPage`: Tab Home
- `SettingTabPage`: Tab Settings

**Providers (State Management):**
- `MusicProvider`: Quản lý state recognition
- `PermissionProvider`: Quản lý microphone permission
- `AuthProvider`: Quản lý authentication
- `MessageProvider`: Quản lý messages

### Core Layer

**Constants:**
- `ApiConstants`: API base URL và endpoints
- `AppStrings`: App strings

**Dependency Injection:**
- `InjectionContainer`: Setup providers và repositories

---

## 📊 Workflow

### Workflow 1: Learn Song (Thêm Bài Hát)

```
[Client] POST /learn
    │
    ├─> [FastAPI] Validate file type
    │
    ├─> [AudioFingerprinter] process_file()
    │   ├─> load_audio() → Mono, 22050Hz
    │   └─> generate_fingerprints()
    │       ├─> _compute_spectrogram() → STFT
    │       ├─> _find_peaks() → Max filter
    │       └─> Combinatorial hashing
    │
    ├─> [InMemoryDB] add_song()
    │
    └─> Return success response
```

### Workflow 2: Recognize Song (Nhận Diện)

```
[Client] POST /recognize
    │
    ├─> [FastAPI] Validate file type
    │
    ├─> [AudioFingerprinter] process_file()
    │   └─> Generate fingerprints từ sample
    │
    ├─> [InMemoryDB] query()
    │   ├─> Lookup mỗi hash
    │   ├─> Calculate offsets
    │   └─> Time coherency analysis
    │
    └─> Return recognition result
```

---

## ⚠️ Lưu Ý và Giới Hạn

### Current Limitations

1. **In-Memory Storage:**
   - Mất dữ liệu khi restart server
   - Giới hạn bởi RAM
   - Không persistent

2. **Single Process:**
   - Không hỗ trợ concurrent requests tốt
   - Blocking I/O operations

3. **No Caching:**
   - Mỗi request đều process từ đầu

### Optimization Opportunities

1. **Persistent Storage:**
   - Sử dụng SQLite hoặc PostgreSQL
   - Serialize database to JSON file
   - Periodic backup

2. **Caching:**
   - Cache fingerprints cho popular songs
   - LRU cache cho recent queries

3. **Async Processing:**
   - Use async file I/O
   - Background tasks cho heavy operations

---

## 🔒 Security Considerations

### Current State
- ⚠️ CORS: Allow all origins (dev only)
- ⚠️ No authentication
- ⚠️ No rate limiting
- ⚠️ No file size limits

### Recommendations
1. **CORS:** Chỉ định rõ các origin được phép
2. **Authentication:** Add API keys hoặc JWT tokens
3. **File Validation:** Max file size, type validation
4. **Rate Limiting:** Prevent abuse

---

## 📚 Tài Liệu Tham Khảo

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Scipy Signal Processing](https://docs.scipy.org/doc/scipy/reference/signal.html)
- [Audio Fingerprinting Algorithm](https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf)
- [Flutter Documentation](https://flutter.dev/docs)

---

## 🎯 Kết Luận

Dự án **Music Recognition System** được thiết kế với:
- ✅ Kiến trúc rõ ràng và modular
- ✅ API RESTful đầy đủ
- ✅ DSP processing chính xác
- ✅ Clean Architecture cho Flutter app
- ✅ Tools và scripts hỗ trợ

Sẵn sàng cho development và có thể mở rộng cho production.
