"""
Script to generate synthetic test audio files
Creates simple tones that can be used for testing
"""

import numpy as np
import soundfile as sf
from pathlib import Path
import os

# Create test_data directory
test_data_dir = Path(__file__).parent
test_data_dir.mkdir(exist_ok=True)


def generate_tone(frequency: float, duration: float, sample_rate: int = 22050) -> np.ndarray:
    """
    Generate a simple sine wave tone
    
    Args:
        frequency: Frequency in Hz
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        
    Returns:
        Audio signal as numpy array
    """
    t = np.linspace(0, duration, int(sample_rate * duration))
    signal = np.sin(2 * np.pi * frequency * t)
    return signal


def generate_chord(frequencies: list, duration: float, sample_rate: int = 22050) -> np.ndarray:
    """
    Generate a chord from multiple frequencies
    
    Args:
        frequencies: List of frequencies in Hz
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        
    Returns:
        Audio signal as numpy array
    """
    t = np.linspace(0, duration, int(sample_rate * duration))
    signal = np.zeros_like(t)
    
    for freq in frequencies:
        signal += np.sin(2 * np.pi * freq * t)
    
    # Normalize
    signal = signal / len(frequencies)
    return signal


def create_test_songs():
    """Create synthetic test audio files"""
    print("=" * 60)
    print("Creating Test Audio Files")
    print("=" * 60)
    
    # Test Song 1: Simple tone sequence
    print("\nCreating test_song_1.wav...")
    tone1 = generate_tone(440, 2.0)  # A4 note
    tone2 = generate_tone(523.25, 2.0)  # C5 note
    tone3 = generate_tone(659.25, 2.0)  # E5 note
    song1 = np.concatenate([tone1, tone2, tone3])
    sf.write(test_data_dir / "test_song_1.wav", song1, 22050)
    print("✓ Created test_song_1.wav")
    
    # Test Song 2: Chord progression
    print("\nCreating test_song_2.wav...")
    chord1 = generate_chord([261.63, 329.63, 392.00], 2.0)  # C major
    chord2 = generate_chord([293.66, 369.99, 440.00], 2.0)  # D major
    chord3 = generate_chord([329.63, 415.30, 493.88], 2.0)  # E major
    song2 = np.concatenate([chord1, chord2, chord3])
    sf.write(test_data_dir / "test_song_2.wav", song2, 22050)
    print("✓ Created test_song_2.wav")
    
    # Test Song 3: Mixed frequencies
    print("\nCreating test_song_3.wav...")
    mixed = generate_chord([220, 330, 440, 550], 6.0)
    sf.write(test_data_dir / "test_song_3.wav", mixed, 22050)
    print("✓ Created test_song_3.wav")
    
    print("\n" + "=" * 60)
    print("✓ All test files created successfully!")
    print(f"Test data directory: {test_data_dir}")
    print("=" * 60)


if __name__ == "__main__":
    create_test_songs()

