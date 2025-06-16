#!/usr/bin/env python3
"""
Cleanup Test Data Script
Removes test data from the ZackGPT database
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def cleanup_database():
    """Clean up test data from the main database."""
    db_path = "data/zackgpt.db"
    
    if not os.path.exists(db_path):
        print("✅ No database file found - nothing to clean")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count test data before cleanup
        test_threads = cursor.execute("""
            SELECT COUNT(*) FROM threads 
            WHERE title LIKE '%Test%' OR title LIKE '%test%' 
               OR title LIKE '%Performance%' OR title LIKE '%Query%'
        """).fetchone()[0]
        
        test_messages = cursor.execute("""
            SELECT COUNT(*) FROM messages 
            WHERE thread_id IN (
                SELECT id FROM threads 
                WHERE title LIKE '%Test%' OR title LIKE '%test%' 
                   OR title LIKE '%Performance%' OR title LIKE '%Query%'
            )
        """).fetchone()[0]
        
        test_memories = cursor.execute("""
            SELECT COUNT(*) FROM memories 
            WHERE question LIKE '%test%' OR answer LIKE '%test%'
               OR question LIKE '%Test%' OR answer LIKE '%Test%'
        """).fetchone()[0]
        
        print(f"Found test data:")
        print(f"  - {test_threads} test threads")
        print(f"  - {test_messages} test messages")
        print(f"  - {test_memories} test memories")
        
        if test_threads == 0 and test_messages == 0 and test_memories == 0:
            print("✅ No test data found - database is clean")
            return
        
        # Delete test data
        print("\nCleaning up test data...")
        
        # Delete messages first (foreign key constraint)
        cursor.execute("""
            DELETE FROM messages 
            WHERE thread_id IN (
                SELECT id FROM threads 
                WHERE title LIKE '%Test%' OR title LIKE '%test%' 
                   OR title LIKE '%Performance%' OR title LIKE '%Query%'
            )
        """)
        
        # Delete test threads
        cursor.execute("""
            DELETE FROM threads 
            WHERE title LIKE '%Test%' OR title LIKE '%test%' 
               OR title LIKE '%Performance%' OR title LIKE '%Query%'
        """)
        
        # Delete test memories
        cursor.execute("""
            DELETE FROM memories 
            WHERE question LIKE '%test%' OR answer LIKE '%test%'
               OR question LIKE '%Test%' OR answer LIKE '%Test%'
        """)
        
        conn.commit()
        
        # Count remaining data
        remaining_threads = cursor.execute("SELECT COUNT(*) FROM threads").fetchone()[0]
        remaining_messages = cursor.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        remaining_memories = cursor.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        
        print(f"✅ Cleanup complete!")
        print(f"Remaining data:")
        print(f"  - {remaining_threads} threads")
        print(f"  - {remaining_messages} messages")
        print(f"  - {remaining_memories} memories")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")

def cleanup_test_files():
    """Clean up test database files."""
    test_files_found = 0
    
    # Look for test database files
    for pattern in ["test_*.db", "**/test_*.db"]:
        import glob
        for file_path in glob.glob(pattern, recursive=True):
            try:
                os.remove(file_path)
                print(f"🗑️ Removed test file: {file_path}")
                test_files_found += 1
            except Exception as e:
                print(f"❌ Could not remove {file_path}: {e}")
    
    if test_files_found == 0:
        print("✅ No test database files found")
    else:
        print(f"✅ Removed {test_files_found} test database files")

if __name__ == "__main__":
    print("🧹 ZackGPT Test Data Cleanup")
    print("=" * 40)
    
    print("\n1. Cleaning up test database files...")
    cleanup_test_files()
    
    print("\n2. Cleaning up test data from main database...")
    cleanup_database()
    
    print("\n🎉 Cleanup complete!") 