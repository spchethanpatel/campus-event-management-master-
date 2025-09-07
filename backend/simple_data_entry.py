#!/usr/bin/env python3
"""
Simple Data Entry Script for Testing.
Adds data to all tables with proper validation.
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

from config import settings


def add_test_data():
    """Add comprehensive test data to all tables."""
    print("🔧 Adding test data to all tables...")
    
    db_path = Path(settings.database_path)
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # 1. Add Colleges
        print("\n🏫 Adding Colleges...")
        colleges = [
            ("Test University", "Test City"),
            ("Demo College", "Demo Town"),
            ("Sample Institute", "Sample City")
        ]
        
        for name, location in colleges:
            cursor.execute("""
                INSERT OR IGNORE INTO Colleges (name, location, status)
                VALUES (?, ?, 'active')
            """, (name, location))
            print(f"   ✅ Added college: {name}")
        
        # 2. Add Admins
        print("\n👨‍💼 Adding Admins...")
        cursor.execute("SELECT college_id FROM Colleges LIMIT 3")
        colleges_data = cursor.fetchall()
        
        admins = [
            ("John Admin", "john.admin@test.com", "Event Coordinator"),
            ("Jane Manager", "jane.manager@test.com", "Student Affairs"),
            ("Bob Director", "bob.director@test.com", "IT Manager")
        ]
        
        for i, (name, email, role) in enumerate(admins):
            college_id = colleges_data[i][0]
            cursor.execute("""
                INSERT OR IGNORE INTO Admins (college_id, name, email, role, status)
                VALUES (?, ?, ?, ?, 'active')
            """, (college_id, name, email, role))
            print(f"   ✅ Added admin: {name}")
        
        # 3. Add Students
        print("\n🎓 Adding Students...")
        students = [
            ("Alice Johnson", "alice.johnson@test.com", "2024", "Computer Science"),
            ("Bob Smith", "bob.smith@test.com", "2023", "Engineering"),
            ("Carol Davis", "carol.davis@test.com", "2024", "Business"),
            ("David Wilson", "david.wilson@test.com", "2025", "Mathematics"),
            ("Eva Brown", "eva.brown@test.com", "2023", "Physics")
        ]
        
        for i, (name, email, year, department) in enumerate(students):
            college_id = colleges_data[i % len(colleges_data)][0]
            cursor.execute("""
                INSERT OR IGNORE INTO Students (college_id, name, email, year, department, status)
                VALUES (?, ?, ?, ?, ?, 'active')
            """, (college_id, name, email, year, department))
            print(f"   ✅ Added student: {name}")
        
        # 4. Add Event Types
        print("\n📋 Adding Event Types...")
        event_types = [
            "Workshop",
            "Seminar", 
            "Conference",
            "Hackathon",
            "Networking"
        ]
        
        for event_type in event_types:
            cursor.execute("""
                INSERT OR IGNORE INTO EventTypes (name)
                VALUES (?)
            """, (event_type,))
            print(f"   ✅ Added event type: {event_type}")
        
        # 5. Add Events
        print("\n🎉 Adding Events...")
        cursor.execute("SELECT college_id FROM Colleges LIMIT 1")
        college = cursor.fetchone()
        cursor.execute("SELECT admin_id FROM Admins LIMIT 1")
        admin = cursor.fetchone()
        cursor.execute("SELECT type_id FROM EventTypes LIMIT 3")
        event_types_data = cursor.fetchall()
        
        if college and admin and event_types_data:
            now = datetime.now()
            
            events = [
                {
                    "title": "Python Programming Workshop",
                    "description": "Learn Python basics and advanced concepts",
                    "venue": "Computer Lab A",
                    "start_time": now + timedelta(days=7, hours=9),
                    "end_time": now + timedelta(days=7, hours=17),
                    "capacity": 30,
                    "type_id": event_types_data[0][0]
                },
                {
                    "title": "Web Development Bootcamp",
                    "description": "Full-stack web development intensive",
                    "venue": "Main Auditorium",
                    "start_time": now + timedelta(days=14, hours=10),
                    "end_time": now + timedelta(days=16, hours=18),
                    "capacity": 50,
                    "type_id": event_types_data[1][0]
                },
                {
                    "title": "Data Science Conference",
                    "description": "Latest trends in data science and AI",
                    "venue": "Conference Center",
                    "start_time": now + timedelta(days=21, hours=8),
                    "end_time": now + timedelta(days=21, hours=20),
                    "capacity": 100,
                    "type_id": event_types_data[2][0]
                }
            ]
            
            for event_data in events:
                cursor.execute("""
                    INSERT OR IGNORE INTO Events (title, description, venue, start_time, end_time, 
                                                 capacity, status, college_id, type_id, created_by, semester)
                    VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, 'Fall 2024')
                """, (
                    event_data['title'],
                    event_data['description'],
                    event_data['venue'],
                    event_data['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
                    event_data['end_time'].strftime("%Y-%m-%d %H:%M:%S"),
                    event_data['capacity'],
                    college[0],
                    event_data['type_id'],
                    admin[0]
                ))
                print(f"   ✅ Added event: {event_data['title']}")
        
        # 6. Add Registrations
        print("\n📝 Adding Registrations...")
        cursor.execute("SELECT student_id FROM Students LIMIT 5")
        students_data = cursor.fetchall()
        cursor.execute("SELECT event_id FROM Events WHERE status = 'active' LIMIT 3")
        events_data = cursor.fetchall()
        
        if students_data and events_data:
            registrations_added = 0
            for i, student in enumerate(students_data):
                event = events_data[i % len(events_data)]
                
                try:
                    cursor.execute("""
                        INSERT INTO Registrations (student_id, event_id, status, registration_time)
                        VALUES (?, ?, 'registered', datetime('now'))
                    """, (student[0], event[0]))
                    registrations_added += 1
                    print(f"   ✅ Registered student {student[0]} for event {event[0]}")
                except sqlite3.IntegrityError as e:
                    print(f"   ⚠️  Registration failed: {e}")
            
            print(f"   📊 Added {registrations_added} registrations")
        
        # 7. Add Attendance
        print("\n✅ Adding Attendance...")
        cursor.execute("SELECT registration_id FROM Registrations LIMIT 3")
        registrations_data = cursor.fetchall()
        
        if registrations_data:
            attendance_added = 0
            for registration in registrations_data:
                try:
                    cursor.execute("""
                        INSERT INTO Attendance (registration_id, attended, check_in_time)
                        VALUES (?, 1, datetime('now'))
                    """, (registration[0],))
                    attendance_added += 1
                    print(f"   ✅ Marked attendance for registration {registration[0]}")
                except sqlite3.IntegrityError as e:
                    print(f"   ⚠️  Attendance failed: {e}")
            
            print(f"   📊 Added {attendance_added} attendance records")
        
        # 8. Add Feedback (for completed events)
        print("\n💬 Adding Feedback...")
        # Create a completed event for feedback testing
        cursor.execute("""
            INSERT OR IGNORE INTO Events (title, description, venue, start_time, end_time, 
                                         capacity, status, college_id, type_id, created_by, semester)
            VALUES ('Completed Workshop', 'Past event for feedback testing', 'Room 101', 
                    datetime('now', '-2 days', '9:00'), datetime('now', '-2 days', '17:00'), 
                    20, 'completed', ?, ?, ?, 'Fall 2024')
        """, (college[0], event_types_data[0][0], admin[0]))
        
        # Get the completed event
        cursor.execute("SELECT event_id FROM Events WHERE title = 'Completed Workshop'")
        completed_event = cursor.fetchone()
        
        if completed_event:
            # Register a student for the completed event
            cursor.execute("SELECT student_id FROM Students LIMIT 1")
            student = cursor.fetchone()
            
            if student:
                try:
                    cursor.execute("""
                        INSERT INTO Registrations (student_id, event_id, status, registration_time)
                        VALUES (?, ?, 'registered', datetime('now', '-3 days'))
                    """, (student[0], completed_event[0]))
                    
                    registration_id = cursor.lastrowid
                    
                    # Mark attendance
                    cursor.execute("""
                        INSERT INTO Attendance (registration_id, attended, check_in_time)
                        VALUES (?, 1, datetime('now', '-2 days', '9:30'))
                    """, (registration_id,))
                    
                    # Add feedback
                    cursor.execute("""
                        INSERT INTO Feedback (registration_id, rating, comments, submitted_at)
                        VALUES (?, 5, 'Excellent workshop! Very informative.', datetime('now', '-1 day'))
                    """, (registration_id,))
                    
                    print(f"   ✅ Added feedback for completed event")
                    
                except sqlite3.IntegrityError as e:
                    print(f"   ⚠️  Feedback failed: {e}")
        
        conn.commit()
        print("\n🎉 Test data added successfully!")
        
        # Show summary
        print("\n📊 Data Summary:")
        cursor.execute("SELECT COUNT(*) FROM Colleges")
        print(f"   Colleges: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM Admins")
        print(f"   Admins: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM Students")
        print(f"   Students: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM EventTypes")
        print(f"   Event Types: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM Events")
        print(f"   Events: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM Registrations")
        print(f"   Registrations: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM Attendance")
        print(f"   Attendance: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM Feedback")
        print(f"   Feedback: {cursor.fetchone()[0]}")
        
    except Exception as e:
        print(f"❌ Error adding test data: {e}")
        conn.rollback()
    finally:
        conn.close()


def test_error_scenarios():
    """Test various error scenarios."""
    print("\n🚨 Testing Error Scenarios...")
    
    db_path = Path(settings.database_path)
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Test 1: Duplicate registration
        print("\n1. Testing Duplicate Registration...")
        cursor.execute("SELECT student_id, event_id FROM Registrations LIMIT 1")
        registration = cursor.fetchone()
        
        if registration:
            try:
                cursor.execute("""
                    INSERT INTO Registrations (student_id, event_id, status, registration_time)
                    VALUES (?, ?, 'registered', datetime('now'))
                """, (registration[0], registration[1]))
                
                print("   ❌ FAILED: System allowed duplicate registration")
                conn.rollback()
            except sqlite3.IntegrityError:
                print("   ✅ SUCCESS: System correctly prevented duplicate registration")
                conn.rollback()
        
        # Test 2: Invalid feedback rating
        print("\n2. Testing Invalid Feedback Rating...")
        cursor.execute("SELECT registration_id FROM Registrations LIMIT 1")
        registration = cursor.fetchone()
        
        if registration:
            try:
                cursor.execute("""
                    INSERT INTO Feedback (registration_id, rating, comments, submitted_at)
                    VALUES (?, 6, 'Invalid rating test', datetime('now'))
                """, (registration[0],))
                
                print("   ❌ FAILED: System allowed invalid rating")
                conn.rollback()
            except sqlite3.IntegrityError:
                print("   ✅ SUCCESS: System correctly prevented invalid rating")
                conn.rollback()
        
        # Test 3: Negative capacity
        print("\n3. Testing Negative Capacity...")
        try:
            cursor.execute("""
                INSERT INTO Events (title, description, start_time, end_time, capacity, 
                                 status, college_id, type_id, created_by, semester)
                VALUES ('Invalid Event', 'Test', datetime('now', '+1 hour'), 
                        datetime('now', '+2 hours'), -5, 'active', 1, 1, 1, 'Fall 2024')
            """)
            
            print("   ❌ FAILED: System allowed negative capacity")
            conn.rollback()
        except sqlite3.IntegrityError:
            print("   ✅ SUCCESS: System correctly prevented negative capacity")
            conn.rollback()
        
        # Test 4: Invalid event times
        print("\n4. Testing Invalid Event Times...")
        try:
            cursor.execute("""
                INSERT INTO Events (title, description, start_time, end_time, capacity, 
                                 status, college_id, type_id, created_by, semester)
                VALUES ('Invalid Times Event', 'Test', datetime('now', '+2 hours'), 
                        datetime('now', '+1 hour'), 10, 'active', 1, 1, 1, 'Fall 2024')
            """)
            
            print("   ❌ FAILED: System allowed invalid event times")
            conn.rollback()
        except sqlite3.IntegrityError:
            print("   ✅ SUCCESS: System correctly prevented invalid event times")
            conn.rollback()
        
        print("\n🎉 Error scenario testing completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    finally:
        conn.close()


def main():
    """Main function."""
    print("🧪 SIMPLE DATA ENTRY TESTING")
    print("=" * 50)
    
    # Add test data
    add_test_data()
    
    # Test error scenarios
    test_error_scenarios()
    
    print("\n✅ Data entry testing completed!")
    print("🎯 You can now test the system with real data!")


if __name__ == "__main__":
    main()
