#!/usr/bin/env python3
"""
Comprehensive Data Tracking System for Event Management
Tracks: Event creation, student registration, attendance, feedback
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import json

def get_db_connection():
    """Get database connection"""
    db_path = Path(__file__).parent.parent / "database" / "event_management_db.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def track_event_creation():
    """Track event creation data"""
    print("🎉 EVENT CREATION TRACKING")
    print("=" * 50)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all events with details
        cursor.execute("""
            SELECT 
                e.event_id,
                e.title,
                e.description,
                e.venue,
                e.start_time,
                e.end_time,
                e.capacity,
                e.semester,
                e.status,
                c.name as college_name,
                et.name as event_type,
                a.name as created_by_admin
            FROM Events e
            LEFT JOIN Colleges c ON e.college_id = c.college_id
            LEFT JOIN EventTypes et ON e.type_id = et.type_id
            LEFT JOIN Admins a ON e.created_by = a.admin_id
            ORDER BY e.event_id
        """)
        
        events = cursor.fetchall()
        
        if not events:
            print("❌ No events found in the database")
            return
        
        print(f"📊 Total Events: {len(events)}")
        print("\n📋 Event Details:")
        
        for event in events:
            print(f"\n🎯 Event ID: {event['event_id']}")
            print(f"   Title: {event['title']}")
            print(f"   College: {event['college_name']}")
            print(f"   Type: {event['event_type']}")
            print(f"   Venue: {event['venue']}")
            print(f"   Start: {event['start_time']}")
            print(f"   End: {event['end_time']}")
            print(f"   Capacity: {event['capacity']}")
            print(f"   Semester: {event['semester']}")
            print(f"   Status: {event['status']}")
            print(f"   Created by: {event['created_by_admin']}")
            
            # Get registration count for this event
            cursor.execute("""
                SELECT COUNT(*) as reg_count 
                FROM Registrations 
                WHERE event_id = ? AND status = 'registered'
            """, (event['event_id'],))
            reg_count = cursor.fetchone()['reg_count']
            print(f"   Registrations: {reg_count}/{event['capacity']}")
    
    except Exception as e:
        print(f"❌ Error tracking events: {e}")
    finally:
        conn.close()

def track_student_registrations():
    """Track student registration data"""
    print("\n\n📝 STUDENT REGISTRATION TRACKING")
    print("=" * 50)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all registrations with details
        cursor.execute("""
            SELECT 
                r.registration_id,
                r.registration_time,
                r.status,
                s.name as student_name,
                s.email as student_email,
                s.department,
                s.year,
                e.title as event_title,
                e.start_time as event_start,
                c.name as college_name
            FROM Registrations r
            LEFT JOIN Students s ON r.student_id = s.student_id
            LEFT JOIN Events e ON r.event_id = e.event_id
            LEFT JOIN Colleges c ON s.college_id = c.college_id
            ORDER BY r.registration_time DESC
        """)
        
        registrations = cursor.fetchall()
        
        if not registrations:
            print("❌ No registrations found in the database")
            return
        
        print(f"📊 Total Registrations: {len(registrations)}")
        
        # Group by status
        status_counts = {}
        for reg in registrations:
            status = reg['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n📈 Registration Status Summary:")
        for status, count in status_counts.items():
            print(f"   {status}: {count}")
        
        print(f"\n📋 Recent Registrations:")
        for reg in registrations[:10]:  # Show last 10
            print(f"\n🎫 Registration ID: {reg['registration_id']}")
            print(f"   Student: {reg['student_name']} ({reg['student_email']})")
            print(f"   Department: {reg['department']}, Year: {reg['year']}")
            print(f"   Event: {reg['event_title']}")
            print(f"   College: {reg['college_name']}")
            print(f"   Registered: {reg['registration_time']}")
            print(f"   Status: {reg['status']}")
    
    except Exception as e:
        print(f"❌ Error tracking registrations: {e}")
    finally:
        conn.close()

def track_attendance():
    """Track attendance data"""
    print("\n\n✅ ATTENDANCE TRACKING")
    print("=" * 50)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get attendance data with details
        cursor.execute("""
            SELECT 
                a.attendance_id,
                a.attended,
                a.check_in_time,
                r.registration_id,
                s.name as student_name,
                e.title as event_title,
                e.start_time as event_start
            FROM Attendance a
            LEFT JOIN Registrations r ON a.registration_id = r.registration_id
            LEFT JOIN Students s ON r.student_id = s.student_id
            LEFT JOIN Events e ON r.event_id = e.event_id
            ORDER BY a.check_in_time DESC
        """)
        
        attendance_records = cursor.fetchall()
        
        if not attendance_records:
            print("❌ No attendance records found in the database")
            return
        
        print(f"📊 Total Attendance Records: {len(attendance_records)}")
        
        # Calculate attendance statistics
        total_attended = sum(1 for record in attendance_records if record['attended'] == 1)
        total_registered = len(attendance_records)
        attendance_rate = (total_attended / total_registered * 100) if total_registered > 0 else 0
        
        print(f"\n📈 Attendance Statistics:")
        print(f"   Total Registered: {total_registered}")
        print(f"   Total Attended: {total_attended}")
        print(f"   Attendance Rate: {attendance_rate:.1f}%")
        
        print(f"\n📋 Attendance Records:")
        for record in attendance_records:
            status = "✅ Attended" if record['attended'] == 1 else "❌ Absent"
            print(f"\n🎯 Attendance ID: {record['attendance_id']}")
            print(f"   Student: {record['student_name']}")
            print(f"   Event: {record['event_title']}")
            print(f"   Status: {status}")
            if record['check_in_time']:
                print(f"   Check-in: {record['check_in_time']}")
    
    except Exception as e:
        print(f"❌ Error tracking attendance: {e}")
    finally:
        conn.close()

def track_feedback():
    """Track feedback data"""
    print("\n\n💬 FEEDBACK TRACKING")
    print("=" * 50)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get feedback data with details
        cursor.execute("""
            SELECT 
                f.feedback_id,
                f.rating,
                f.comments,
                f.submitted_at,
                s.name as student_name,
                e.title as event_title,
                c.name as college_name
            FROM Feedback f
            LEFT JOIN Registrations r ON f.registration_id = r.registration_id
            LEFT JOIN Students s ON r.student_id = s.student_id
            LEFT JOIN Events e ON r.event_id = e.event_id
            LEFT JOIN Colleges c ON s.college_id = c.college_id
            ORDER BY f.submitted_at DESC
        """)
        
        feedback_records = cursor.fetchall()
        
        if not feedback_records:
            print("❌ No feedback records found in the database")
            return
        
        print(f"📊 Total Feedback Records: {len(feedback_records)}")
        
        # Calculate feedback statistics
        ratings = [record['rating'] for record in feedback_records]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        rating_distribution = {}
        for rating in ratings:
            rating_distribution[rating] = rating_distribution.get(rating, 0) + 1
        
        print(f"\n📈 Feedback Statistics:")
        print(f"   Average Rating: {avg_rating:.1f}/5")
        print(f"   Rating Distribution:")
        for rating in sorted(rating_distribution.keys()):
            count = rating_distribution[rating]
            stars = "⭐" * rating
            print(f"     {rating} stars {stars}: {count} responses")
        
        print(f"\n📋 Recent Feedback:")
        for feedback in feedback_records[:10]:  # Show last 10
            stars = "⭐" * feedback['rating']
            print(f"\n💭 Feedback ID: {feedback['feedback_id']}")
            print(f"   Student: {feedback['student_name']}")
            print(f"   Event: {feedback['event_title']}")
            print(f"   College: {feedback['college_name']}")
            print(f"   Rating: {feedback['rating']} {stars}")
            print(f"   Comments: {feedback['comments']}")
            print(f"   Submitted: {feedback['submitted_at']}")
    
    except Exception as e:
        print(f"❌ Error tracking feedback: {e}")
    finally:
        conn.close()

def generate_summary_report():
    """Generate a comprehensive summary report"""
    print("\n\n📊 COMPREHENSIVE SUMMARY REPORT")
    print("=" * 60)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get overall statistics
        stats = {}
        
        # Count colleges
        cursor.execute("SELECT COUNT(*) as count FROM Colleges")
        stats['colleges'] = cursor.fetchone()['count']
        
        # Count students
        cursor.execute("SELECT COUNT(*) as count FROM Students")
        stats['students'] = cursor.fetchone()['count']
        
        # Count events
        cursor.execute("SELECT COUNT(*) as count FROM Events")
        stats['events'] = cursor.fetchone()['count']
        
        # Count registrations
        cursor.execute("SELECT COUNT(*) as count FROM Registrations")
        stats['registrations'] = cursor.fetchone()['count']
        
        # Count attendance
        cursor.execute("SELECT COUNT(*) as count FROM Attendance")
        stats['attendance_records'] = cursor.fetchone()['count']
        
        # Count feedback
        cursor.execute("SELECT COUNT(*) as count FROM Feedback")
        stats['feedback_records'] = cursor.fetchone()['count']
        
        # Calculate attendance rate
        cursor.execute("SELECT COUNT(*) as attended FROM Attendance WHERE attended = 1")
        attended = cursor.fetchone()['attended']
        attendance_rate = (attended / stats['attendance_records'] * 100) if stats['attendance_records'] > 0 else 0
        
        # Calculate average rating
        cursor.execute("SELECT AVG(rating) as avg_rating FROM Feedback")
        avg_rating = cursor.fetchone()['avg_rating'] or 0
        
        print(f"🏫 System Overview:")
        print(f"   Colleges: {stats['colleges']}")
        print(f"   Students: {stats['students']}")
        print(f"   Events: {stats['events']}")
        print(f"   Registrations: {stats['registrations']}")
        print(f"   Attendance Records: {stats['attendance_records']}")
        print(f"   Feedback Records: {stats['feedback_records']}")
        
        print(f"\n📈 Performance Metrics:")
        print(f"   Attendance Rate: {attendance_rate:.1f}%")
        print(f"   Average Rating: {avg_rating:.1f}/5")
        
        # Recent activity
        cursor.execute("""
            SELECT COUNT(*) as recent_events 
            FROM Events 
            WHERE start_time >= datetime('now', '-30 days')
        """)
        recent_events = cursor.fetchone()['recent_events']
        
        cursor.execute("""
            SELECT COUNT(*) as recent_registrations 
            FROM Registrations 
            WHERE registration_time >= datetime('now', '-7 days')
        """)
        recent_registrations = cursor.fetchone()['recent_registrations']
        
        print(f"\n📅 Recent Activity (Last 30 days):")
        print(f"   New Events: {recent_events}")
        print(f"   New Registrations (Last 7 days): {recent_registrations}")
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
    finally:
        conn.close()

def main():
    """Main tracking function"""
    print("🔍 EVENT MANAGEMENT SYSTEM - DATA TRACKING")
    print("=" * 70)
    print("Tracking: Event Creation, Student Registration, Attendance, Feedback")
    print("=" * 70)
    
    # Track each component
    track_event_creation()
    track_student_registrations()
    track_attendance()
    track_feedback()
    generate_summary_report()
    
    print("\n" + "=" * 70)
    print("✅ Data tracking completed!")
    print("💡 Use this information to monitor system performance and user engagement")

if __name__ == "__main__":
    main()
