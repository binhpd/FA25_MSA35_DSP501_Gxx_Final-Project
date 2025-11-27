# Tài Liệu Chi Tiết Backend - Music Recognition System

## 📋 Mục Lục

1. [Tổng Quan](#tổng-quan)
2. [Kiến Trúc Hệ Thống](#kiến-trúc-hệ-thống)
3. [Cấu Trúc Thư Mục](#cấu-trúc-thư-mục)
4. [Thiết Kế Database](#thiết-kế-database)
5. [DSP Engine - Audio Fingerprinting](#dsp-engine---audio-fingerprinting)
6. [API Endpoints](#api-endpoints)
7. [Workflow và Luồng Xử Lý](#workflow-và-luồng-xử-lý)
8. [Công Cụ và Scripts](#công-cụ-và-scripts)
9. [Deployment và Configuration](#deployment-và-configuration)

---

## 🎯 Tổng Quan

### Mục Đích
Backend server cung cấp API để nhận diện bài hát sử dụng Audio Fingerprinting (thuật toán tương tự Shazam).

### Công Nghệ
- **Language:** Python 3.9+
- **Framework:** FastAPI
- **Server:** Uvicorn (ASGI)
- **DSP Libraries:** scipy, numpy, soundfile
- **Storage:** In-Memory Dictionary (Python dict)

### Kiến Trúc
- **Thin Client (Flutter)** - Ghi âm và gửi request
- **Fat Server (Python)** - Xử lý DSP và matching

---

## 🏗️ Kiến Trúc Hệ Thống

### High-Level Architecture

```
┌─────────────────┐
│  Flutter App    │
│  (Client)       │
└────────┬────────┘
         │ HTTP/REST
         │ Multipart Form Data
         ▼
┌─────────────────────────────────┐
│  FastAPI Server                 │
│  (main.py)                      │
│  - CORS Middleware              │
│  - Request Validation           │
│  - File Upload Handling         │
└────────┬────────────────────────┘
         │
         ├─────────────────┬─────────────────┐
         ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ DSP Engine   │  │  Database    │  │  File Temp  │
│ (dsp_engine) │  │ (database)   │  │  Storage    │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  API Layer (main.py)                            │  │
│  │  - POST /learn                                  │  │
│  │  - POST /recognize                              │  │
│  │  - GET /stats                                   │  │
│  │  - GET /songs                                   │  │
│  │  - DELETE /songs/{song_name}                    │  │
│  │  - DELETE /songs                                │  │
│  └──────────────┬──────────────────────────────────┘  │
│                 │                                      │
│  ┌──────────────▼──────────────────────────────────┐  │
│  │  AudioFingerprinter (dsp_engine.py)            │  │
│  │  - load_audio()                                 │  │
│  │  - _compute_spectrogram()                       │  │
│  │  - _find_peaks()                                │  │
│  │  - generate_fingerprints()                      │  │
│  └──────────────┬──────────────────────────────────┘  │
│                 │                                      │
│  ┌──────────────▼──────────────────────────────────┐  │
│  │  InMemoryDB (database.py)                       │  │
│  │  - add_song()                                   │  │
│  │  - query()                                      │  │
│  │  - delete_song()                                │  │
│  │  - clear_all()                                  │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Cấu Trúc Thư Mục

```
backend/
├── main.py                    # FastAPI application & API endpoints
├── dsp_engine.py              # Audio fingerprinting engine
├── database.py                # In-memory database implementation
├── requirements.txt           # Python dependencies
├── README.md                  # Quick start guide
│
├── test_data/                 # Test data và scripts
│   ├── create_test_audio.py   # Tạo audio test synthetic
│   ├── download_test_songs.py # Download audio từ internet
│   ├── test_api.py            # Test API endpoints
│   ├── test_upload_wav.py     # Test upload WAV files
│   ├── test_delete_songs.py   # Test delete APIs
│   ├── song_mapping.json      # Mapping file names → song names
│   └── *.wav, *.mp3           # Test audio files
│
├── batch_upload_songs.py      # Script batch upload nhiều bài hát
├── create_song_mapping.py     # Script tạo mapping file
│
├── venv/                      # Python virtual environment
│
└── Documentation/
    ├── BACKEND_DOCUMENTATION.md    # File này
    ├── GUIDE_BATCH_UPLOAD.md       # Hướng dẫn upload batch
    ├── DELETE_SONGS_GUIDE.md       # Hướng dẫn xóa bài hát
    └── QUICK_UPLOAD_GUIDE.md       # Hướng dẫn nhanh
```

---

## 🗄️ Thiết Kế Database

### 1. Cấu Trúc Dữ Liệu

#### In-Memory Dictionary Structure

```python
class InMemoryDB:
    def __init__(self):
        # Main database: {hash_token: [(song_name, absolute_time), ...]}
        self.db: dict = {}
        
        # Song list: set of song names
        self.song_list: set = set()
```

#### Database Schema (Conceptual)

```
┌─────────────────────────────────────────────────┐
│  Hash Table (self.db)                            │
│                                                  │
│  Key: (f1, f2, dt)                              │
│  └─> List of (song_name, absolute_time)         │
│                                                  │
│  Example:                                       │
│  (440, 523, 10) → [                             │
│    ("Song_A", 2.5),                             │
│    ("Song_A", 15.3),                            │
│    ("Song_B", 8.2)                              │
│  ]                                               │
│                                                  │
│  (523, 659, 15) → [                             │
│    ("Song_A", 3.0),                             │
│    ("Song_C", 1.5)                              │
│  ]                                               │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Song List (self.song_list)                     │
│                                                  │
│  Set: {"Song_A", "Song_B", "Song_C", ...}      │
└─────────────────────────────────────────────────┘
```

### 2. Hash Token Format

**Structure:** `(f1, f2, dt)`

- **f1** (int): Tần số của anchor point (Hz)
- **f2** (int): Tần số của target point (Hz)
- **dt** (int): Time delta giữa anchor và target (số bins)

**Example:**
```python
hash_token = (440, 523, 10)
# Anchor: 440 Hz tại time t1
# Target: 523 Hz tại time t2
# Delta: t2 - t1 = 10 bins
```

### 3. Data Storage Format

**Value Format:** `(song_name, absolute_time)`

- **song_name** (str): Tên/ID của bài hát
- **absolute_time** (float): Thời điểm tuyệt đối trong bài hát (giây)

**Example:**
```python
("Happy Birthday", 12.5)
# Bài hát "Happy Birthday" có fingerprint này tại 12.5 giây
```

### 4. Database Operations

#### 4.1. Add Song
```python
def add_song(song_name: str, fingerprints: List[Tuple]) -> int:
    """
    Thêm bài hát vào database
    
    Process:
    1. Add song_name vào song_list
    2. Với mỗi fingerprint (hash, time):
       - Nếu hash chưa có → tạo entry mới
       - Append (song_name, time) vào hash entry
    3. Return số fingerprints đã thêm
    """
```

**Time Complexity:** O(n) với n = số fingerprints

#### 4.2. Query
```python
def query(query_fingerprints: List[Tuple], min_matches: int = 5):
    """
    Query database để tìm bài hát match
    
    Process:
    1. Lookup mỗi hash trong query
    2. Tính offset = db_time - sample_time
    3. Group matches theo song_name
    4. Time coherency analysis:
       - Count offsets cho mỗi song
       - Tìm song có offset xuất hiện nhiều nhất
    5. Return best match
    """
```

**Time Complexity:** O(n*m) với n = query fingerprints, m = avg matches per hash

#### 4.3. Delete Song
```python
def delete_song(song_name: str) -> Tuple[bool, int]:
    """
    Xóa một bài hát
    
    Process:
    1. Check song exists
    2. Iterate qua tất cả hash entries
    3. Filter out entries có song_name
    4. Remove empty hash entries
    5. Remove từ song_list
    """
```

**Time Complexity:** O(h) với h = số hash entries

### 5. Database Statistics

**Metrics:**
- `song_count`: Số bài hát trong database
- `fingerprint_count`: Tổng số fingerprints
- `songs`: Danh sách tên bài hát

**Example:**
```python
{
    "song_count": 10,
    "fingerprint_count": 125430,
    "songs": ["Song_1", "Song_2", ..., "Song_10"]
}
```

---

## 🎵 DSP Engine - Audio Fingerprinting

### 1. Class: AudioFingerprinter

**File:** `dsp_engine.py`

**Purpose:** Xử lý audio và tạo fingerprints

### 2. Audio Preprocessing

#### Method: `load_audio(file_path)`

**Input:** Đường dẫn file audio (WAV/MP3)

**Process:**
1. Load audio file bằng `soundfile.read()`
2. Convert stereo → mono (nếu cần)
3. Resample về 22050 Hz (nếu cần)

**Output:** Mono audio signal (1D numpy array) ở 22050 Hz

**Code:**
```python
def load_audio(self, file_path: str) -> np.ndarray:
    # Load với soundfile (không cần numba)
    audio, sr = sf.read(file_path)
    
    # Convert to mono
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
    
    # Resample to 22050 Hz
    if sr != 22050:
        num_samples = int(len(audio) * 22050 / sr)
        audio = resample(audio, num_samples)
    
    return audio
```

### 3. Spectrogram Generation

#### Method: `_compute_spectrogram(audio)`

**Algorithm:** Short-Time Fourier Transform (STFT)

**Parameters:**
- **n_fft:** 4096 samples (window size)
- **hop_length:** 1024 samples (75% overlap)
- **window:** Hanning window
- **sample_rate:** 22050 Hz

**Output:**
- **magnitude:** Magnitude spectrogram (freq_bins × time_bins)
- **times:** Time bins array (seconds)
- **frequencies:** Frequency bins array (Hz)

**Code:**
```python
def _compute_spectrogram(self, audio: np.ndarray) -> tuple:
    from scipy.signal import stft
    
    window = np.hanning(self.n_fft)
    frequencies, times, stft_result = stft(
        audio,
        fs=self.sample_rate,
        window=window,
        nperseg=self.n_fft,
        noverlap=self.n_fft - self.hop_length,
        nfft=self.n_fft,
        return_onesided=True
    )
    
    magnitude = np.abs(stft_result)
    return magnitude, times, frequencies
```

**Spectrogram Shape:**
- Rows (frequencies): ~2049 bins (0-11025 Hz)
- Columns (times): ~(audio_length / hop_length) bins

### 4. Peak Detection

#### Method: `_find_peaks(spectrogram)`

**Algorithm:** 2D Local Maximum Filter

**Process:**
1. Apply maximum filter với neighborhood 20×20
2. Find points where original == local_max
3. Apply threshold (75th percentile)
4. Return peak coordinates (time_idx, freq_idx)

**Code:**
```python
def _find_peaks(self, spectrogram: np.ndarray) -> list:
    # Maximum filter
    neighborhood = np.ones((20, 20))
    local_max = maximum_filter(spectrogram, footprint=neighborhood)
    
    # Find peaks
    peaks_mask = (spectrogram == local_max) & (spectrogram > 0)
    
    # Threshold (75th percentile)
    threshold = np.percentile(spectrogram[peaks_mask], 75)
    peaks_mask = peaks_mask & (spectrogram >= threshold)
    
    # Get coordinates
    freq_indices, time_indices = np.where(peaks_mask)
    return list(zip(time_indices, freq_indices))
```

**Output:** List of `(time_idx, freq_idx)` tuples

### 5. Fingerprint Generation

#### Method: `generate_fingerprints(audio)`

**Algorithm:** Combinatorial Hashing (Avery Wang's Algorithm)

**Process:**
1. Compute spectrogram
2. Find peaks
3. For each anchor peak:
   - Find target peaks trong zone 1-5 seconds
   - Create hash: `(f1, f2, dt)`
   - Store: `(hash, absolute_time)`

**Code:**
```python
def generate_fingerprints(self, audio: np.ndarray) -> list:
    spectrogram, times, frequencies = self._compute_spectrogram(audio)
    peaks = self._find_peaks(spectrogram)
    
    fingerprints = []
    
    for anchor_time_idx, anchor_freq_idx in peaks:
        anchor_time = times[anchor_time_idx]
        anchor_freq = frequencies[anchor_freq_idx]
        
        # Target zone: 1-5 seconds ahead
        time_min = anchor_time_idx + self.target_zone_bin_min
        time_max = min(anchor_time_idx + self.target_zone_bin_max, len(times))
        
        # Find target peaks in zone
        target_peaks = [
            (t_idx, f_idx) for t_idx, f_idx in peaks
            if time_min <= t_idx < time_max
        ]
        
        # Create hashes
        for target_time_idx, target_freq_idx in target_peaks:
            target_freq = frequencies[target_freq_idx]
            dt = target_time_idx - anchor_time_idx
            
            hash_token = (int(anchor_freq), int(target_freq), int(dt))
            fingerprints.append((hash_token, anchor_time))
    
    return fingerprints
```

**Output:** List of `((f1, f2, dt), absolute_time)` tuples

**Example:**
```python
[
    ((440, 523, 10), 0.5),   # Hash tại 0.5s
    ((523, 659, 15), 0.5),   # Hash tại 0.5s
    ((440, 392, 8), 1.2),    # Hash tại 1.2s
    ...
]
```

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

---

### 1. GET /

**Mô tả:** Root endpoint - API information

**Request:**
```http
GET /
```

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

---

### 2. POST /learn

**Mô tả:** Thêm bài hát vào database

**Request:**
```http
POST /learn
Content-Type: multipart/form-data

file: <audio_file>
song_name: <song_name>
```

**Parameters:**
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

**Response (Error - 400):**
```json
{
  "detail": "Invalid file type. Please upload an audio file (WAV, MP3, etc.)"
}
```

**Response (Error - 500):**
```json
{
  "detail": "Error processing audio file: <error_message>"
}
```

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/learn" \
  -F "file=@song.mp3" \
  -F "song_name=My_Song"
```

**Example (Python):**
```python
import requests

with open('song.mp3', 'rb') as f:
    files = {'file': ('song.mp3', f, 'audio/mpeg')}
    data = {'song_name': 'My_Song'}
    response = requests.post('http://localhost:8000/learn', files=files, data=data)
    print(response.json())
```

---

### 3. POST /recognize

**Mô tả:** Nhận diện bài hát từ audio sample

**Request:**
```http
POST /recognize
Content-Type: multipart/form-data

file: <audio_file>
```

**Parameters:**
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

**Response (Empty Database - 200):**
```json
{
  "success": false,
  "song": null,
  "confidence": 0.0,
  "matches": 0,
  "message": "Database is empty. Please add songs first using /learn endpoint."
}
```

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/recognize" \
  -F "file=@recording.wav"
```

**Example (Python):**
```python
import requests

with open('recording.wav', 'rb') as f:
    files = {'file': ('recording.wav', f, 'audio/wav')}
    response = requests.post('http://localhost:8000/recognize', files=files)
    result = response.json()
    if result['success']:
        print(f"Recognized: {result['song']} ({result['confidence']}%)")
```

---

### 4. GET /stats

**Mô tả:** Lấy thống kê database

**Request:**
```http
GET /stats
```

**Response:**
```json
{
  "song_count": 10,
  "fingerprint_count": 125430,
  "songs": [
    "Song_1",
    "Song_2",
    "Song_3",
    ...
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/stats | python3 -m json.tool
```

---

### 5. GET /songs

**Mô tả:** Liệt kê tất cả bài hát trong database

**Request:**
```http
GET /songs
```

**Response:**
```json
{
  "songs": [
    "Song_1",
    "Song_2",
    "Song_3"
  ],
  "count": 3
}
```

**Example:**
```bash
curl http://localhost:8000/songs | python3 -m json.tool
```

---

### 6. DELETE /songs/{song_name}

**Mô tả:** Xóa một bài hát cụ thể

**Request:**
```http
DELETE /songs/{song_name}
```

**Path Parameters:**
- `song_name` (string, required): Tên bài hát cần xóa (URL encoded nếu có khoảng trắng)

**Response (Success - 200):**
```json
{
  "success": true,
  "song_name": "Test_Song_1",
  "deleted_fingerprints": 6166,
  "message": "Song 'Test_Song_1' deleted successfully. Removed 6166 fingerprints."
}
```

**Response (Not Found - 404):**
```json
{
  "success": false,
  "song_name": "NonExistent_Song",
  "deleted_fingerprints": 0,
  "message": "Song 'NonExistent_Song' not found in database."
}
```

**Example (cURL):**
```bash
# Tên không có khoảng trắng
curl -X DELETE "http://localhost:8000/songs/Test_Song_1"

# Tên có khoảng trắng (URL encode)
curl -X DELETE "http://localhost:8000/songs/test%20song%201"
```

**Example (Python):**
```python
import requests

song_name = "Test_Song_1"
response = requests.delete(f"http://localhost:8000/songs/{song_name}")
print(response.json())
```

---

### 7. DELETE /songs

**Mô tả:** Xóa toàn bộ database

**Request:**
```http
DELETE /songs
```

**Response:**
```json
{
  "success": true,
  "deleted_songs": 10,
  "deleted_fingerprints": 125430,
  "message": "Database cleared. Deleted 10 songs and 125430 fingerprints."
}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/songs"
```

**⚠️ Warning:** Thao tác này xóa vĩnh viễn tất cả dữ liệu!

---

## 🔄 Workflow và Luồng Xử Lý

### Workflow 1: Learn Song (Thêm Bài Hát)

```
[Client] POST /learn
    │
    ├─> [FastAPI] Validate file type
    │
    ├─> [FastAPI] Save to temp file
    │
    ├─> [AudioFingerprinter] process_file()
    │   ├─> load_audio()
    │   │   ├─> Load file (soundfile)
    │   │   ├─> Convert to mono
    │   │   └─> Resample to 22050 Hz
    │   │
    │   └─> generate_fingerprints()
    │       ├─> _compute_spectrogram()
    │       │   └─> STFT (scipy.signal.stft)
    │       │
    │       ├─> _find_peaks()
    │       │   └─> Maximum filter (20×20)
    │       │
    │       └─> Combinatorial hashing
    │           └─> Create (f1, f2, dt) hashes
    │
    ├─> [InMemoryDB] add_song()
    │   └─> Store fingerprints in database
    │
    └─> [FastAPI] Return success response
```

**Time Complexity:**
- Audio loading: O(n) với n = số samples
- STFT: O(n log n)
- Peak finding: O(f × t) với f = freq bins, t = time bins
- Fingerprint generation: O(p²) với p = số peaks
- Database storage: O(f) với f = số fingerprints

**Total:** ~O(n log n + p²) cho một bài hát

---

### Workflow 2: Recognize Song (Nhận Diện)

```
[Client] POST /recognize
    │
    ├─> [FastAPI] Validate file type
    │
    ├─> [FastAPI] Check database not empty
    │
    ├─> [FastAPI] Save to temp file
    │
    ├─> [AudioFingerprinter] process_file()
    │   └─> Generate fingerprints từ sample
    │
    ├─> [InMemoryDB] query()
    │   ├─> Lookup mỗi hash trong database
    │   ├─> Calculate offsets (db_time - sample_time)
    │   ├─> Group matches by song_name
    │   └─> Time coherency analysis
    │       └─> Find song với most frequent offset
    │
    └─> [FastAPI] Return recognition result
```

**Time Complexity:**
- Fingerprint generation: O(n log n + p²)
- Database lookup: O(q × m) với q = query fingerprints, m = avg matches
- Time coherency: O(s × o) với s = số songs, o = số offsets

**Total:** ~O(n log n + q × m) cho recognition

---

### Workflow 3: Delete Song

```
[Client] DELETE /songs/{song_name}
    │
    ├─> [FastAPI] Extract song_name from path
    │
    ├─> [InMemoryDB] delete_song()
    │   ├─> Check song exists
    │   ├─> Iterate qua tất cả hash entries
    │   ├─> Filter out entries có song_name
    │   ├─> Remove empty hash entries
    │   └─> Remove từ song_list
    │
    └─> [FastAPI] Return deletion result
```

**Time Complexity:** O(h) với h = số hash entries

---

## 🛠️ Công Cụ và Scripts

### 1. batch_upload_songs.py

**Purpose:** Upload nhiều bài hát từ thư mục

**Usage:**
```bash
python3 batch_upload_songs.py <directory> [--mapping <mapping_file>] [--url <api_url>]
```

**Features:**
- Tự động tìm file audio (.wav, .mp3, .m4a, .flac)
- Progress tracking
- Error handling per file
- Summary report
- Save results to JSON

**Example:**
```bash
python3 batch_upload_songs.py ~/Music/songs --mapping song_mapping.json
```

---

### 2. create_song_mapping.py

**Purpose:** Tạo file mapping từ tên file

**Usage:**
```bash
python3 create_song_mapping.py <directory> [-o <output_file>]
```

**Features:**
- Extract song name từ filename
- Parse "Artist - Song" format
- Generate JSON mapping file

**Example:**
```bash
python3 create_song_mapping.py ~/Music/songs
# Tạo file: ~/Music/songs/song_mapping.json
```

---

### 3. test_api.py

**Purpose:** Test tất cả API endpoints

**Usage:**
```bash
python3 test_data/test_api.py
```

**Tests:**
- Server connection
- Learn songs
- Recognize songs
- Stats endpoint

---

### 4. test_upload_wav.py

**Purpose:** Test upload WAV files

**Usage:**
```bash
python3 test_data/test_upload_wav.py
```

---

### 5. test_delete_songs.py

**Purpose:** Test delete APIs

**Usage:**
```bash
python3 test_data/test_delete_songs.py
```

---

## ⚙️ Deployment và Configuration

### 1. Installation

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# hoặc: venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify installation
python3 -c "import fastapi, scipy, numpy, soundfile; print('OK')"
```

### 2. Running Server

#### Development Mode
```bash
cd backend
source venv/bin/activate
python3 main.py
```

#### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Configuration

#### CORS Settings
```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Server Settings
```python
# main.py
uvicorn.run(
    "main:app",
    host="0.0.0.0",      # Listen on all interfaces
    port=8000,            # Port number
    reload=True           # Auto-reload (dev only)
)
```

### 4. Environment Variables

Có thể thêm file `.env`:
```bash
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 5. Logging

Thêm logging (optional):
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## 📊 Performance và Scalability

### Current Limitations

1. **In-Memory Storage:**
   - Mất dữ liệu khi restart
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

4. **Load Balancing:**
   - Multiple workers với uvicorn
   - Redis cho shared state

---

## 🔒 Security Considerations

### Current State
- ⚠️ CORS: Allow all origins (dev only)
- ⚠️ No authentication
- ⚠️ No rate limiting
- ⚠️ No file size limits

### Recommendations

1. **CORS:**
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

2. **Authentication:**
   - Add API keys hoặc JWT tokens
   - Rate limiting per user

3. **File Validation:**
   - Max file size (e.g., 50MB)
   - File type validation
   - Virus scanning (optional)

4. **Input Sanitization:**
   - Validate song names
   - Prevent path traversal

---

## 📈 Monitoring và Debugging

### Health Check

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": {
            "songs": db.get_song_count(),
            "fingerprints": db.get_fingerprint_count()
        }
    }
```

### Error Handling

```python
try:
    # Process audio
except FileNotFoundError:
    raise HTTPException(404, "File not found")
except Exception as e:
    logger.error(f"Error: {e}")
    raise HTTPException(500, f"Internal error: {str(e)}")
```

---

## 📚 Tài Liệu Tham Khảo

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Scipy Signal Processing](https://docs.scipy.org/doc/scipy/reference/signal.html)
- [Audio Fingerprinting Algorithm](https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf)
- [PROJECT_SPECS.md](../PROẸCT_SPECS.md)

---

## 🎯 Kết Luận

Backend được thiết kế với:
- ✅ Kiến trúc rõ ràng và modular
- ✅ API RESTful đầy đủ
- ✅ DSP processing chính xác
- ✅ Database hiệu quả
- ✅ Tools và scripts hỗ trợ

Sẵn sàng cho development và có thể mở rộng cho production.

