#!/usr/bin/env python3
"""
Script to add sample data to the Event Management Database
Run this script to populate the database with sample data
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    db_path = Path(__file__).parent.parent / "database" / "event_management_db.db"
    
    if not db_path.exists():
        print(f"❌ Database file not found: {db_path}")
        return None
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def add_sample_data():
    """Add sample data to the database"""
    
    print("🚀 Adding Sample Data to Event Management Database")
    print("=" * 60)
    
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # 1. Add Sample Colleges
        print("📚 Adding Colleges...")
        colleges_data = [
            ("University of Technology", "New York", "active"),
            ("State College", "California", "active"),
            ("Tech Institute", "Texas", "active"),
            ("Community College", "Florida", "active")
        ]
        
        for college in colleges_data:
            cursor.execute("""
                INSERT INTO Colleges (name, location, status) 
                VALUES (?, ?, ?)
            """, college)
        
        print(f"   ✅ Added {len(colleges_data)} colleges")
        
        # 2. Add Sample Admins
        print("👨‍💼 Adding Admins...")
        admins_data = [
            (1, "John Smith", "john.smith@university.edu", "Event Coordinator", "active"),
            (2, "Sarah Johnson", "sarah.johnson@statecollege.edu", "Student Affairs", "active"),
            (3, "Mike Davis", "mike.davis@techinstitute.edu", "IT Manager", "active"),
            (4, "Lisa Brown", "lisa.brown@communitycollege.edu", "Activities Director", "active")
        ]
        
        for admin in admins_data:
            cursor.execute("""
                INSERT INTO Admins (college_id, name, email, role, status) 
                VALUES (?, ?, ?, ?, ?)
            """, admin)
        
        print(f"   ✅ Added {len(admins_data)} admins")
        
        # 3. Add Sample Students
        print("🎓 Adding Students...")
        students_data = [
            (1, "Alice Johnson", "alice.johnson@university.edu", "Computer Science", "2024", "active"),
            (1, "Bob Wilson", "bob.wilson@university.edu", "Engineering", "2023", "active"),
            (2, "Carol Davis", "carol.davis@statecollege.edu", "Business", "2024", "active"),
            (2, "David Miller", "david.miller@statecollege.edu", "Mathematics", "2023", "active"),
            (3, "Emma Garcia", "emma.garcia@techinstitute.edu", "Information Technology", "2024", "active"),
            (3, "Frank Rodriguez", "frank.rodriguez@techinstitute.edu", "Cybersecurity", "2023", "active"),
            (4, "Grace Lee", "grace.lee@communitycollege.edu", "Liberal Arts", "2024", "active"),
            (4, "Henry Chen", "henry.chen@communitycollege.edu", "Health Sciences", "2023", "active")
        ]
        
        for student in students_data:
            cursor.execute("""
                INSERT INTO Students (college_id, name, email, department, year, status) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, student)
        
        print(f"   ✅ Added {len(students_data)} students")
        
        # 4. Add Sample Events
        print("🎉 Adding Events...")
        events_data = [
            (1, "Python Programming Workshop", "Learn Python basics and advanced concepts", 1, "Room 101", "2024-02-15 09:00:00", "2024-02-15 17:00:00", 50, 1, "Spring 2024", "active"),
            (1, "Web Development Bootcamp", "Full-stack web development intensive", 2, "Computer Lab A", "2024-02-20 10:00:00", "2024-02-22 18:00:00", 30, 1, "Spring 2024", "active"),
            (2, "Data Science Conference", "Latest trends in data science and AI", 3, "Main Auditorium", "2024-03-01 08:00:00", "2024-03-01 20:00:00", 200, 2, "Spring 2024", "active"),
            (3, "Cybersecurity Workshop", "Security best practices and ethical hacking", 1, "Security Lab", "2024-03-10 14:00:00", "2024-03-10 18:00:00", 25, 3, "Spring 2024", "active"),
            (4, "Career Fair 2024", "Meet employers and explore career opportunities", 3, "Gymnasium", "2024-03-15 09:00:00", "2024-03-15 16:00:00", 500, 4, "Spring 2024", "active")
        ]
        
        for event in events_data:
            cursor.execute("""
                INSERT INTO Events (college_id, title, description, type_id, venue, start_time, end_time, capacity, created_by, semester, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, event)
        
        print(f"   ✅ Added {len(events_data)} events")
        
        # 5. Add Sample Registrations
        print("📝 Adding Registrations...")
        registrations_data = [
            (1, 1, "registered"),
            (2, 1, "registered"),
            (3, 2, "registered"),
            (4, 2, "registered"),
            (5, 3, "registered"),
            (6, 3, "registered"),
            (7, 4, "registered"),
            (8, 4, "registered"),
            (1, 5, "registered"),
            (2, 5, "registered"),
            (3, 5, "registered"),
            (4, 5, "registered")
        ]
        
        for registration in registrations_data:
            try:
                cursor.execute("""
                    INSERT INTO Registrations (student_id, event_id, status) 
                    VALUES (?, ?, ?)
                """, registration)
            except Exception as e:
                print(f"   ⚠️  Registration {registration} failed: {e}")
                continue
        
        print(f"   ✅ Added {len(registrations_data)} registrations")
        
        # 6. Add Sample Attendance
        print("✅ Adding Attendance Records...")
        attendance_data = [
            (1, 1, "2024-02-15 09:15:00"),
            (2, 1, "2024-02-15 09:20:00"),
            (3, 2, "2024-02-20 10:05:00"),
            (4, 2, "2024-02-20 10:10:00"),
            (5, 3, "2024-03-01 08:30:00"),
            (6, 3, "2024-03-01 08:45:00"),
            (7, 4, "2024-03-10 14:15:00"),
            (8, 4, "2024-03-10 14:20:00")
        ]
        
        attendance_count = 0
        for attendance in attendance_data:
            try:
                cursor.execute("""
                    INSERT INTO Attendance (registration_id, attended, check_in_time) 
                    VALUES (?, ?, ?)
                """, attendance)
                attendance_count += 1
            except Exception as e:
                print(f"   ⚠️  Attendance {attendance} failed: {e}")
                continue
        
        print(f"   ✅ Added {attendance_count} attendance records")
        
        # 7. Add Sample Feedback
        print("💬 Adding Feedback...")
        feedback_data = [
            (1, 5, "Excellent workshop! Very informative and well-structured."),
            (2, 4, "Good content but could use more hands-on exercises."),
            (3, 5, "Amazing bootcamp! Learned so much in just 3 days."),
            (4, 4, "Great instructors and practical examples."),
            (5, 5, "Outstanding conference with top-notch speakers."),
            (6, 5, "Very insightful presentations on AI and ML."),
            (7, 4, "Good workshop on cybersecurity fundamentals."),
            (8, 5, "Excellent practical demonstrations and real-world examples.")
        ]
        
        feedback_count = 0
        for feedback in feedback_data:
            try:
                cursor.execute("""
                    INSERT INTO Feedback (registration_id, rating, comments) 
                    VALUES (?, ?, ?)
                """, feedback)
                feedback_count += 1
            except Exception as e:
                print(f"   ⚠️  Feedback {feedback} failed: {e}")
                continue
        
        print(f"   ✅ Added {feedback_count} feedback records")
        
        # Commit all changes
        conn.commit()
        
        print("\n" + "=" * 60)
        print("🎉 Sample Data Successfully Added!")
        print("=" * 60)
        
        # Show summary
        cursor.execute("SELECT COUNT(*) as count FROM Colleges")
        colleges_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Admins")
        admins_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Students")
        students_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Events")
        events_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Registrations")
        registrations_count = cursor.fetchone()['count']
        
        print(f"📊 Database Summary:")
        print(f"   - Colleges: {colleges_count}")
        print(f"   - Admins: {admins_count}")
        print(f"   - Students: {students_count}")
        print(f"   - Events: {events_count}")
        print(f"   - Registrations: {registrations_count}")
        print(f"   - Event Types: 6 (already existed)")
        
        print(f"\n🌐 Your API is ready at: http://localhost:8000")
        print(f"📖 API Documentation: http://localhost:8000/docs")
        print(f"❤️  Health Check: http://localhost:8000/health")
        
    except Exception as e:
        print(f"❌ Error adding data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_sample_data()
