# Test Data for Music Recognition

This directory contains scripts and data for testing the music recognition system.

## Setup Test Data

### Option 1: Generate Synthetic Audio (Recommended for quick testing)

```bash
cd backend/test_data
python create_test_audio.py
```

This will create 3 synthetic WAV files:
- `test_song_1.wav` - Simple tone sequence
- `test_song_2.wav` - Chord progression
- `test_song_3.wav` - Mixed frequencies

### Option 2: Download Sample Audio

```bash
cd backend/test_data
python download_test_songs.py
```

This will attempt to download sample audio files from the internet.

### Option 3: Add Your Own Audio Files

Place your own audio files (WAV or MP3) in this directory. They will be automatically detected by the test script.

## Testing the API

1. Start the backend server:
```bash
cd backend
python main.py
```

2. In another terminal, run the test script:
```bash
cd backend/test_data
python test_api.py
```

The test script will:
- Check server connection
- Learn all songs in the test_data directory
- Test recognition with the same files
- Test recognition with partial samples

## File Structure

```
test_data/
├── README.md (this file)
├── create_test_audio.py (generate synthetic audio)
├── download_test_songs.py (download sample audio)
├── test_api.py (test the API)
└── *.wav, *.mp3 (audio files for testing)
```

