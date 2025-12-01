# 🏗️ Tổng Quan Kiến Trúc Hệ Thống - Music Recognition System

## 📋 Mục Lục

1. [Tổng Quan Hệ Thống](#tổng-quan-hệ-thống)
2. [Kiến Trúc Tổng Thể](#kiến-trúc-tổng-thể)
3. [Module Backend](#module-backend)
4. [Module Desktop](#module-desktop)
5. [Module Mobile](#module-mobile)
6. [Luồng Xử Lý](#luồng-xử-lý)
7. [Công Nghệ Sử Dụng](#công-nghệ-sử-dụng)
8. [Giao Tiếp Giữa Các Module](#giao-tiếp-giữa-các-module)

---

## 🎯 Tổng Quan Hệ Thống

**Music Recognition System** là hệ thống nhận diện bài hát tương tự Shazam, được phát triển với 3 module chính:

- **Backend (Python/FastAPI)**: Xử lý DSP, tạo fingerprint và matching
- **Desktop App (Python/Tkinter)**: Ứng dụng desktop để ghi âm và nhận diện
- **Mobile App (Flutter)**: Ứng dụng mobile với UI/UX hiện đại

### Đặc Điểm Chính

- ✅ **Audio Fingerprinting**: Sử dụng thuật toán của Avery Wang (Shazam)
- ✅ **Multi-Platform**: Hỗ trợ Desktop và Mobile
- ✅ **Real-time Recognition**: Nhận diện trong 5-10 giây
- ✅ **RESTful API**: Giao tiếp qua HTTP/REST
- ✅ **Persistent Database**: Lưu trữ fingerprints trong SQLite

---

## 🏗️ Kiến Trúc Tổng Thể

```
┌─────────────────────────────────────────────────────────────────┐
│                    Music Recognition System                      │
│                                                                  │
│  ┌──────────────────┐      ┌──────────────────┐                │
│  │  Mobile App      │      │  Desktop App     │                │
│  │  (Flutter)       │      │  (Python/Tkinter)│                │
│  │                  │      │                  │                │
│  │  - Ghi âm        │      │  - Ghi âm         │                │
│  │  - UI/UX         │      │  - UI Desktop     │                │
│  │  - Animation     │      │  - Progress       │                │
│  └────────┬─────────┘      └────────┬─────────┘                │
│           │                         │                            │
│           │  HTTP/REST              │  HTTP/REST                │
│           │  Multipart Form Data    │  Multipart Form Data      │
│           │                         │                            │
│           └─────────────┬───────────┘                            │
│                         │                                        │
│                         ▼                                        │
│           ┌────────────────────────────────────┐                 │
│           │     Backend Server                 │                 │
│           │     (Python/FastAPI)               │                 │
│           │                                    │                 │
│           │  ┌────────────────────────────┐  │                 │
│           │  │  API Layer (routes.py)      │  │                 │
│           │  │  - POST /learn              │  │                 │
│           │  │  - POST /recognize          │  │                 │
│           │  │  - GET /stats                │  │                 │
│           │  │  - GET /songs                │  │                 │
│           │  │  - DELETE /songs             │  │                 │
│           │  └──────────┬───────────────────┘  │                 │
│           │             │                        │                 │
│           │  ┌──────────▼───────────────────┐  │                 │
│           │  │  DSP Engine                  │  │                 │
│           │  │  (dsp_engine.py)             │  │                 │
│           │  │  - Audio Processing          │  │                 │
│           │  │  - Spectrogram                │  │                 │
│           │  │  - Peak Finding               │  │                 │
│           │  │  - Fingerprint Generation     │  │                 │
│           │  └──────────┬───────────────────┘  │                 │
│           │             │                        │                 │
│           │  ┌──────────▼───────────────────┐  │                 │
│           │  │  Database                    │  │                 │
│           │  │  (database.py)                │  │                 │
│           │  │  - SQLite (Persistent)        │  │                 │
│           │  │  - Fingerprint Storage        │  │                 │
│           │  │  - Query & Matching           │  │                 │
│           │  └───────────────────────────────┘  │                 │
│           └────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Module Backend

### Tổng Quan

Backend là trái tim của hệ thống, xử lý tất cả logic DSP và matching.

### Cấu Trúc

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/
│   │   └── routes.py        # API endpoints definition
│   └── core/
│       ├── dsp_engine.py    # Audio fingerprinting engine
│       └── database.py       # Database operations
├── scripts/                 # Utility scripts
│   ├── batch_upload_songs.py
│   └── music_crawler.py
└── docs/                    # Documentation
```

### Thành Phần Chính

#### 1. **API Layer** (`app/api/routes.py`)

**Chức năng:**
- Xử lý HTTP requests từ clients
- Validate file uploads
- Route requests đến các components phù hợp
- Trả về JSON responses

**Endpoints:**
- `POST /learn`: Thêm bài hát vào database
- `POST /recognize`: Nhận diện bài hát từ audio sample
- `GET /stats`: Lấy thống kê database
- `GET /songs`: Liệt kê tất cả bài hát
- `DELETE /songs/{song_name}`: Xóa bài hát cụ thể
- `DELETE /songs`: Xóa toàn bộ database

**Đặc điểm:**
- CORS middleware cho cross-origin requests
- File validation (WAV, MP3)
- Error handling chi tiết
- Logging đầy đủ

#### 2. **DSP Engine** (`app/core/dsp_engine.py`)

**Chức năng:**
- Xử lý audio signal
- Tạo audio fingerprints
- Implement thuật toán Shazam

**Quy trình xử lý:**

```
Audio File
    ↓
Load & Preprocess
    ├─> Load audio (soundfile)
    ├─> Convert to mono
    └─> Resample to 22050 Hz
    ↓
Compute Spectrogram
    └─> STFT (Short-Time Fourier Transform)
    ↓
Find Peaks
    └─> Maximum filter (20×20 window)
    ↓
Generate Fingerprints
    └─> Combinatorial hashing
        └─> Create (f1, f2, dt) hashes
```

**Thuật toán:**
- **Spectrogram**: STFT với window size 2048, overlap 50%
- **Peak Finding**: Maximum filter với window 20×20
- **Fingerprinting**: Tạo hash từ pairs of peaks (frequency1, frequency2, time_delta)

#### 3. **Database** (`app/core/database.py`)

**Chức năng:**
- Lưu trữ fingerprints
- Query và matching
- Quản lý songs

**Cấu trúc:**
- **SQLite Database**: Persistent storage
- **Tables**:
  - `songs`: Thông tin bài hát
  - `fingerprints`: Hash fingerprints với song_id và time offset

**Operations:**
- `add_song()`: Thêm bài hát và fingerprints
- `query()`: Tìm matching song từ query fingerprints
- `delete_song()`: Xóa bài hát
- `get_stats()`: Thống kê database

### Công Nghệ

- **Language**: Python 3.9+
- **Framework**: FastAPI
- **Server**: Uvicorn (ASGI)
- **DSP Libraries**: scipy, numpy, soundfile
- **Database**: SQLite (via sqlite3)

### Đặc Điểm Kỹ Thuật

- ✅ **Async/Await**: Xử lý requests không đồng bộ
- ✅ **File Upload**: Multipart form data
- ✅ **Error Handling**: Comprehensive error responses
- ✅ **Logging**: Chi tiết cho debugging
- ✅ **CORS**: Hỗ trợ cross-origin requests

---

## 💻 Module Desktop

### Tổng Quan

Desktop application cho phép người dùng ghi âm và nhận diện bài hát trên máy tính.

### Cấu Trúc

```
lynk_desktop/
├── main.py              # Main application với UI
├── audio_recorder.py    # Module ghi âm
├── api_client.py        # Module giao tiếp với API
├── config.py            # File cấu hình
├── requirements.txt     # Dependencies
└── README.md           # Documentation
```

### Thành Phần Chính

#### 1. **Main Application** (`main.py`)

**Chức năng:**
- UI với Tkinter
- Quản lý state (recording, processing, result)
- Xử lý user interactions
- Hiển thị kết quả

**UI Components:**
- **Header**: Title với màu sắc chủ đạo
- **Recording Section**: 
  - Nút ghi âm (circular button)
  - Timer hiển thị thời gian
  - Status label
- **Result Section**:
  - Tên bài hát
  - Độ chính xác (%)
  - Số matches
- **Status Bar**: Hiển thị server connection

**Features:**
- Progress indicator với animation
- Error handling với thông báo chi tiết
- Thread-safe UI updates
- Auto-reset sau mỗi lần nhận diện

#### 2. **Audio Recorder** (`audio_recorder.py`)

**Chức năng:**
- Ghi âm từ microphone
- Lưu file WAV tạm thời
- Quản lý audio stream

**Cấu hình:**
- Sample rate: 44100 Hz
- Channels: Mono
- Format: 16-bit PCM
- Duration: 10 giây (có thể cấu hình)

**Đặc điểm:**
- Sử dụng PyAudio
- Tự động chọn input device
- Fallback nếu device không khả dụng
- Error handling cho microphone issues

#### 3. **API Client** (`api_client.py`)

**Chức năng:**
- Giao tiếp với backend server
- Upload audio file
- Xử lý responses
- Error handling

**Features:**
- Dynamic timeout dựa trên file size
- JSON parsing an toàn
- Chi tiết error messages
- Connection testing
- Logging đầy đủ

**Error Handling:**
- Connection errors
- Timeout errors
- Server errors (500, 400, 404)
- JSON parsing errors

### Công Nghệ

- **Language**: Python 3.7+
- **GUI Framework**: Tkinter (built-in)
- **Audio**: PyAudio
- **HTTP**: requests
- **Logging**: Python logging module

### Đặc Điểm Kỹ Thuật

- ✅ **Threading**: Background threads cho recording và recognition
- ✅ **Thread-safe UI**: Sử dụng `root.after()` cho UI updates
- ✅ **Progress Indicator**: Animation khi xử lý
- ✅ **Error Recovery**: Tự động reset state sau lỗi
- ✅ **Configurable**: Tất cả settings trong `config.py`

---

## 📱 Module Mobile

### Tổng Quan

Mobile application với Flutter, cung cấp UI/UX hiện đại và trải nghiệm tốt.

### Cấu Trúc

```
lynk/lib/
├── main.dart                    # Entry point
├── core/
│   ├── constants/              # API constants
│   ├── utils/                  # Utilities
│   └── di/                     # Dependency injection
├── data/
│   ├── datasources/            # Remote data source
│   └── repositories/           # Repository implementations
├── domain/
│   ├── entities/              # Business entities
│   └── repositories/          # Repository interfaces
└── presentation/
    ├── pages/                 # UI pages
    │   ├── music_home_page.dart
    │   └── recognition_result_page.dart
    └── providers/             # State management
        └── music_provider.dart
```

### Thành Phần Chính

#### 1. **Presentation Layer**

**Pages:**
- **MusicHomePage**: 
  - Giao diện ghi âm
  - Nút ghi âm với animation
  - Timer hiển thị thời gian
  - Auto-stop sau 10 giây
  
- **RecognitionResultPage**:
  - Hiển thị kết quả nhận diện
  - Tên bài hát, artist
  - Confidence percentage
  - Buttons: Spotify, YouTube

**Providers:**
- **MusicProvider**: Quản lý state
  - Recording state
  - Recognition result
  - Error handling

#### 2. **Data Layer**

**Data Sources:**
- **MusicRemoteDataSource**: 
  - Gửi file lên server
  - Xử lý HTTP requests
  - Error handling

**Repositories:**
- **MusicRepositoryImpl**: 
  - Implement business logic
  - Parse responses
  - Create entities

#### 3. **Domain Layer**

**Entities:**
- **Song**: 
  - title, artist, album
  - confidence, matches
  - spotifyUrl, youtubeUrl

**Repositories:**
- **MusicRepository**: Interface cho data operations

### Công Nghệ

- **Framework**: Flutter
- **Language**: Dart
- **HTTP**: Dio package
- **Audio Recording**: record package
- **State Management**: Provider
- **Architecture**: Clean Architecture

### Đặc Điểm Kỹ Thuật

- ✅ **Clean Architecture**: Tách biệt layers rõ ràng
- ✅ **State Management**: Provider pattern
- ✅ **Animations**: Smooth UI animations
- ✅ **Error Handling**: User-friendly error messages
- ✅ **Platform Detection**: Auto-detect iOS/Android
- ✅ **URL Handling**: Deep links cho Spotify/YouTube

---

## 🔄 Luồng Xử Lý

### Luồng Nhận Diện Bài Hát

```
┌─────────────────────────────────────────────────────────────┐
│                    Recognition Flow                          │
└─────────────────────────────────────────────────────────────┘

[Client - Mobile/Desktop]
    │
    ├─> 1. User nhấn nút "Ghi âm"
    │
    ├─> 2. Bắt đầu ghi âm (10 giây)
    │   ├─> Record audio từ microphone
    │   ├─> Lưu file WAV/M4A tạm thời
    │   └─> Hiển thị timer và animation
    │
    ├─> 3. Tự động dừng sau 10 giây
    │
    ├─> 4. Upload file lên server
    │   ├─> POST /recognize
    │   ├─> Multipart form data
    │   └─> Hiển thị "Đang xử lý..."
    │
    ▼
[Backend Server]
    │
    ├─> 5. Nhận file upload
    │   ├─> Validate file type
    │   └─> Lưu tạm thời
    │
    ├─> 6. Xử lý audio (DSP Engine)
    │   ├─> Load audio file
    │   ├─> Preprocess (mono, resample)
    │   ├─> Compute spectrogram (STFT)
    │   ├─> Find peaks
    │   └─> Generate fingerprints
    │
    ├─> 7. Query database
    │   ├─> Lookup fingerprints
    │   ├─> Calculate time offsets
    │   ├─> Time coherency analysis
    │   └─> Find best match
    │
    ├─> 8. Trả về kết quả
    │   ├─> Song name
    │   ├─> Confidence (%)
    │   └─> Number of matches
    │
    ▼
[Client - Mobile/Desktop]
    │
    ├─> 9. Nhận response
    │
    ├─> 10. Hiển thị kết quả
    │   ├─> Tên bài hát
    │   ├─> Độ chính xác
    │   └─> Số matches
    │
    └─> 11. Options: Ghi âm lại / Mở Spotify/YouTube
```

### Luồng Thêm Bài Hát (Learn)

```
[Client/Admin]
    │
    ├─> POST /learn
    │   ├─> File: audio file (MP3/WAV)
    │   └─> Form: song_name
    │
    ▼
[Backend]
    │
    ├─> Validate file
    │
    ├─> Process audio (DSP Engine)
    │   └─> Generate fingerprints
    │
    ├─> Store in database
    │   ├─> Add song record
    │   └─> Store all fingerprints
    │
    └─> Return success + fingerprint count
```

---

## 🛠️ Công Nghệ Sử Dụng

### Backend

| Component | Technology |
|-----------|-----------|
| Language | Python 3.9+ |
| Framework | FastAPI |
| Server | Uvicorn (ASGI) |
| DSP | scipy, numpy, soundfile |
| Database | SQLite |
| HTTP | FastAPI built-in |

### Desktop

| Component | Technology |
|-----------|-----------|
| Language | Python 3.7+ |
| GUI | Tkinter |
| Audio | PyAudio |
| HTTP | requests |
| Config | Python config file |

### Mobile

| Component | Technology |
|-----------|-----------|
| Framework | Flutter |
| Language | Dart |
| HTTP | Dio |
| Audio | record package |
| State | Provider |
| Architecture | Clean Architecture |

---

## 🔌 Giao Tiếp Giữa Các Module

### API Contract

**Base URL**: `http://localhost:8000` (hoặc configurable)

**Endpoints:**

1. **POST /recognize**
   - **Request**: Multipart form data với file audio
   - **Response**: 
     ```json
     {
       "success": true,
       "song": "Song Name",
       "confidence": 95.5,
       "matches": 150,
       "message": "Recognized as 'Song Name' with 95.5% confidence"
     }
     ```

2. **POST /learn**
   - **Request**: Multipart form data với file + song_name
   - **Response**:
     ```json
     {
       "success": true,
       "song_name": "Song Name",
       "fingerprints_count": 50000,
       "message": "Song added successfully"
     }
     ```

3. **GET /stats**
   - **Response**:
     ```json
     {
       "song_count": 4,
       "fingerprint_count": 1653066,
       "songs": ["Song 1", "Song 2", ...]
     }
     ```

### Error Responses

**Format:**
```json
{
  "success": false,
  "error": true,
  "status_code": 500,
  "message": "Error message",
  "detail": "Detailed error information"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad Request (invalid file)
- `404`: Not Found (endpoint không tồn tại)
- `500`: Internal Server Error

### Communication Flow

```
┌─────────────┐
│   Client   │
│ (Mobile/   │
│  Desktop)  │
└─────┬──────┘
      │
      │ HTTP POST /recognize
      │ Content-Type: multipart/form-data
      │ Body: file=<audio_file>
      │
      ▼
┌─────────────┐
│   Backend   │
│   Server    │
└─────┬──────┘
      │
      │ Process & Query
      │
      │ HTTP 200 OK
      │ Content-Type: application/json
      │ Body: {success, song, confidence, ...}
      │
      ▼
┌─────────────┐
│   Client   │
│ (Display    │
│  Result)   │
└─────────────┘
```

---

## 📊 So Sánh Các Module

| Feature | Backend | Desktop | Mobile |
|---------|---------|---------|--------|
| **Platform** | Server | Windows/macOS/Linux | iOS/Android |
| **UI** | API only | Tkinter | Flutter |
| **Audio** | Processing | PyAudio | record package |
| **Architecture** | REST API | MVC | Clean Architecture |
| **State** | Stateless | Local state | Provider |
| **Error Handling** | HTTP status | Messagebox | Snackbar/Dialog |
| **Animation** | N/A | Basic | Advanced |

---

## 🎯 Kết Luận

Hệ thống Music Recognition được thiết kế với kiến trúc modular, cho phép:

- ✅ **Tách biệt concerns**: Mỗi module có trách nhiệm riêng
- ✅ **Scalability**: Dễ dàng mở rộng và thêm features
- ✅ **Maintainability**: Code rõ ràng, có documentation
- ✅ **Cross-platform**: Hỗ trợ nhiều platform
- ✅ **User Experience**: UI/UX tốt trên cả desktop và mobile

Ba module hoạt động độc lập nhưng tích hợp chặt chẽ thông qua REST API, tạo nên một hệ thống hoàn chỉnh và mạnh mẽ.



