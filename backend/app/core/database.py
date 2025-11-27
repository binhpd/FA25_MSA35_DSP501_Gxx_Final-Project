"""
Persistent Database for Audio Fingerprints using SQLite
Stores and queries fingerprints for music recognition
"""

import sqlite3
import os
from collections import Counter, defaultdict
from typing import List, Tuple, Optional
import logging

# Setup logging
logger = logging.getLogger(__name__)


class PersistentDB:
    """
    Persistent database for storing and querying audio fingerprints using SQLite
    """
    
    def __init__(self, db_path: str = "music_recognition.db"):
        """
        Initialize the database
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._init_database()
        logger.info(f"✅ Database initialized at: {os.path.abspath(self.db_path)}")
    
    def _get_connection(self):
        """Get database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def _init_database(self):
        """Initialize database schema"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create songs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create fingerprints table
        # Hash token is stored as: f1|f2|dt (pipe-separated string for simplicity)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fingerprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash_token TEXT NOT NULL,
                song_id INTEGER NOT NULL,
                absolute_time REAL NOT NULL,
                FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_hash_token ON fingerprints(hash_token)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_song_id ON fingerprints(song_id)
        """)
        
        conn.commit()
        logger.info("✅ Database schema initialized")
    
    def _hash_to_string(self, hash_token: Tuple) -> str:
        """Convert hash tuple to string for storage"""
        return f"{hash_token[0]}|{hash_token[1]}|{hash_token[2]}"
    
    def _string_to_hash(self, hash_str: str) -> Tuple:
        """Convert hash string to tuple"""
        parts = hash_str.split("|")
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    
    def add_song(self, song_name: str, fingerprints: List[Tuple]) -> int:
        """
        Add a song and its fingerprints to the database
        
        Args:
            song_name: Name/ID of the song
            fingerprints: List of ((hash_token), absolute_time) tuples
            
        Returns:
            Number of fingerprints added
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Insert or get song
            cursor.execute("""
                INSERT OR IGNORE INTO songs (name) VALUES (?)
            """, (song_name,))
            
            # Get song_id
            cursor.execute("SELECT id FROM songs WHERE name = ?", (song_name,))
            song_row = cursor.fetchone()
            if song_row is None:
                raise ValueError(f"Failed to get song_id for {song_name}")
            song_id = song_row[0]
            
            # Insert fingerprints
            count = 0
            fingerprint_data = []
            for hash_token, absolute_time in fingerprints:
                hash_str = self._hash_to_string(hash_token)
                fingerprint_data.append((hash_str, song_id, absolute_time))
                count += 1
            
            # Batch insert for better performance
            cursor.executemany("""
                INSERT INTO fingerprints (hash_token, song_id, absolute_time)
                VALUES (?, ?, ?)
            """, fingerprint_data)
            
            conn.commit()
            logger.info(f"✅ Added song '{song_name}' with {count} fingerprints")
            return count
            
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"❌ Database error while adding song: {e}")
            raise
    
    def query(self, query_fingerprints: List[Tuple], 
              min_matches: int = 5) -> Optional[Tuple[str, int, float]]:
        """
        Query the database with sample fingerprints
        
        Args:
            query_fingerprints: List of ((hash_token), sample_time) tuples
            min_matches: Minimum number of matches required
            
        Returns:
            Tuple of (song_name, match_count, confidence) or None if no match
            confidence is the ratio of matches to total query fingerprints
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Dictionary to store matches: {song_name: [offsets]}
        matches_by_song: dict = defaultdict(list)
        
        # For each query fingerprint
        for hash_token, sample_time in query_fingerprints:
            hash_str = self._hash_to_string(hash_token)
            
            # Look up in database
            cursor.execute("""
                SELECT s.name, f.absolute_time
                FROM fingerprints f
                JOIN songs s ON f.song_id = s.id
                WHERE f.hash_token = ?
            """, (hash_str,))
            
            # Get all matches for this hash
            for row in cursor.fetchall():
                song_name = row[0]
                db_time = row[1]
                # Calculate offset
                offset = db_time - sample_time
                matches_by_song[song_name].append(offset)
        
        if not matches_by_song:
            return None
        
        # Find the best match using histogram analysis
        best_song = None
        best_score = 0
        best_confidence = 0.0
        
        for song_name, offsets in matches_by_song.items():
            # Count occurrences of each offset
            offset_counter = Counter(offsets)
            
            # Find the most frequent offset (time coherency)
            if offset_counter:
                most_common_offset, count = offset_counter.most_common(1)[0]
                
                # Score is the count of matches with the same offset
                if count >= min_matches and count > best_score:
                    best_song = song_name
                    best_score = count
                    best_confidence = count / len(query_fingerprints) if query_fingerprints else 0
        
        if best_song is None:
            return None
        
        return (best_song, best_score, best_confidence)
    
    def get_song_count(self) -> int:
        """Get the number of songs in the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM songs")
        return cursor.fetchone()[0]
    
    def get_fingerprint_count(self) -> int:
        """Get the total number of fingerprints in the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fingerprints")
        return cursor.fetchone()[0]
    
    def list_songs(self) -> List[str]:
        """Get list of all song names in the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM songs ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    
    def delete_song(self, song_name: str) -> Tuple[bool, int]:
        """
        Delete a specific song from the database
        
        Args:
            song_name: Name/ID of the song to delete
            
        Returns:
            Tuple of (success, deleted_fingerprints_count)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get song_id and count fingerprints before deletion
            cursor.execute("SELECT id FROM songs WHERE name = ?", (song_name,))
            song_row = cursor.fetchone()
            
            if song_row is None:
                return (False, 0)
            
            song_id = song_row[0]
            
            # Count fingerprints to be deleted
            cursor.execute("SELECT COUNT(*) FROM fingerprints WHERE song_id = ?", (song_id,))
            deleted_count = cursor.fetchone()[0]
            
            # Delete song (fingerprints will be deleted by CASCADE)
            cursor.execute("DELETE FROM songs WHERE id = ?", (song_id,))
            
            conn.commit()
            logger.info(f"✅ Deleted song '{song_name}' with {deleted_count} fingerprints")
            return (True, deleted_count)
            
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"❌ Database error while deleting song: {e}")
            raise
    
    def clear(self):
        """Clear all data from the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM fingerprints")
            cursor.execute("DELETE FROM songs")
            conn.commit()
            logger.info("✅ Database cleared")
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"❌ Database error while clearing: {e}")
            raise
    
    def clear_all(self):
        """Alias for clear() - Clear all data from the database"""
        self.clear()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("✅ Database connection closed")


# Alias for backward compatibility
InMemoryDB = PersistentDB
