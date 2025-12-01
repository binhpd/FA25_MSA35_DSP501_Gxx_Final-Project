from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import tempfile

from app.core.dsp_engine import AudioFingerprinter
from app.core.database import PersistentDB

router = APIRouter()

fingerprinter: AudioFingerprinter = None
db: PersistentDB = None


def init_routes(fingerprinter_instance: AudioFingerprinter, db_instance: PersistentDB):
    global fingerprinter, db
    fingerprinter = fingerprinter_instance
    db = db_instance


@router.get("/")
async def root():
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
    if not file.content_type or not any(
        file.content_type.startswith(f"audio/{ext}") 
        for ext in ["wav", "mp3", "mpeg", "x-mpeg", "mpeg3", "x-mpeg3"]
    ):
        if not any(file.filename.lower().endswith(ext) for ext in [".wav", ".mp3", ".m4a", ".flac"]):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an audio file (WAV, MP3, etc.)"
            )
    
    tmp_file_path = None
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
        try:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
            
            fingerprints = fingerprinter.process_file(tmp_file_path)
            
            if not fingerprints:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to generate fingerprints. Please check the audio file."
                )
            
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
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)


@router.post("/recognize")
async def recognize_song(
    file: UploadFile = File(...)
):
    if not file.content_type or not any(
        file.content_type.startswith(f"audio/{ext}") 
        for ext in ["wav", "mp3", "mpeg", "x-mpeg", "mpeg3", "x-mpeg3"]
    ):
        if not any(file.filename.lower().endswith(ext) for ext in [".wav", ".mp3", ".m4a", ".flac"]):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an audio file (WAV, MP3, etc.)"
            )
    
    song_count = db.get_song_count()
    
    if song_count == 0:
        return JSONResponse({
            "success": False,
            "song": None,
            "confidence": 0.0,
            "matches": 0,
            "message": "Database is empty. Please add songs first using /learn endpoint."
        })
    
    tmp_file_path = None
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
        try:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
            
            try:
                query_fingerprints = fingerprinter.process_file(tmp_file_path)
            except Exception as fp_error:
                raise
            
            if not query_fingerprints:
                return JSONResponse({
                    "success": False,
                    "song": None,
                    "confidence": 0.0,
                    "matches": 0,
                    "message": "Failed to generate fingerprints from audio sample."
                })
            
            try:
                result = db.query(query_fingerprints, min_matches=5)
            except Exception as query_error:
                raise
            
            if result:
                song_name, match_count, confidence = result
                return JSONResponse({
                    "success": True,
                    "song": song_name,
                    "confidence": round(confidence * 100, 2),
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
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing audio file: {str(e)}"
            )
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                try:
                    os.unlink(tmp_file_path)
                except Exception as cleanup_error:
                    pass


@router.get("/stats")
async def get_stats():
    return {
        "song_count": db.get_song_count(),
        "fingerprint_count": db.get_fingerprint_count(),
        "songs": db.list_songs()
    }


@router.get("/songs")
async def list_songs():
    return {
        "songs": db.list_songs(),
        "count": db.get_song_count()
    }


@router.delete("/songs/{song_name}")
async def delete_song(song_name: str):
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
    song_count = db.get_song_count()
    fingerprint_count = db.get_fingerprint_count()
    
    db.clear_all()
    
    return JSONResponse({
        "success": True,
        "deleted_songs": song_count,
        "deleted_fingerprints": fingerprint_count,
        "message": f"Database cleared. Deleted {song_count} songs and {fingerprint_count} fingerprints."
    })
