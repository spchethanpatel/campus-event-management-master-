#!/usr/bin/env python3
"""
Quick Data Entry for Key Activities
Event Creation, Student Registration, Attendance, Feedback
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

def create_event():
    """Create a new event"""
    print("\n🎉 CREATE NEW EVENT")
    print("-" * 30)
    
    # Get available colleges
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT college_id, name FROM Colleges")
    colleges = cursor.fetchall()
    
    if not colleges:
        print("❌ No colleges found. Please add a college first.")
        return
    
    print("Available Colleges:")
    for college in colleges:
        print(f"  {college['college_id']}: {college['name']}")
    
    college_id = int(input("Select College ID: "))
    
    # Get available event types
    cursor.execute("SELECT type_id, name FROM EventTypes")
    event_types = cursor.fetchall()
    
    print("\nAvailable Event Types:")
    for event_type in event_types:
        print(f"  {event_type['type_id']}: {event_type['name']}")
    
    type_id = int(input("Select Event Type ID: "))
    
    # Get available admins
    cursor.execute("SELECT admin_id, name FROM Admins WHERE college_id = ?", (college_id,))
    admins = cursor.fetchall()
    
    if not admins:
        print("❌ No admins found for this college.")
        return
    
    print("\nAvailable Admins:")
    for admin in admins:
        print(f"  {admin['admin_id']}: {admin['name']}")
    
    created_by = int(input("Select Admin ID: "))
    
    # Get event details
    title = input("Event Title: ")
    description = input("Description: ")
    venue = input("Venue: ")
    
    # Set future dates
    start_date = datetime.now() + timedelta(days=7)
    end_date = start_date + timedelta(hours=4)
    
    start_time = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_time = end_date.strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"Start Time: {start_time}")
    print(f"End Time: {end_time}")
    
    capacity = int(input("Capacity: "))
    semester = input("Semester: ")
    
    try:
        cursor.execute("""
            INSERT INTO Events (college_id, title, description, type_id, venue, 
                              start_time, end_time, capacity, created_by, semester, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (college_id, title, description, type_id, venue, start_time, 
              end_time, capacity, created_by, semester, "active"))
        
        event_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Event created successfully with ID: {event_id}")
        
    except Exception as e:
        print(f"❌ Error creating event: {e}")
    finally:
        conn.close()

