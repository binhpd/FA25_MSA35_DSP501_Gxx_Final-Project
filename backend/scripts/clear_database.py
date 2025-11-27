#!/usr/bin/env python3
"""
Script to clear all songs and fingerprints from the database
"""

import sys
import os
import argparse

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import PersistentDB


def clear_database(db_path: str = "music_recognition.db", confirm: bool = False):
    """
    Clear all data from the database
    
    Args:
        db_path: Path to database file
        confirm: If True, skip confirmation prompt
    """
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    # Initialize database
    db = PersistentDB(db_path=db_path)
    
    # Get current stats
    song_count = db.get_song_count()
    fingerprint_count = db.get_fingerprint_count()
    
    if song_count == 0 and fingerprint_count == 0:
        print("✅ Database is already empty")
        return True
    
    # Show current stats
    print("=" * 60)
    print("📊 Current Database Status:")
    print(f"   Songs: {song_count}")
    print(f"   Fingerprints: {fingerprint_count}")
    print("=" * 60)
    
    # Confirmation
    if not confirm:
        response = input("\n⚠️  Are you sure you want to delete ALL data? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Operation cancelled")
            return False
    
    # Clear database
    try:
        db.clear()
        print("\n✅ Database cleared successfully!")
        print(f"   Deleted: {song_count} songs, {fingerprint_count} fingerprints")
        return True
    except Exception as e:
        print(f"\n❌ Error clearing database: {e}")
        return False
    finally:
        db.close()


def delete_song(db_path: str, song_name: str, confirm: bool = False):
    """
    Delete a specific song from the database
    
    Args:
        db_path: Path to database file
        song_name: Name of the song to delete
        confirm: If True, skip confirmation prompt
    """
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    # Initialize database
    db = PersistentDB(db_path=db_path)
    
    # Check if song exists
    songs = db.list_songs()
    if song_name not in songs:
        print(f"❌ Song '{song_name}' not found in database")
        print(f"   Available songs: {', '.join(songs) if songs else 'None'}")
        db.close()
        return False
    
    # Confirmation
    if not confirm:
        response = input(f"\n⚠️  Are you sure you want to delete '{song_name}'? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Operation cancelled")
            db.close()
            return False
    
    # Delete song
    try:
        success, deleted_count = db.delete_song(song_name)
        if success:
            print(f"\n✅ Song '{song_name}' deleted successfully!")
            print(f"   Deleted: {deleted_count} fingerprints")
            return True
        else:
            print(f"\n❌ Failed to delete song '{song_name}'")
            return False
    except Exception as e:
        print(f"\n❌ Error deleting song: {e}")
        return False
    finally:
        db.close()


def list_songs(db_path: str):
    """
    List all songs in the database
    
    Args:
        db_path: Path to database file
    """
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    # Initialize database
    db = PersistentDB(db_path=db_path)
    
    try:
        songs = db.list_songs()
        song_count = db.get_song_count()
        fingerprint_count = db.get_fingerprint_count()
        
        print("=" * 60)
        print("📊 Database Status:")
        print(f"   Total Songs: {song_count}")
        print(f"   Total Fingerprints: {fingerprint_count}")
        print("=" * 60)
        
        if songs:
            print("\n📝 Songs in database:")
            for i, song in enumerate(songs, 1):
                print(f"   {i}. {song}")
        else:
            print("\n📝 Database is empty")
    finally:
        db.close()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Clear database or delete songs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clear all data (with confirmation)
  python3 clear_database.py --clear
  
  # Clear all data (without confirmation)
  python3 clear_database.py --clear --yes
  
  # Delete a specific song
  python3 clear_database.py --delete "Song_Name"
  
  # List all songs
  python3 clear_database.py --list
  
  # Use custom database path
  python3 clear_database.py --clear --db-path custom.db
        """
    )
    
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear all songs and fingerprints from database'
    )
    
    parser.add_argument(
        '--delete',
        type=str,
        metavar='SONG_NAME',
        help='Delete a specific song by name'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all songs in database'
    )
    
    parser.add_argument(
        '--db-path',
        type=str,
        default='music_recognition.db',
        help='Path to database file (default: music_recognition.db)'
    )
    
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    args = parser.parse_args()
    
    # Change to backend directory to use relative path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    os.chdir(backend_dir)
    
    # Resolve database path
    db_path = os.path.abspath(args.db_path)
    
    # Execute command
    if args.clear:
        clear_database(db_path, confirm=args.yes)
    elif args.delete:
        delete_song(db_path, args.delete, confirm=args.yes)
    elif args.list:
        list_songs(db_path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

