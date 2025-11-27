"""
FastAPI Server for Music Recognition System
Provides endpoints for learning and recognizing songs
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import tempfile
from typing import Optional

from dsp_engine import AudioFingerprinter
from database import InMemoryDB

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
db = InMemoryDB()


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Music Recognition API",
        "version": "1.0.0",
        "endpoints": {
            "POST /learn": "Add a song to the database",
            "POST /recognize": "Recognize a song from audio sample",
            "GET /stats": "Get database statistics",
            "GET /songs": "List all songs in database"
        }
    }


@app.post("/learn")
async def learn_song(
    file: UploadFile = File(...),
    song_name: str = Form(...)
):
    """
    Learn a new song by processing its audio file
    
    Args:
        file: Audio file (WAV/MP3)
        song_name: Name/ID of the song
        
    Returns:
        JSON response with success status and fingerprint count
    """
    # Validate file type
    if not file.content_type or not any(
        file.content_type.startswith(f"audio/{ext}") 
        for ext in ["wav", "mp3", "mpeg", "x-mpeg", "mpeg3", "x-mpeg3"]
    ):
        # Also accept if filename has audio extension
        if not any(file.filename.lower().endswith(ext) for ext in [".wav", ".mp3", ".m4a", ".flac"]):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an audio file (WAV, MP3, etc.)"
            )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
        try:
            # Write uploaded content to temp file
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
            
            # Generate fingerprints
            fingerprints = fingerprinter.process_file(tmp_file_path)
            
            if not fingerprints:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to generate fingerprints. Please check the audio file."
                )
            
            # Add to database
            count = db.add_song(song_name, fingerprints)
            
            return JSONResponse({
                "success": True,
                "song_name": song_name,
                "fingerprints_count": count,
                "message": f"Song '{song_name}' added successfully with {count} fingerprints"
            })
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing audio file: {str(e)}"
            )
        finally:
            # Clean up temp file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)


@app.post("/recognize")
async def recognize_song(
    file: UploadFile = File(...)
):
    """
    Recognize a song from an audio sample
    
    Args:
        file: Audio file (WAV/MP3) - typically a short recording (5-10 seconds)
        
    Returns:
        JSON response with recognized song name and confidence score
    """
    # Validate file type
    if not file.content_type or not any(
        file.content_type.startswith(f"audio/{ext}") 
        for ext in ["wav", "mp3", "mpeg", "x-mpeg", "mpeg3", "x-mpeg3"]
    ):
        if not any(file.filename.lower().endswith(ext) for ext in [".wav", ".mp3", ".m4a", ".flac"]):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an audio file (WAV, MP3, etc.)"
            )
    
    # Check if database is empty
    if db.get_song_count() == 0:
        return JSONResponse({
            "success": False,
            "song": None,
            "confidence": 0.0,
            "matches": 0,
            "message": "Database is empty. Please add songs first using /learn endpoint."
        })
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
        try:
            # Write uploaded content to temp file
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
            
            # Generate fingerprints from sample
            query_fingerprints = fingerprinter.process_file(tmp_file_path)
            
            if not query_fingerprints:
                return JSONResponse({
                    "success": False,
                    "song": None,
                    "confidence": 0.0,
                    "matches": 0,
                    "message": "Failed to generate fingerprints from audio sample."
                })
            
            # Query database
            result = db.query(query_fingerprints, min_matches=5)
            
            if result:
                song_name, match_count, confidence = result
                return JSONResponse({
                    "success": True,
                    "song": song_name,
                    "confidence": round(confidence * 100, 2),  # Convert to percentage
                    "matches": match_count,
                    "message": f"Recognized as '{song_name}' with {confidence*100:.2f}% confidence"
                })
            else:
                return JSONResponse({
                    "success": False,
                    "song": None,
                    "confidence": 0.0,
                    "matches": 0,
                    "message": "No matching song found in database."
                })
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing audio file: {str(e)}"
            )
        finally:
            # Clean up temp file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)


@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    return {
        "song_count": db.get_song_count(),
        "fingerprint_count": db.get_fingerprint_count(),
        "songs": db.list_songs()
    }


@app.get("/songs")
async def list_songs():
    """List all songs in the database"""
    return {
        "songs": db.list_songs(),
        "count": db.get_song_count()
    }


@app.delete("/songs/{song_name}")
async def delete_song(song_name: str):
    """
    Delete a specific song from the database
    
    Args:
        song_name: Name/ID of the song to delete
        
    Returns:
        JSON response with deletion status
    """
    success, deleted_count = db.delete_song(song_name)
    
    if success:
        return JSONResponse({
            "success": True,
            "song_name": song_name,
            "deleted_fingerprints": deleted_count,
            "message": f"Song '{song_name}' deleted successfully. Removed {deleted_count} fingerprints."
        })
    else:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "song_name": song_name,
                "deleted_fingerprints": 0,
                "message": f"Song '{song_name}' not found in database."
            }
        )


@app.delete("/songs")
async def clear_all_songs():
    """
    Delete all songs from the database (clear entire database)
    
    Returns:
        JSON response with deletion status
    """
    song_count = db.get_song_count()
    fingerprint_count = db.get_fingerprint_count()
    
    db.clear_all()
    
    return JSONResponse({
        "success": True,
        "deleted_songs": song_count,
        "deleted_fingerprints": fingerprint_count,
        "message": f"Database cleared. Deleted {song_count} songs and {fingerprint_count} fingerprints."
    })


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload for development
    )

