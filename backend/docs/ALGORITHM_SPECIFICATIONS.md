# Thông Số Giải Thuật Nhận Diện Bài Hát

## 📋 Tổng Quan

Dự án sử dụng thuật toán **Audio Fingerprinting** dựa trên phương pháp của **Avery Wang** (Shazam) với các thông số kỹ thuật sau:

---

## 🎵 1. Thông Số Tiền Xử Lý Audio (Pre-processing)

### Sample Rate
- **Giá trị:** `22050 Hz`
- **Lý do:** 
  - Nyquist frequency = 11025 Hz, đủ để capture thông tin âm nhạc quan trọng
  - Giảm \kích thước dữ liệu và thời gian xử lý so với 44.1 kHz
  - Tối ưu cho voice và music recognition

### Channels
- **Giá trị:** `Mono (1 channel)`
- **Phương pháp:** Average channels nếu input là stereo
- **Công thức:** `audio_mono = np.mean(audio_stereo, axis=1)`

### Resampling
- **Phương pháp:** `scipy.signal.resample`
- **Tự động:** Resample về 22050 Hz nếu input khác sample rate

---

## 📊 2. Thông Số Spectrogram (STFT)

### Window Function
- **Loại:** `Hanning Window`
- **Công thức:** `window = np.hanning(n_fft)`

### N_FFT (Window Size)
- **Giá trị:** `4096 samples`
- **Lý do:**
  - Độ phân giải tần số: ~5.38 Hz per bin
  - Công thức: `frequency_resolution = sample_rate / n_fft = 22050 / 4096 ≈ 5.38 Hz`
  - Cân bằng giữa độ phân giải và thời gian xử lý

### Hop Length
- **Giá trị:** `1024 samples`
- **Overlap:** `75%` (vì `noverlap = n_fft - hop_length = 4096 - 1024 = 3072`)
- **Lý do:**
  - Overlap cao giúp capture tốt hơn các thay đổi trong tín hiệu
  - Giảm aliasing trong time domain

### Time Resolution
- **Time per bin:** `1024 / 22050 ≈ 0.0464 seconds` (~46.4 ms)
- **Công thức:** `time_resolution = hop_length / sample_rate`

### Frequency Resolution
- **Frequency bins:** `2049 bins` (one-sided)
- **Frequency range:** `0 - 11025 Hz` (Nyquist frequency)
- **Frequency per bin:** `~5.38 Hz`

---

## 🔍 3. Thông Số Peak Detection

### Neighborhood Size
- **Giá trị:** `20 × 20 bins`
- **Phương pháp:** 2D Local Maximum Filter
- **Lý do:**
  - Đủ lớn để loại bỏ noise
  - Đủ nhỏ để capture các peaks quan trọng

### Threshold
- **Phương pháp:** Percentile-based
- **Giá trị:** `75th percentile` của peaks
- **Công thức:** `threshold = np.percentile(spectrogram[peaks_mask], 75)`
- **Lý do:**
  - Tự động adapt với từng audio file
  - Loại bỏ ~75% peaks yếu (noise)
  - Giữ lại ~25% peaks mạnh nhất

### Peak Selection Criteria
1. Point phải là local maximum trong neighborhood 20×20
2. Magnitude > 0
3. Magnitude >= threshold (75th percentile)

---

## 🔑 4. Thông Số Fingerprint Generation (Combinatorial Hashing)

### Target Zone (Time Window)
- **Minimum time:** `1 second` sau anchor point
- **Maximum time:** `5 seconds` sau anchor point
- **Time range:** `1 - 5 seconds`

### Target Zone (Bins)
- **Minimum bins:** `target_zone_bin_min = int(1 * 22050 / 1024) = 21 bins`
- **Maximum bins:** `target_zone_bin_max = int(5 * 22050 / 1024) = 107 bins`
- **Công thức:** `bins = time_seconds * sample_rate / hop_length`

