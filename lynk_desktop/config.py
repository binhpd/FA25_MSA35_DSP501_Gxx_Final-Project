"""
Configuration file for Lynk Desktop
"""

# Server configuration
SERVER_HOST = "localhost"
SERVER_PORT = 8000
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

# Recording configuration
RECORDING_DURATION = 10  # seconds
SAMPLE_RATE = 44100  # Hz
CHANNELS = 1  # Mono
CHUNK_SIZE = 1024

# UI configuration
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700
PRIMARY_COLOR = "#673AB7"  # Deep purple
SUCCESS_COLOR = "#4CAF50"   # Green
ERROR_COLOR = "#F44336"     # Red
ACCENT_COLOR = "#FF9800"    # Orange
BG_COLOR = "#f5f5f5"



