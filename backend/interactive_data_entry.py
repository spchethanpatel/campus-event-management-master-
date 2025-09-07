#!/usr/bin/env python3
"""
Interactive Data Entry Script.
Allows manual data entry to test the system.
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

from config import settings


def connect_db():
    """Connect to database."""
    db_path = Path(settings.database_path)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def show_menu():
    """Show main menu."""
    print("\n" + "=" * 50)
    print("🎯 INTERACTIVE DATA ENTRY MENU")
    print("=" * 50)
    print("1. Add College")
    print("2. Add Admin")
    print("3. Add Student")
    print("4. Add Event Type")
    print("5. Add Event")
    print("6. Register Student for Event")
    print("7. Mark Attendance")
    print("8. Add Feedback")
    print("9. View Data Summary")
    print("10. Test Error Scenarios")
    print("0. Exit")
    print("=" * 50)


def add_college():
    """Add a new college."""
    print("\n🏫 Adding New College")
    print("-" * 30)
    
    name = input("College Name: ").strip()
    location = input("Location: ").strip()
    
    if not name:
        print("❌ College name is required!")
        return
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO Colleges (name, location, status)
            VALUES (?, ?, 'active')
        """, (name, location))
        
        college_id = cursor.lastrowid
        conn.commit()
        print(f"✅ College added successfully! ID: {college_id}")
        
    except Exception as e:
        print(f"❌ Error adding college: {e}")
        conn.rollback()
    finally:
        conn.close()


def add_admin():
    """Add a new admin."""
    print("\n👨‍💼 Adding New Admin")
    print("-" * 30)
    
    # Show available colleges
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT college_id, name FROM Colleges")
    colleges = cursor.fetchall()
    
    if not colleges:
        print("❌ No colleges available. Please add a college first.")
        conn.close()
        return
    
    print("Available Colleges:")
    for college in colleges:
        print(f"  {college['college_id']}. {college['name']}")
    
    try:
        college_id = int(input("Select College ID: "))
        name = input("Admin Name: ").strip()
        email = input("Email: ").strip()
        role = input("Role: ").strip()
        
        if not name or not email:
            print("❌ Name and email are required!")
            return
        
        cursor.execute("""
            INSERT INTO Admins (college_id, name, email, role, status)
            VALUES (?, ?, ?, ?, 'active')
        """, (college_id, name, email, role))
        
        admin_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Admin added successfully! ID: {admin_id}")
        
    except ValueError:
        print("❌ Invalid college ID!")
    except Exception as e:
        print(f"❌ Error adding admin: {e}")
        conn.rollback()
    finally:
        conn.close()


def add_student():
    """Add a new student."""
    print("\n🎓 Adding New Student")
    print("-" * 30)
    
    # Show available colleges
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT college_id, name FROM Colleges")
    colleges = cursor.fetchall()
    
    if not colleges:
        print("❌ No colleges available. Please add a college first.")
        conn.close()
        return
    
    print("Available Colleges:")
    for college in colleges:
        print(f"  {college['college_id']}. {college['name']}")
    
    try:
        college_id = int(input("Select College ID: "))
        name = input("Student Name: ").strip()
        email = input("Email: ").strip()
        year = input("Year (e.g., 2024): ").strip()
        department = input("Department: ").strip()
        
        if not name or not email:
            print("❌ Name and email are required!")
            return
        
        cursor.execute("""
            INSERT INTO Students (college_id, name, email, year, department, status)
            VALUES (?, ?, ?, ?, ?, 'active')
        """, (college_id, name, email, year, department))
        
        student_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Student added successfully! ID: {student_id}")
        
    except ValueError:
        print("❌ Invalid college ID!")
    except Exception as e:
        print(f"❌ Error adding student: {e}")
        conn.rollback()
    finally:
        conn.close()