### Hash Format
- **Structure:** `(f1, f2, dt)`
  - `f1`: Tần số của anchor point (Hz, integer)
  - `f2`: Tần số của target point (Hz, integer)
  - `dt`: Time delta giữa anchor và target (bins, integer)

### Hash Storage
- **Format:** `(hash_token, absolute_time)`
  - `hash_token`: `(f1, f2, dt)` tuple
  - `absolute_time`: Thời gian tuyệt đối của anchor point (seconds, float)

### Number of Fingerprints
- **Phụ thuộc vào:**
  - Số lượng peaks trong spectrogram
  - Số lượng target peaks trong target zone của mỗi anchor
- **Công thức:** `N_fingerprints ≈ N_peaks × N_targets_per_anchor`
- **Ví dụ:** Bài hát 3 phút có thể tạo ~6,000-10,000 fingerprints

---

## 🎯 5. Thông Số Matching (Query & Recognition)

### Minimum Matches
- **Giá trị mặc định:** `min_matches = 5`
- **Lý do:**
  - Đủ để phân biệt match thật với collision ngẫu nhiên
  - Cân bằng giữa độ chính xác và khả năng nhận diện

### Time Coherency Analysis
- **Phương pháp:** Histogram analysis
- **Công thức:**
  1. Với mỗi match: `offset = db_time - sample_time`
  2. Nhóm matches theo `song_name`
  3. Đếm số lần xuất hiện của mỗi `offset`
  4. Chọn song có `offset` xuất hiện nhiều nhất

### Confidence Score
- **Công thức:** `confidence = best_match_count / total_query_fingerprints`
- **Range:** `0.0 - 1.0` (0% - 100%)
- **Ví dụ:** 
  - 42 matches từ 100 query fingerprints → confidence = 0.42 (42%)

### Matching Algorithm
```
1. Query: Gửi sample fingerprints
2. Lookup: Tìm tất cả matches trong database
3. Calculate offsets: offset = db_time - sample_time
4. Group by song: Nhóm matches theo song_name
5. Histogram: Đếm số lần xuất hiện của mỗi offset
6. Best match: Song có offset xuất hiện nhiều nhất
7. Filter: Chỉ trả về nếu match_count >= min_matches
```

---

## 📈 6. Thông Số Performance

### Time Complexity

#### Pre-processing
- **Audio loading:** `O(n)` với n = số samples
- **Resampling:** `O(n)` với n = số samples
- **Total:** `O(n)`

#### Spectrogram Generation
- **STFT:** `O(n log n)` với n = số samples
- **Time:** ~0.1-1 giây cho bài hát 3 phút

#### Peak Detection
- **Maximum filter:** `O(f × t × k²)` 
  - f = số frequency bins (~2049)
  - t = số time bins (~(duration × sample_rate / hop_length))
  - k = neighborhood size (20)
- **Time:** ~0.1-0.5 giây

#### Fingerprint Generation
- **Combinatorial hashing:** `O(p²)` với p = số peaks
- **Time:** ~0.5-2 giây cho bài hát 3 phút

#### Database Query
- **Hash lookup:** `O(q × m)`
  - q = số query fingerprints
  - m = số matches trung bình per hash
- **Time coherency:** `O(s × o)`
  - s = số songs
  - o = số offsets per song
- **Total:** ~0.01-0.1 giây

### Space Complexity

#### Memory
- **Spectrogram:** `O(f × t)` với f=2049, t=time_bins
- **Peaks:** `O(p)` với p = số peaks
- **Fingerprints:** `O(p²)` trong worst case

#### Database Storage
- **Per fingerprint:** ~20-30 bytes (hash_token + song_id + time)
- **Per song (3 phút):** ~6,000 fingerprints × 25 bytes ≈ 150 KB
- **100 songs:** ~15 MB

---

## 🔢 7. Thông Số Kỹ Thuật Chi Tiết

