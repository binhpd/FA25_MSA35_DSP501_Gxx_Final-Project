"""
API Routes for Music Recognition System
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import tempfile
import logging

from app.core.dsp_engine import AudioFingerprinter
from app.core.database import PersistentDB

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Initialize components (will be injected from main)
fingerprinter: AudioFingerprinter = None
db: PersistentDB = None


def init_routes(fingerprinter_instance: AudioFingerprinter, db_instance: PersistentDB):
    """Initialize routes with dependencies"""
    global fingerprinter, db
    fingerprinter = fingerprinter_instance
    db = db_instance


@router.get("/")
async def root():
    """Root endpoint - API information"""
    return {
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


@router.post("/learn")
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
    tmp_file_path = None
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
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)


@router.post("/recognize")
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
    logger.info("=" * 60)
    logger.info("🎵 [RECOGNIZE] New recognition request received")
    logger.info(f"📁 [RECOGNIZE] Filename: {file.filename}")
    logger.info(f"📋 [RECOGNIZE] Content-Type: {file.content_type}")
    logger.info(f"📊 [RECOGNIZE] Content-Length: {file.size if hasattr(file, 'size') else 'unknown'}")
    
    # Validate file type
    if not file.content_type or not any(
        file.content_type.startswith(f"audio/{ext}") 
        for ext in ["wav", "mp3", "mpeg", "x-mpeg", "mpeg3", "x-mpeg3"]
    ):
        if not any(file.filename.lower().endswith(ext) for ext in [".wav", ".mp3", ".m4a", ".flac"]):
            logger.warning(f"❌ [RECOGNIZE] Invalid file type: {file.content_type}, filename: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an audio file (WAV, MP3, etc.)"
            )
    
    logger.info(f"✅ [RECOGNIZE] File type validated: {file.filename}")
    
    # Check if database is empty
    song_count = db.get_song_count()
    logger.info(f"📚 [RECOGNIZE] Database has {song_count} songs")
    
    if song_count == 0:
        logger.warning("⚠️ [RECOGNIZE] Database is empty")
        return JSONResponse({
            "success": False,
            "song": None,
            "confidence": 0.0,
            "matches": 0,
            "message": "Database is empty. Please add songs first using /learn endpoint."
        })
    
    # Save uploaded file temporarily
    tmp_file_path = None
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
        try:
            logger.info(f"💾 [RECOGNIZE] Saving uploaded file to: {tmp_file.name}")
            
            # Write uploaded content to temp file
            content = await file.read()
            file_size = len(content)
            logger.info(f"📦 [RECOGNIZE] File size: {file_size} bytes ({file_size / 1024:.2f} KB)")
            
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
            logger.info(f"✅ [RECOGNIZE] File saved successfully")
            
            # Generate fingerprints from sample
            logger.info("🔍 [RECOGNIZE] Starting fingerprint generation...")
            try:
                query_fingerprints = fingerprinter.process_file(tmp_file_path)
                fingerprint_count = len(query_fingerprints) if query_fingerprints else 0
                logger.info(f"✅ [RECOGNIZE] Generated {fingerprint_count} fingerprints")
            except Exception as fp_error:
                logger.error(f"❌ [RECOGNIZE] Fingerprint generation failed: {str(fp_error)}", exc_info=True)
                raise
            
            if not query_fingerprints:
                logger.warning("⚠️ [RECOGNIZE] No fingerprints generated from audio sample")
                return JSONResponse({
                    "success": False,
                    "song": None,
                    "confidence": 0.0,
                    "matches": 0,
                    "message": "Failed to generate fingerprints from audio sample."
                })
            
            # Query database
            logger.info(f"🔎 [RECOGNIZE] Querying database with {fingerprint_count} fingerprints (min_matches=5)...")
            try:
                result = db.query(query_fingerprints, min_matches=5)
            except Exception as query_error:
                logger.error(f"❌ [RECOGNIZE] Database query failed: {str(query_error)}", exc_info=True)
                raise
            
            if result:
                song_name, match_count, confidence = result
                logger.info(f"🎉 [RECOGNIZE] Match found! Song: {song_name}, Matches: {match_count}, Confidence: {confidence*100:.2f}%")
                return JSONResponse({
                    "success": True,
                    "song": song_name,
                    "confidence": round(confidence * 100, 2),  # Convert to percentage
                    "matches": match_count,
                    "message": f"Recognized as '{song_name}' with {confidence*100:.2f}% confidence"
                })
            else:
                logger.info("❌ [RECOGNIZE] No matching song found in database")
                return JSONResponse({
                    "success": False,
                    "song": None,
                    "confidence": 0.0,
                    "matches": 0,
                    "message": "No matching song found in database."
                })
                
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.error(f"❌ [RECOGNIZE] Unexpected error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error processing audio file: {str(e)}"
            )
        finally:
            # Clean up temp file
            if tmp_file_path and os.path.exists(tmp_file_path):
                try:
                    os.unlink(tmp_file_path)
                    logger.info(f"🗑️ [RECOGNIZE] Cleaned up temp file: {tmp_file_path}")
                except Exception as cleanup_error:
                    logger.warning(f"⚠️ [RECOGNIZE] Failed to cleanup temp file: {cleanup_error}")


@router.get("/stats")
async def get_stats():
    """Get database statistics"""
    return {
        "song_count": db.get_song_count(),
        "fingerprint_count": db.get_fingerprint_count(),
        "songs": db.list_songs()
    }


@router.get("/songs")
async def list_songs():
    """List all songs in the database"""
    return {
        "songs": db.list_songs(),
        "count": db.get_song_count()
    }


@router.delete("/songs/{song_name}")
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


@router.delete("/songs")
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


