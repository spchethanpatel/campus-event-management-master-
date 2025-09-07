#!/usr/bin/env python3
"""
Test script to verify database connection and basic operations.
"""
import sqlite3
from pathlib import Path
from typing import List, Tuple, Any

from config import settings


def test_database_connection() -> bool:
    """Test basic database connection and operations."""
    
    db_path = Path(settings.database_path)
    
    if not db_path.exists():
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        # Test basic connection
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        print(f"✅ Database connection successful!")
        print(f"📁 Database path: {db_path}")
        print(f"📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"   • {table[0]}")
        
        # Test some basic queries
        print("\n🔍 Testing basic queries:")
        
        # Test each table
        table_tests = [
            "Colleges", "Admins", "Students", "EventTypes", 
            "Events", "Registrations", "Attendance", "Feedback"
        ]
        
        for table_name in table_tests:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"   • {table_name}: {count} records")
                
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 2;")
                    sample = cursor.fetchall()
                    print(f"     Sample: {sample}")
            except sqlite3.OperationalError:
                print(f"   • {table_name}: Table not found")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def main():
    """Main function to run database tests."""
    print("🧪 Testing Event Management Database Connection")
    print("=" * 60)
    
    success = test_database_connection()
    
    if success:
        print("\n✅ Database is ready for FastAPI integration!")
    else:
        print("\n❌ Database connection failed!")


if __name__ == "__main__":
    main()