### Audio Processing
| Thông số | Giá trị | Đơn vị |
|----------|---------|--------|
| Sample Rate | 22050 | Hz |
| Channels | 1 (Mono) | - |
| Bit Depth | 16-bit (từ file) | bits |
| Window Function | Hanning | - |
| N_FFT | 4096 | samples |
| Hop Length | 1024 | samples |
| Overlap | 75% | - |
| Frequency Resolution | ~5.38 | Hz/bin |
| Time Resolution | ~46.4 | ms/bin |

### Peak Detection
| Thông số | Giá trị | Đơn vị |
|----------|---------|--------|
| Neighborhood Size | 20 × 20 | bins |
| Threshold Method | Percentile | - |
| Threshold Value | 75th percentile | - |
| Peak Selection | Local Maximum | - |

### Fingerprinting
| Thông số | Giá trị | Đơn vị |
|----------|---------|--------|
| Target Zone Min | 1 | seconds |
| Target Zone Max | 5 | seconds |
| Target Zone Min (bins) | 21 | bins |
| Target Zone Max (bins) | 107 | bins |
| Hash Format | (f1, f2, dt) | - |
| f1, f2 Range | 0 - 11025 | Hz |
| dt Range | 21 - 107 | bins |

### Matching
| Thông số | Giá trị | Đơn vị |
|----------|---------|--------|
| Min Matches | 5 | matches |
| Confidence Range | 0.0 - 1.0 | - |
| Time Coherency | Histogram | - |

---

## 📐 8. Công Thức Toán Học

### Frequency Resolution
```
frequency_resolution = sample_rate / n_fft
                     = 22050 / 4096
                     ≈ 5.38 Hz/bin
```

### Time Resolution
```
time_resolution = hop_length / sample_rate
                = 1024 / 22050
                ≈ 0.0464 seconds/bin
                ≈ 46.4 ms/bin
```

### Number of Frequency Bins
```
freq_bins = (n_fft / 2) + 1
          = (4096 / 2) + 1
          = 2049 bins
```

### Number of Time Bins
```
time_bins = (audio_length - n_fft) / hop_length + 1
          ≈ audio_length / hop_length (for long audio)
```

### Target Zone Bins
```
target_zone_bin_min = int(time_min * sample_rate / hop_length)
                     = int(1 * 22050 / 1024)
                     = 21 bins

target_zone_bin_max = int(time_max * sample_rate / hop_length)
                     = int(5 * 22050 / 1024)
                     = 107 bins
```

### Confidence Score
```
confidence = best_match_count / total_query_fingerprints
```

---

## 🎯 9. Đặc Điểm Thuật Toán

### Ưu Điểm
1. **Robust:** Chống lại noise và distortion
2. **Fast:** Query nhanh với hash lookup
3. **Scalable:** Có thể scale với nhiều bài hát
4. **Accurate:** Time coherency đảm bảo độ chính xác cao

### Giới Hạn
1. **Short samples:** Cần ít nhất 5-10 giây để nhận diện
2. **Noise:** Quá nhiều noise có thể giảm accuracy
3. **Similar songs:** Có thể nhầm lẫn với bài hát tương tự

### Độ Chính Xác
- **Ideal conditions:** > 90% với sample 10 giây
- **Normal conditions:** 70-90% với sample 5-10 giây
- **Noisy conditions:** 50-70% với nhiều noise

---

## 📚 10. Tài Liệu Tham Khảo

- **Avery Wang's Algorithm:** [An Industrial-Strength Audio Search Algorithm](https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf)
- **STFT:** Short-Time Fourier Transform
- **Spectrogram:** Time-frequency representation
- **Combinatorial Hashing:** Pairing peaks for unique identification

---

## 🔧 11. Cấu Hình Hiện Tại

Tất cả thông số trên được định nghĩa trong `AudioFingerprinter` class:

```python
AudioFingerprinter(
    sample_rate=22050,           # Hz
    n_fft=4096,                  # samples
    hop_length=1024,             # samples
    peak_neighborhood_size=20,    # bins
    target_zone_t_min=1,         # seconds
    target_zone_t_max=5          # seconds
)
```

Các thông số này có thể được điều chỉnh trong code nếu cần tối ưu cho use case cụ thể.



