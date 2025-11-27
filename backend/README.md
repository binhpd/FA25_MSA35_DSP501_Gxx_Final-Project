# Music Recognition Backend API

Backend server for Shazam-like music recognition using audio fingerprinting.

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## API Endpoints

### POST /learn
Add a song to the database.

**Request:**
- `file`: Audio file (WAV/MP3)
- `song_name`: Name/ID of the song

**Response:**
```json
{
  "success": true,
  "song_name": "Song Name",
  "fingerprints_count": 1234,
  "message": "Song added successfully"
}
```

### POST /recognize
Recognize a song from an audio sample.

**Request:**
- `file`: Audio file (WAV/MP3) - typically 5-10 seconds

**Response:**
```json
{
  "success": true,
  "song": "Song Name",
  "confidence": 85.5,
  "matches": 42,
  "message": "Recognized as 'Song Name' with 85.50% confidence"
}
```

### GET /stats
Get database statistics.

**Response:**
```json
{
  "song_count": 10,
  "fingerprint_count": 12345,
  "songs": ["Song 1", "Song 2", ...]
}
```

### GET /songs
List all songs in the database.

## Testing

Use the scripts in the `test_data/` directory to add test songs and test recognition.

