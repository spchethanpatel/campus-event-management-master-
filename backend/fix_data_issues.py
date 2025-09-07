#!/usr/bin/env python3
"""
Fix Data Consistency Issues
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

def get_db_connection():
    """Get database connection"""
    db_path = Path(__file__).parent.parent / "database" / "event_management_db.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def fix_past_events():
    """Fix past events that are marked as active"""
    print("🔧 FIXING PAST EVENTS")
    print("=" * 40)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Find past events that are still active
        cursor.execute("""
            SELECT event_id, title, start_time 
            FROM Events 
            WHERE start_time < datetime('now') AND status = 'active'
        """)
        past_events = cursor.fetchall()
        
        if not past_events:
            print("✅ No past events found")
            return True
        
        print(f"Found {len(past_events)} past events:")
        for event in past_events:
            print(f"  - {event['title']} (started: {event['start_time']})")
        
        # Update them to completed status
        cursor.execute("""
            UPDATE Events 
            SET status = 'completed' 
            WHERE start_time < datetime('now') AND status = 'active'
        """)
        
        updated_count = cursor.rowcount
        conn.commit()
        
        print(f"✅ Updated {updated_count} events to 'completed' status")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing past events: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def enable_foreign_keys():
    """Enable foreign key constraints"""
    print("\n🔗 ENABLING FOREIGN KEY CONSTRAINTS")
    print("=" * 40)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Verify it's enabled
        cursor.execute("PRAGMA foreign_keys")
        fk_enabled = cursor.fetchone()[0]
        
        if fk_enabled:
            print("✅ Foreign key constraints enabled")
        else:
            print("❌ Failed to enable foreign key constraints")
        
        conn.close()
        return fk_enabled
        
    except Exception as e:
        print(f"❌ Error enabling foreign keys: {e}")
        return False

def create_future_events():
    """Create some future events for testing"""
    print("\n🎉 CREATING FUTURE EVENTS")
    print("=" * 40)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get available colleges and admins
        cursor.execute("SELECT college_id FROM Colleges LIMIT 1")
        college = cursor.fetchone()
        
        cursor.execute("SELECT admin_id FROM Admins LIMIT 1")
        admin = cursor.fetchone()
        
        if not college or not admin:
            print("❌ No colleges or admins found")
            return False
        
        # Create future events
        future_events = [
            {
                "title": "Python Workshop 2024",
                "description": "Learn Python programming from basics to advanced",
                "type_id": 1,
                "venue": "Computer Lab A",
                "start_time": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": (datetime.now() + timedelta(days=7, hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
                "capacity": 30,
                "semester": "Spring 2024"
            },
            {
                "title": "Web Development Bootcamp",
                "description": "Full-stack web development intensive course",
                "type_id": 2,
                "venue": "Main Auditorium",
                "start_time": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": (datetime.now() + timedelta(days=16)).strftime("%Y-%m-%d %H:%M:%S"),
                "capacity": 50,
                "semester": "Spring 2024"
            },
            {
                "title": "Data Science Conference",
                "description": "Latest trends in data science and AI",
                "type_id": 3,
                "venue": "Conference Hall",
                "start_time": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": (datetime.now() + timedelta(days=21, hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
                "capacity": 100,
                "semester": "Spring 2024"
            }
        ]
        
        created_count = 0
        for event in future_events:
            cursor.execute("""
                INSERT INTO Events (college_id, title, description, type_id, venue, 
                                  start_time, end_time, capacity, created_by, semester, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (college['college_id'], event['title'], event['description'], 
                  event['type_id'], event['venue'], event['start_time'], 
                  event['end_time'], event['capacity'], admin['admin_id'], 
                  event['semester'], 'active'))
            created_count += 1
        
        conn.commit()
        print(f"✅ Created {created_count} future events")
        return True
        
    except Exception as e:
        print(f"❌ Error creating future events: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """Fix all data issues"""
    print("🔧 FIXING DATA CONSISTENCY ISSUES")
    print("=" * 50)
    
    fixes = [
        ("Past Events", fix_past_events),
        ("Foreign Keys", enable_foreign_keys),
        ("Future Events", create_future_events)
    ]
    
    all_fixed = True
    
    for fix_name, fix_func in fixes:
        try:
            result = fix_func()
            if result:
                print(f"✅ {fix_name} fixed successfully")
            else:
                print(f"❌ {fix_name} fix failed")
                all_fixed = False
        except Exception as e:
            print(f"❌ {fix_name} fix crashed: {e}")
            all_fixed = False
    
    print("\n" + "=" * 50)
    if all_fixed:
        print("🎉 All data issues fixed successfully!")
    else:
        print("⚠️  Some issues could not be fixed")
    
    return all_fixed

if __name__ == "__main__":
    main()
