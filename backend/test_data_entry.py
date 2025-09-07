#!/usr/bin/env python3
"""
Comprehensive Data Entry Testing Script.
Tests adding data to all tables with proper validation and error handling.
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from config import settings


class DataEntryTester:
    """Comprehensive data entry testing system."""
    
    def __init__(self):
        self.db_path = Path(settings.database_path)
        self.conn = None
        self.test_results = []
        self.data_added = []
    
    def connect_db(self):
        """Connect to database."""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def close_db(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def log_result(self, operation: str, status: str, details: str = "", data_id: Any = None):
        """Log test results."""
        result = {
            "operation": operation,
            "status": status,
            "details": details,
            "data_id": data_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "⚠️"
        print(f"{status_emoji} {operation}: {status}")
        if details:
            print(f"   Details: {details}")
        if data_id:
            print(f"   ID: {data_id}")
    
    def test_college_creation(self):
        """Test creating colleges."""
        print("\n🏫 Testing College Creation...")
        
        cursor = self.conn.cursor()
        
        colleges = [
            ("Test University", "Test City", "test@university.edu"),
            ("Demo College", "Demo Town", "demo@college.edu"),
            ("Sample Institute", "Sample City", "sample@institute.edu")
        ]
        
        for name, location, email in colleges:
            try:
                cursor.execute("""
                    INSERT INTO Colleges (name, location, contact_email, status)
                    VALUES (?, ?, ?, 'active')
                """, (name, location, email))
                
                college_id = cursor.lastrowid
                self.log_result("Create College", "SUCCESS", f"Created: {name}", college_id)
                self.data_added.append(("Colleges", college_id, name))
                
            except sqlite3.IntegrityError as e:
                self.log_result("Create College", "FAILED", f"Integrity error: {e}")
            except Exception as e:
                self.log_result("Create College", "FAILED", f"Error: {e}")
        
        self.conn.commit()
    
    def test_admin_creation(self):
        """Test creating admins."""
        print("\n👨‍💼 Testing Admin Creation...")
        
        cursor = self.conn.cursor()
        
        # Get college IDs
        cursor.execute("SELECT college_id FROM Colleges LIMIT 3")
        colleges = cursor.fetchall()
        
        if not colleges:
            self.log_result("Create Admin", "SKIPPED", "No colleges available")
            return
        
        admins = [
            ("John Admin", "john.admin@test.com", "Event Coordinator"),
            ("Jane Manager", "jane.manager@test.com", "Student Affairs"),
            ("Bob Director", "bob.director@test.com", "IT Manager")
        ]
        
        for i, (name, email, role) in enumerate(admins):
            college_id = colleges[i % len(colleges)]['college_id']
            
            try:
                cursor.execute("""
                    INSERT INTO Admins (college_id, name, email, role, status)
                    VALUES (?, ?, ?, ?, 'active')
                """, (college_id, name, email, role))
                
                admin_id = cursor.lastrowid
                self.log_result("Create Admin", "SUCCESS", f"Created: {name}", admin_id)
                self.data_added.append(("Admins", admin_id, name))
                
            except sqlite3.IntegrityError as e:
                self.log_result("Create Admin", "FAILED", f"Integrity error: {e}")
            except Exception as e:
                self.log_result("Create Admin", "FAILED", f"Error: {e}")
        
        self.conn.commit()
    
    def test_student_creation(self):
        """Test creating students."""
        print("\n🎓 Testing Student Creation...")
        
        cursor = self.conn.cursor()
        
        # Get college IDs
        cursor.execute("SELECT college_id FROM Colleges LIMIT 3")
        colleges = cursor.fetchall()
        
        if not colleges:
            self.log_result("Create Student", "SKIPPED", "No colleges available")
            return
        
        students = [
            ("Alice Johnson", "alice.johnson@test.com", "2024", "Computer Science"),
            ("Bob Smith", "bob.smith@test.com", "2023", "Engineering"),
            ("Carol Davis", "carol.davis@test.com", "2024", "Business"),
            ("David Wilson", "david.wilson@test.com", "2025", "Mathematics"),
            ("Eva Brown", "eva.brown@test.com", "2023", "Physics")
        ]
        
        for i, (name, email, year, department) in enumerate(students):
            college_id = colleges[i % len(colleges)]['college_id']
            
            try:
                cursor.execute("""
                    INSERT INTO Students (college_id, name, email, year, department, status)
                    VALUES (?, ?, ?, ?, ?, 'active')
                """, (college_id, name, email, year, department))
                
                student_id = cursor.lastrowid
                self.log_result("Create Student", "SUCCESS", f"Created: {name}", student_id)
                self.data_added.append(("Students", student_id, name))
                
            except sqlite3.IntegrityError as e:
                self.log_result("Create Student", "FAILED", f"Integrity error: {e}")
            except Exception as e:
                self.log_result("Create Student", "FAILED", f"Error: {e}")
        
        self.conn.commit()
    
    def test_event_type_creation(self):
        """Test creating event types."""
        print("\n📋 Testing Event Type Creation...")
        
        cursor = self.conn.cursor()
        
        event_types = [
            ("Workshop", "Hands-on learning sessions"),
            ("Seminar", "Educational presentations"),
            ("Conference", "Large-scale professional gatherings"),
            ("Hackathon", "Coding competitions"),
            ("Networking", "Professional networking events")
        ]
        
        for name, description in event_types:
            try:
                cursor.execute("""
                    INSERT INTO EventTypes (name, description)
                    VALUES (?, ?)
                """, (name, description))
                
                type_id = cursor.lastrowid
                self.log_result("Create Event Type", "SUCCESS", f"Created: {name}", type_id)
                self.data_added.append(("EventTypes", type_id, name))
                
            except sqlite3.IntegrityError as e:
                self.log_result("Create Event Type", "FAILED", f"Integrity error: {e}")
            except Exception as e:
                self.log_result("Create Event Type", "FAILED", f"Error: {e}")
        
        self.conn.commit()
    
    def test_event_creation(self):
        """Test creating events."""
        print("\n🎉 Testing Event Creation...")
        
        cursor = self.conn.cursor()
        
        # Get required IDs
        cursor.execute("SELECT college_id FROM Colleges LIMIT 1")
        college = cursor.fetchone()
        if not college:
            self.log_result("Create Event", "SKIPPED", "No colleges available")
            return
        
        cursor.execute("SELECT admin_id FROM Admins LIMIT 1")
        admin = cursor.fetchone()
        if not admin:
            self.log_result("Create Event", "SKIPPED", "No admins available")
            return
        
        cursor.execute("SELECT type_id FROM EventTypes LIMIT 3")
        event_types = cursor.fetchall()
        if not event_types:
            self.log_result("Create Event", "SKIPPED", "No event types available")
            return
        
        college_id = college['college_id']
        admin_id = admin['admin_id']
        
        now = datetime.now()
        
        events = [
            {
                "title": "Python Programming Workshop",
                "description": "Learn Python basics and advanced concepts",
                "venue": "Computer Lab A",
                "start_time": now + timedelta(days=7, hours=9),
                "end_time": now + timedelta(days=7, hours=17),
                "capacity": 30,
                "type_id": event_types[0]['type_id']
            },
            {
                "title": "Web Development Bootcamp",
                "description": "Full-stack web development intensive",
                "venue": "Main Auditorium",
                "start_time": now + timedelta(days=14, hours=10),
                "end_time": now + timedelta(days=16, hours=18),
                "capacity": 50,
                "type_id": event_types[1]['type_id']
            },
            {
                "title": "Data Science Conference",
                "description": "Latest trends in data science and AI",
                "venue": "Conference Center",
                "start_time": now + timedelta(days=21, hours=8),
                "end_time": now + timedelta(days=21, hours=20),
                "capacity": 100,
                "type_id": event_types[2]['type_id']
            }
        ]
        
        for event_data in events:
            try:
                cursor.execute("""
                    INSERT INTO Events (title, description, venue, start_time, end_time, 
                                     capacity, status, college_id, type_id, created_by, semester)
                    VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, 'Fall 2024')
                """, (
                    event_data['title'],
                    event_data['description'],
                    event_data['venue'],
                    event_data['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
                    event_data['end_time'].strftime("%Y-%m-%d %H:%M:%S"),
                    event_data['capacity'],
                    college_id,
                    event_data['type_id'],
                    admin_id
                ))
                
                event_id = cursor.lastrowid
                self.log_result("Create Event", "SUCCESS", f"Created: {event_data['title']}", event_id)
                self.data_added.append(("Events", event_id, event_data['title']))
                
            except sqlite3.IntegrityError as e:
                self.log_result("Create Event", "FAILED", f"Integrity error: {e}")
            except Exception as e:
                self.log_result("Create Event", "FAILED", f"Error: {e}")
        
        self.conn.commit()
    
    def test_registration_creation(self):
        """Test creating registrations."""
        print("\n📝 Testing Registration Creation...")
        
        cursor = self.conn.cursor()
        
        # Get students and events
        cursor.execute("SELECT student_id FROM Students LIMIT 5")
        students = cursor.fetchall()
        
        cursor.execute("SELECT event_id FROM Events WHERE status = 'active' LIMIT 3")
        events = cursor.fetchall()
        
        if not students or not events:
            self.log_result("Create Registration", "SKIPPED", "No students or events available")
            return
        
        # Create registrations
        registrations_created = 0
        
        for i, student in enumerate(students):
            event = events[i % len(events)]
            
            try:
                cursor.execute("""
                    INSERT INTO Registrations (student_id, event_id, status, registration_time)
                    VALUES (?, ?, 'registered', datetime('now'))
                """, (student['student_id'], event['event_id']))
                
                registration_id = cursor.lastrowid
                registrations_created += 1
                self.log_result("Create Registration", "SUCCESS", 
                              f"Student {student['student_id']} -> Event {event['event_id']}", 
                              registration_id)
                self.data_added.append(("Registrations", registration_id, f"Student {student['student_id']}"))
                
            except sqlite3.IntegrityError as e:
                self.log_result("Create Registration", "FAILED", f"Integrity error: {e}")
            except Exception as e:
                self.log_result("Create Registration", "FAILED", f"Error: {e}")
        
        self.conn.commit()
        print(f"   📊 Created {registrations_created} registrations")
    
    def test_attendance_creation(self):
        """Test creating attendance records."""
        print("\n✅ Testing Attendance Creation...")
        
        cursor = self.conn.cursor()
        
        # Get registrations
        cursor.execute("SELECT registration_id FROM Registrations LIMIT 3")
        registrations = cursor.fetchall()
        
        if not registrations:
            self.log_result("Create Attendance", "SKIPPED", "No registrations available")
            return
        
        attendance_created = 0
        
        for registration in registrations:
            try:
                cursor.execute("""
                    INSERT INTO Attendance (registration_id, attended, check_in_time)
                    VALUES (?, 1, datetime('now'))
                """, (registration['registration_id'],))
                
                attendance_id = cursor.lastrowid
                attendance_created += 1
                self.log_result("Create Attendance", "SUCCESS", 
                              f"Registration {registration['registration_id']} attended", 
                              attendance_id)
                self.data_added.append(("Attendance", attendance_id, f"Registration {registration['registration_id']}"))
                
            except sqlite3.IntegrityError as e:
                self.log_result("Create Attendance", "FAILED", f"Integrity error: {e}")
            except Exception as e:
                self.log_result("Create Attendance", "FAILED", f"Error: {e}")
        
        self.conn.commit()
        print(f"   📊 Created {attendance_created} attendance records")
    
    def test_feedback_creation(self):
        """Test creating feedback records."""
        print("\n💬 Testing Feedback Creation...")
        
        cursor = self.conn.cursor()
        
        # Get registrations with attendance
        cursor.execute("""
            SELECT r.registration_id
            FROM Registrations r
            JOIN Attendance a ON r.registration_id = a.registration_id
            WHERE a.attended = 1
            LIMIT 3
        """)
        registrations = cursor.fetchall()
        
        if not registrations:
            self.log_result("Create Feedback", "SKIPPED", "No attended registrations available")
            return
        
        feedback_created = 0
        
        for registration in registrations:
            try:
                cursor.execute("""
                    INSERT INTO Feedback (registration_id, rating, comments, submitted_at)
                    VALUES (?, ?, ?, datetime('now'))
                """, (registration['registration_id'], 5, "Great event! Very informative."))
                
                feedback_id = cursor.lastrowid
                feedback_created += 1
                self.log_result("Create Feedback", "SUCCESS", 
                              f"Registration {registration['registration_id']} feedback", 
                              feedback_id)
                self.data_added.append(("Feedback", feedback_id, f"Registration {registration['registration_id']}"))
                
            except sqlite3.IntegrityError as e:
                self.log_result("Create Feedback", "FAILED", f"Integrity error: {e}")
            except Exception as e:
                self.log_result("Create Feedback", "FAILED", f"Error: {e}")
        
        self.conn.commit()
        print(f"   📊 Created {feedback_created} feedback records")
    
    def test_error_scenarios(self):
        """Test various error scenarios."""
        print("\n🚨 Testing Error Scenarios...")
        
        cursor = self.conn.cursor()
        
        # Test 1: Duplicate registration
        cursor.execute("SELECT student_id, event_id FROM Registrations LIMIT 1")
        registration = cursor.fetchone()
        
        if registration:
            try:
                cursor.execute("""
                    INSERT INTO Registrations (student_id, event_id, status, registration_time)
                    VALUES (?, ?, 'registered', datetime('now'))
                """, (registration['student_id'], registration['event_id']))
                
                self.log_result("Duplicate Registration Test", "FAILED", "System allowed duplicate registration")
                self.conn.rollback()
            except sqlite3.IntegrityError:
                self.log_result("Duplicate Registration Test", "SUCCESS", "System correctly prevented duplicate")
                self.conn.rollback()
        
        # Test 2: Invalid feedback rating
        cursor.execute("SELECT registration_id FROM Registrations LIMIT 1")
        registration = cursor.fetchone()
        
        if registration:
            try:
                cursor.execute("""
                    INSERT INTO Feedback (registration_id, rating, comments, submitted_at)
                    VALUES (?, 6, 'Invalid rating test', datetime('now'))
                """, (registration['registration_id'],))
                
                self.log_result("Invalid Rating Test", "FAILED", "System allowed invalid rating")
                self.conn.rollback()
            except sqlite3.IntegrityError:
                self.log_result("Invalid Rating Test", "SUCCESS", "System correctly prevented invalid rating")
                self.conn.rollback()
        
        # Test 3: Negative capacity
        try:
            cursor.execute("""
                INSERT INTO Events (title, description, start_time, end_time, capacity, 
                                 status, college_id, type_id, created_by, semester)
                VALUES ('Invalid Event', 'Test', datetime('now', '+1 hour'), 
                        datetime('now', '+2 hours'), -5, 'active', 1, 1, 1, 'Fall 2024')
            """)
            
            self.log_result("Negative Capacity Test", "FAILED", "System allowed negative capacity")
            self.conn.rollback()
        except sqlite3.IntegrityError:
            self.log_result("Negative Capacity Test", "SUCCESS", "System correctly prevented negative capacity")
            self.conn.rollback()
    
    def generate_summary_report(self):
        """Generate comprehensive summary report."""
        print("\n" + "=" * 80)
        print("📊 DATA ENTRY TESTING SUMMARY REPORT")
        print("=" * 80)
        
        # Count results by status
        success_count = len([r for r in self.test_results if r['status'] == 'SUCCESS'])
        failed_count = len([r for r in self.test_results if r['status'] == 'FAILED'])
        skipped_count = len([r for r in self.test_results if r['status'] == 'SKIPPED'])
        
        print(f"📈 Test Summary:")
        print(f"   Total Operations: {len(self.test_results)}")
        print(f"   ✅ Successful: {success_count}")
        print(f"   ❌ Failed: {failed_count}")
        print(f"   ⚠️  Skipped: {skipped_count}")
        
        success_rate = (success_count / len(self.test_results) * 100) if self.test_results else 0
        print(f"   📊 Success Rate: {success_rate:.1f}%")
        
        # Data added summary
        print(f"\n📊 Data Added Summary:")
        data_by_table = {}
        for table, id_val, name in self.data_added:
            if table not in data_by_table:
                data_by_table[table] = 0
            data_by_table[table] += 1
        
        for table, count in data_by_table.items():
            print(f"   • {table}: {count} records")
        
        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            status_emoji = "✅" if result['status'] == "SUCCESS" else "❌" if result['status'] == "FAILED" else "⚠️"
            print(f"   {status_emoji} {result['operation']}: {result['status']}")
            if result['details']:
                print(f"      {result['details']}")
        
        # Overall assessment
        if failed_count == 0:
            print(f"\n🎉 Overall Assessment: EXCELLENT - All operations successful!")
        elif failed_count <= 2:
            print(f"\n✅ Overall Assessment: GOOD - Most operations successful")
        else:
            print(f"\n⚠️  Overall Assessment: NEEDS ATTENTION - Multiple operations failed")
        
        return {
            "total_operations": len(self.test_results),
            "successful": success_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "success_rate": success_rate,
            "data_added": len(self.data_added)
        }
    
    def run_comprehensive_test(self):
        """Run comprehensive data entry testing."""
        print("🧪 STARTING COMPREHENSIVE DATA ENTRY TESTING")
        print("=" * 80)
        
        if not self.connect_db():
            return None
        
        try:
            # Run all data entry tests
            self.test_college_creation()
            self.test_admin_creation()
            self.test_student_creation()
            self.test_event_type_creation()
            self.test_event_creation()
            self.test_registration_creation()
            self.test_attendance_creation()
            self.test_feedback_creation()
            
            # Test error scenarios
            self.test_error_scenarios()
            
            # Generate report
            return self.generate_summary_report()
            
        finally:
            self.close_db()


def main():
    """Main function to run data entry testing."""
    tester = DataEntryTester()
    result = tester.run_comprehensive_test()
    
    if result:
        if result['failed'] == 0:
            print(f"\n🎉 Data entry testing completed successfully!")
            print(f"📊 Added {result['data_added']} records across all tables")
            return 0
        elif result['failed'] <= 2:
            print(f"\n✅ Data entry testing mostly successful!")
            print(f"📊 Added {result['data_added']} records across all tables")
            return 0
        else:
            print(f"\n⚠️  Data entry testing needs attention.")
            return 1
    else:
        print(f"\n❌ Testing failed - check database connection.")
        return 1


if __name__ == "__main__":
    exit(main())