def add_event_type():
    """Add a new event type."""
    print("\n📋 Adding New Event Type")
    print("-" * 30)
    
    name = input("Event Type Name: ").strip()
    
    if not name:
        print("❌ Event type name is required!")
        return
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO EventTypes (name)
            VALUES (?)
        """, (name,))
        
        type_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Event type added successfully! ID: {type_id}")
        
    except Exception as e:
        print(f"❌ Error adding event type: {e}")
        conn.rollback()
    finally:
        conn.close()


def add_event():
    """Add a new event."""
    print("\n🎉 Adding New Event")
    print("-" * 30)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Show available colleges
    cursor.execute("SELECT college_id, name FROM Colleges")
    colleges = cursor.fetchall()
    
    if not colleges:
        print("❌ No colleges available. Please add a college first.")
        conn.close()
        return
    
    print("Available Colleges:")
    for college in colleges:
        print(f"  {college['college_id']}. {college['name']}")
    
    # Show available admins
    cursor.execute("SELECT admin_id, name FROM Admins")
    admins = cursor.fetchall()
    
    if not admins:
        print("❌ No admins available. Please add an admin first.")
        conn.close()
        return
    
    print("\nAvailable Admins:")
    for admin in admins:
        print(f"  {admin['admin_id']}. {admin['name']}")
    
    # Show available event types
    cursor.execute("SELECT type_id, name FROM EventTypes")
    event_types = cursor.fetchall()
    
    if not event_types:
        print("❌ No event types available. Please add an event type first.")
        conn.close()
        return
    
    print("\nAvailable Event Types:")
    for event_type in event_types:
        print(f"  {event_type['type_id']}. {event_type['name']}")
    
    try:
        college_id = int(input("\nSelect College ID: "))
        admin_id = int(input("Select Admin ID: "))
        type_id = int(input("Select Event Type ID: "))
        
        title = input("Event Title: ").strip()
        description = input("Description: ").strip()
        venue = input("Venue: ").strip()
        
        # Get start time
        start_date = input("Start Date (YYYY-MM-DD): ").strip()
        start_time = input("Start Time (HH:MM): ").strip()
        start_datetime = f"{start_date} {start_time}:00"
        
        # Get end time
        end_date = input("End Date (YYYY-MM-DD): ").strip()
        end_time = input("End Time (HH:MM): ").strip()
        end_datetime = f"{end_date} {end_time}:00"
        
        capacity = int(input("Capacity: "))
        semester = input("Semester (e.g., Fall 2024): ").strip()
        
        if not title or not start_datetime or not end_datetime:
            print("❌ Title, start time, and end time are required!")
            return
        
        cursor.execute("""
            INSERT INTO Events (title, description, venue, start_time, end_time, 
                             capacity, status, college_id, type_id, created_by, semester)
            VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?)
        """, (title, description, venue, start_datetime, end_datetime, 
              capacity, college_id, type_id, admin_id, semester))
        
        event_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Event added successfully! ID: {event_id}")
        
    except ValueError:
        print("❌ Invalid input!")
    except Exception as e:
        print(f"❌ Error adding event: {e}")
        conn.rollback()
    finally:
        conn.close()


def register_student():
    """Register a student for an event."""
    print("\n📝 Registering Student for Event")
    print("-" * 30)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Show available students
    cursor.execute("SELECT student_id, name, email FROM Students")
    students = cursor.fetchall()
    
    if not students:
        print("❌ No students available. Please add a student first.")
        conn.close()
        return
    
    print("Available Students:")
    for student in students:
        print(f"  {student['student_id']}. {student['name']} ({student['email']})")
    
    # Show available events
    cursor.execute("SELECT event_id, title, start_time FROM Events WHERE status = 'active'")
    events = cursor.fetchall()
    
    if not events:
        print("❌ No active events available. Please add an event first.")
        conn.close()
        return
    
    print("\nAvailable Events:")
    for event in events:
        print(f"  {event['event_id']}. {event['title']} (Starts: {event['start_time']})")
    
    try:
        student_id = int(input("\nSelect Student ID: "))
        event_id = int(input("Select Event ID: "))
        
        cursor.execute("""
            INSERT INTO Registrations (student_id, event_id, status, registration_time)
            VALUES (?, ?, 'registered', datetime('now'))
        """, (student_id, event_id))
        
        registration_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Registration successful! ID: {registration_id}")
        
    except ValueError:
        print("❌ Invalid input!")
    except sqlite3.IntegrityError as e:
        print(f"❌ Registration failed: {e}")
        conn.rollback()
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()


def mark_attendance():
    """Mark attendance for a registration."""
    print("\n✅ Marking Attendance")
    print("-" * 30)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Show available registrations
    cursor.execute("""
        SELECT r.registration_id, s.name as student_name, e.title as event_title
        FROM Registrations r
        JOIN Students s ON r.student_id = s.student_id
        JOIN Events e ON r.event_id = e.event_id
        WHERE r.registration_id NOT IN (SELECT registration_id FROM Attendance)
    """)
    registrations = cursor.fetchall()
    
    if not registrations:
        print("❌ No unmarked registrations available.")
        conn.close()
        return
    
    print("Available Registrations:")
    for reg in registrations:
        print(f"  {reg['registration_id']}. {reg['student_name']} - {reg['event_title']}")
    
    try:
        registration_id = int(input("\nSelect Registration ID: "))
        attended = input("Did they attend? (y/n): ").strip().lower()
        
        attended_value = 1 if attended == 'y' else 0
        
        cursor.execute("""
            INSERT INTO Attendance (registration_id, attended, check_in_time)
            VALUES (?, ?, datetime('now'))
        """, (registration_id, attended_value))
        
        attendance_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Attendance marked successfully! ID: {attendance_id}")
        
    except ValueError:
        print("❌ Invalid input!")
    except sqlite3.IntegrityError as e:
        print(f"❌ Attendance marking failed: {e}")
        conn.rollback()
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()


def add_feedback():
    """Add feedback for a registration."""
    print("\n💬 Adding Feedback")
    print("-" * 30)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Show available registrations with attendance
    cursor.execute("""
        SELECT r.registration_id, s.name as student_name, e.title as event_title
        FROM Registrations r
        JOIN Students s ON r.student_id = s.student_id
        JOIN Events e ON r.event_id = e.event_id
        JOIN Attendance a ON r.registration_id = a.registration_id
        WHERE a.attended = 1 
        AND r.registration_id NOT IN (SELECT registration_id FROM Feedback)
    """)
    registrations = cursor.fetchall()
    
    if not registrations:
        print("❌ No attended registrations available for feedback.")
        conn.close()
        return
    
    print("Available Registrations (with attendance):")
    for reg in registrations:
        print(f"  {reg['registration_id']}. {reg['student_name']} - {reg['event_title']}")
    
    try:
        registration_id = int(input("\nSelect Registration ID: "))
        rating = int(input("Rating (1-5): "))
        comments = input("Comments: ").strip()
        
        if rating < 1 or rating > 5:
            print("❌ Rating must be between 1 and 5!")
            return
        
        cursor.execute("""
            INSERT INTO Feedback (registration_id, rating, comments, submitted_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (registration_id, rating, comments))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Feedback added successfully! ID: {feedback_id}")
        
    except ValueError:
        print("❌ Invalid input!")
    except sqlite3.IntegrityError as e:
        print(f"❌ Feedback failed: {e}")
        conn.rollback()
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()