def register_student():
    """Register a student for an event"""
    print("\n📝 STUDENT REGISTRATION")
    print("-" * 30)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get available students
    cursor.execute("SELECT student_id, name, email FROM Students")
    students = cursor.fetchall()
    
    if not students:
        print("❌ No students found. Please add students first.")
        return
    
    print("Available Students:")
    for student in students:
        print(f"  {student['student_id']}: {student['name']} ({student['email']})")
    
    student_id = int(input("Select Student ID: "))
    
    # Get available events
    cursor.execute("""
        SELECT e.event_id, e.title, e.start_time, e.capacity, c.name as college_name
        FROM Events e
        LEFT JOIN Colleges c ON e.college_id = c.college_id
        WHERE e.status = 'active' AND e.start_time > datetime('now')
        ORDER BY e.start_time
    """)
    events = cursor.fetchall()
    
    if not events:
        print("❌ No active events found.")
        return
    
    print("\nAvailable Events:")
    for event in events:
        print(f"  {event['event_id']}: {event['title']} at {event['college_name']} on {event['start_time']}")
    
    event_id = int(input("Select Event ID: "))
    
    # Check if already registered
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM Registrations 
        WHERE student_id = ? AND event_id = ?
    """, (student_id, event_id))
    
    if cursor.fetchone()['count'] > 0:
        print("❌ Student is already registered for this event.")
        return
    
    # Check capacity
    cursor.execute("""
        SELECT capacity, 
               (SELECT COUNT(*) FROM Registrations WHERE event_id = ? AND status = 'registered') as current_registrations
        FROM Events 
        WHERE event_id = ?
    """, (event_id, event_id))
    
    capacity_info = cursor.fetchone()
    if capacity_info['current_registrations'] >= capacity_info['capacity']:
        print("❌ Event is at full capacity.")
        return
    
    try:
        cursor.execute("""
            INSERT INTO Registrations (student_id, event_id, status) 
            VALUES (?, ?, ?)
        """, (student_id, event_id, "registered"))
        
        registration_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Student registered successfully with Registration ID: {registration_id}")
        
    except Exception as e:
        print(f"❌ Error registering student: {e}")
    finally:
        conn.close()

def mark_attendance():
    """Mark attendance for an event"""
    print("\n✅ MARK ATTENDANCE")
    print("-" * 30)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get registrations for events that have started
    cursor.execute("""
        SELECT r.registration_id, s.name as student_name, e.title as event_title, e.start_time
        FROM Registrations r
        LEFT JOIN Students s ON r.student_id = s.student_id
        LEFT JOIN Events e ON r.event_id = e.event_id
        WHERE r.status = 'registered' 
        AND e.start_time <= datetime('now')
        AND NOT EXISTS (SELECT 1 FROM Attendance WHERE registration_id = r.registration_id)
        ORDER BY e.start_time
    """)
    
    registrations = cursor.fetchall()
    
    if not registrations:
        print("❌ No pending attendance records found.")
        return
    
    print("Pending Attendance:")
    for reg in registrations:
        print(f"  {reg['registration_id']}: {reg['student_name']} - {reg['event_title']}")
    
    registration_id = int(input("Select Registration ID: "))
    attended = input("Did they attend? (y/n): ").lower() == 'y'
    
    try:
        cursor.execute("""
            INSERT INTO Attendance (registration_id, attended, check_in_time) 
            VALUES (?, ?, ?)
        """, (registration_id, 1 if attended else 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        attendance_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Attendance marked successfully with ID: {attendance_id}")
        
    except Exception as e:
        print(f"❌ Error marking attendance: {e}")
    finally:
        conn.close()

def submit_feedback():
    """Submit feedback for an event"""
    print("\n💬 SUBMIT FEEDBACK")
    print("-" * 30)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get registrations that have attendance but no feedback
    cursor.execute("""
        SELECT r.registration_id, s.name as student_name, e.title as event_title
        FROM Registrations r
        LEFT JOIN Students s ON r.student_id = s.student_id
        LEFT JOIN Events e ON r.event_id = e.event_id
        LEFT JOIN Attendance a ON r.registration_id = a.registration_id
        WHERE r.status = 'registered' 
        AND a.attended = 1
        AND NOT EXISTS (SELECT 1 FROM Feedback WHERE registration_id = r.registration_id)
        ORDER BY e.start_time
    """)
    
    registrations = cursor.fetchall()
    
    if not registrations:
        print("❌ No eligible registrations for feedback found.")
        return
    
    print("Eligible for Feedback:")
    for reg in registrations:
        print(f"  {reg['registration_id']}: {reg['student_name']} - {reg['event_title']}")
    
    registration_id = int(input("Select Registration ID: "))
    rating = int(input("Rating (1-5): "))
    
    if not 1 <= rating <= 5:
        print("❌ Rating must be between 1 and 5.")
        return
    
    comments = input("Comments (optional): ")
    
    try:
        cursor.execute("""
            INSERT INTO Feedback (registration_id, rating, comments) 
            VALUES (?, ?, ?)
        """, (registration_id, rating, comments))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Feedback submitted successfully with ID: {feedback_id}")
        
    except Exception as e:
        print(f"❌ Error submitting feedback: {e}")
    finally:
        conn.close()

def main():
    """Main menu"""
    print("🎯 QUICK DATA ENTRY - EVENT MANAGEMENT SYSTEM")
    print("=" * 60)
    print("1. Create Event")
    print("2. Register Student")
    print("3. Mark Attendance")
    print("4. Submit Feedback")
    print("5. View Current Data")
    print("6. Exit")
    print("=" * 60)
    
    while True:
        choice = input("\nSelect an option (1-6): ")
        
        if choice == "1":
            create_event()
        elif choice == "2":
            register_student()
        elif choice == "3":
            mark_attendance()
        elif choice == "4":
            submit_feedback()
        elif choice == "5":
            print("\n📊 Current Data Summary:")
            conn = get_db_connection()
            cursor = conn.cursor()
            
            tables = ['Events', 'Registrations', 'Attendance', 'Feedback']
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                print(f"   {table}: {count}")
            conn.close()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()
