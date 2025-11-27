"""
FastAPI Server for Music Recognition System
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from app.core.dsp_engine import AudioFingerprinter
from app.core.database import PersistentDB
from app.api.routes import router, init_routes

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Music Recognition API",
    description="Shazam-like music recognition using audio fingerprinting",
    version="1.0.0"
)

# Enable CORS for Flutter mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Flutter app's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
fingerprinter = AudioFingerprinter()
# Use persistent database (SQLite) - data will be saved to music_recognition.db
db = PersistentDB(db_path="music_recognition.db")

# Log database status on startup
song_count = db.get_song_count()
fingerprint_count = db.get_fingerprint_count()
logger.info(f"📊 Database loaded: {song_count} songs, {fingerprint_count} fingerprints")

# Initialize routes with dependencies
init_routes(fingerprinter, db)

# Include router
app.include_router(router)


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload for development
    )