def view_data_summary():
    """View data summary."""
    print("\n📊 Data Summary")
    print("-" * 30)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM Colleges")
        colleges = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Admins")
        admins = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Students")
        students = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM EventTypes")
        event_types = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Events")
        events = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Registrations")
        registrations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Attendance")
        attendance = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Feedback")
        feedback = cursor.fetchone()[0]
        
        print(f"🏫 Colleges: {colleges}")
        print(f"👨‍💼 Admins: {admins}")
        print(f"🎓 Students: {students}")
        print(f"📋 Event Types: {event_types}")
        print(f"🎉 Events: {events}")
        print(f"📝 Registrations: {registrations}")
        print(f"✅ Attendance: {attendance}")
        print(f"💬 Feedback: {feedback}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()


def test_error_scenarios():
    """Test error scenarios."""
    print("\n🚨 Testing Error Scenarios")
    print("-" * 30)
    
    conn = connect_db()
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
        
        print("\n🎉 Error scenario testing completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    finally:
        conn.close()


def main():
    """Main function."""
    print("🎯 Welcome to Interactive Data Entry System!")
    print("This system allows you to add data and test error handling.")
    
    while True:
        show_menu()
        
        try:
            choice = input("\nEnter your choice (0-10): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                add_college()
            elif choice == "2":
                add_admin()
            elif choice == "3":
                add_student()
            elif choice == "4":
                add_event_type()
            elif choice == "5":
                add_event()
            elif choice == "6":
                register_student()
            elif choice == "7":
                mark_attendance()
            elif choice == "8":
                add_feedback()
            elif choice == "9":
                view_data_summary()
            elif choice == "10":
                test_error_scenarios()
            else:
                print("❌ Invalid choice! Please enter 0-10.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
