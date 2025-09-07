#!/usr/bin/env python3
"""
Comprehensive Error Scenario Testing System.
Tests various error conditions and validates system resilience.
"""
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

from config import settings


class ErrorScenarioTester:
    """Test various error scenarios and system resilience."""
    
    def __init__(self):
        self.db_path = Path(settings.database_path)
        self.conn = None
        self.test_results = []
        self.scenarios_tested = 0
        self.scenarios_passed = 0
        self.scenarios_failed = 0
    
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
    
    def log_test_result(self, scenario: str, status: str, details: str = ""):
        """Log test scenario results."""
        result = {
            "scenario": scenario,
            "status": status,
            "details": details,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        self.scenarios_tested += 1
        
        if status == "PASS":
            self.scenarios_passed += 1
            print(f"✅ {scenario}: PASSED")
        else:
            self.scenarios_failed += 1
            print(f"❌ {scenario}: FAILED - {details}")
    
    def test_duplicate_registration_scenario(self):
        """Test duplicate registration prevention."""
        print("\n🧪 Testing Duplicate Registration Scenario...")
        
        cursor = self.conn.cursor()
        
        try:
            # Get a valid student and event
            cursor.execute("SELECT student_id FROM Students LIMIT 1")
            student = cursor.fetchone()
            cursor.execute("SELECT event_id FROM Events WHERE status = 'active' LIMIT 1")
            event = cursor.fetchone()
            
            if not student or not event:
                self.log_test_result("Duplicate Registration", "SKIP", "No valid student/event found")
                return
            
            # First registration (should succeed)
            cursor.execute("""
                INSERT INTO Registrations (student_id, event_id, status, registration_time)
                VALUES (?, ?, 'registered', datetime('now'))
            """, (student['student_id'], event['event_id']))
            
            # Second registration (should fail)
            try:
                cursor.execute("""
                    INSERT INTO Registrations (student_id, event_id, status, registration_time)
                    VALUES (?, ?, 'registered', datetime('now'))
                """, (student['student_id'], event['event_id']))
                
                self.log_test_result("Duplicate Registration", "FAIL", "System allowed duplicate registration")
                self.conn.rollback()
            except sqlite3.IntegrityError:
                self.log_test_result("Duplicate Registration", "PASS", "System correctly prevented duplicate")
                self.conn.rollback()
                
        except Exception as e:
            self.log_test_result("Duplicate Registration", "ERROR", f"Test failed: {e}")
            self.conn.rollback()
    
    def test_capacity_violation_scenario(self):
        """Test event capacity violation prevention."""
        print("\n🧪 Testing Capacity Violation Scenario...")
        
        cursor = self.conn.cursor()
        
        try:
            # Create a test event with capacity 1
            cursor.execute("""
                INSERT INTO Events (title, description, start_time, end_time, capacity, status, college_id, type_id, created_by, semester)
                VALUES ('Test Capacity Event', 'Test event', datetime('now', '+1 hour'), 
                        datetime('now', '+2 hours'), 1, 'active', 1, 1, 1, 'Fall 2024')
            """)
            event_id = cursor.lastrowid
            
            # Get a student
            cursor.execute("SELECT student_id FROM Students LIMIT 1")
            student = cursor.fetchone()
            
            if not student:
                self.log_test_result("Capacity Violation", "SKIP", "No valid student found")
                return
            
            # First registration (should succeed)
            cursor.execute("""
                INSERT INTO Registrations (student_id, event_id, status, registration_time)
                VALUES (?, ?, 'registered', datetime('now'))
            """, (student['student_id'], event_id))
            
            # Second registration (should be prevented by trigger)
            try:
                cursor.execute("SELECT student_id FROM Students WHERE student_id != ? LIMIT 1", (student['student_id'],))
                student2 = cursor.fetchone()
                
                if student2:
                    cursor.execute("""
                        INSERT INTO Registrations (student_id, event_id, status, registration_time)
                        VALUES (?, ?, 'registered', datetime('now'))
                    """, (student2['student_id'], event_id))
                    
                    self.log_test_result("Capacity Violation", "FAIL", "System allowed capacity violation")
                    self.conn.rollback()
                else:
                    self.log_test_result("Capacity Violation", "SKIP", "Only one student available")
                    self.conn.rollback()
                    
            except sqlite3.IntegrityError:
                self.log_test_result("Capacity Violation", "PASS", "System correctly prevented capacity violation")
                self.conn.rollback()
                
        except Exception as e:
            self.log_test_result("Capacity Violation", "ERROR", f"Test failed: {e}")
            self.conn.rollback()
    
    def test_invalid_feedback_scenario(self):
        """Test invalid feedback prevention."""
        print("\n🧪 Testing Invalid Feedback Scenario...")
        
        cursor = self.conn.cursor()
        
        try:
            # Get a registration
            cursor.execute("""
                SELECT r.registration_id, r.student_id, r.event_id
                FROM Registrations r
                LIMIT 1
            """)
            registration = cursor.fetchone()
            
            if not registration:
                self.log_test_result("Invalid Feedback", "SKIP", "No registration found")
                return
            
            # Try to add feedback with invalid rating (should fail)
            try:
                cursor.execute("""
                    INSERT INTO Feedback (registration_id, rating, comments, submitted_at)
                    VALUES (?, 6, 'Test feedback', datetime('now'))
                """, (registration['registration_id'],))
                
                self.log_test_result("Invalid Feedback Rating", "FAIL", "System allowed invalid rating")
                self.conn.rollback()
            except sqlite3.IntegrityError:
                self.log_test_result("Invalid Feedback Rating", "PASS", "System correctly prevented invalid rating")
                self.conn.rollback()
                
        except Exception as e:
            self.log_test_result("Invalid Feedback", "ERROR", f"Test failed: {e}")
            self.conn.rollback()
    
    def test_feedback_without_attendance_scenario(self):
        """Test feedback without attendance prevention."""
        print("\n🧪 Testing Feedback Without Attendance Scenario...")
        
        cursor = self.conn.cursor()
        
        try:
            # Get a registration without attendance
            cursor.execute("""
                SELECT r.registration_id
                FROM Registrations r
                LEFT JOIN Attendance a ON r.registration_id = a.registration_id
                WHERE a.attendance_id IS NULL
                LIMIT 1
            """)
            registration = cursor.fetchone()
            
            if not registration:
                self.log_test_result("Feedback Without Attendance", "SKIP", "No registration without attendance found")
                return
            
            # Try to add feedback without attendance (should fail)
            try:
                cursor.execute("""
                    INSERT INTO Feedback (registration_id, rating, comments, submitted_at)
                    VALUES (?, 5, 'Test feedback', datetime('now'))
                """, (registration['registration_id'],))
                
                self.log_test_result("Feedback Without Attendance", "FAIL", "System allowed feedback without attendance")
                self.conn.rollback()
            except sqlite3.IntegrityError:
                self.log_test_result("Feedback Without Attendance", "PASS", "System correctly prevented feedback without attendance")
                self.conn.rollback()
                
        except Exception as e:
            self.log_test_result("Feedback Without Attendance", "ERROR", f"Test failed: {e}")
            self.conn.rollback()
    
    def test_invalid_event_times_scenario(self):
        """Test invalid event times prevention."""
        print("\n🧪 Testing Invalid Event Times Scenario...")
        
        cursor = self.conn.cursor()
        
        try:
            # Try to create event with end time before start time (should fail)
            try:
                cursor.execute("""
                    INSERT INTO Events (title, description, start_time, end_time, capacity, status, college_id, type_id, created_by, semester)
                    VALUES ('Test Invalid Times', 'Test event', datetime('now', '+2 hours'), 
                            datetime('now', '+1 hour'), 10, 'active', 1, 1, 1, 'Fall 2024')
                """)
                
                self.log_test_result("Invalid Event Times", "FAIL", "System allowed invalid event times")
                self.conn.rollback()
            except sqlite3.IntegrityError:
                self.log_test_result("Invalid Event Times", "PASS", "System correctly prevented invalid event times")
                self.conn.rollback()
                
        except Exception as e:
            self.log_test_result("Invalid Event Times", "ERROR", f"Test failed: {e}")
            self.conn.rollback()
    
    def test_negative_capacity_scenario(self):
        """Test negative capacity prevention."""
        print("\n🧪 Testing Negative Capacity Scenario...")
        
        cursor = self.conn.cursor()
        
        try:
            # Try to create event with negative capacity (should fail)
            try:
                cursor.execute("""
                    INSERT INTO Events (title, description, start_time, end_time, capacity, status, college_id, type_id, created_by, semester)
                    VALUES ('Test Negative Capacity', 'Test event', datetime('now', '+1 hour'), 
                            datetime('now', '+2 hours'), -5, 'active', 1, 1, 1, 'Fall 2024')
                """)
                
                self.log_test_result("Negative Capacity", "FAIL", "System allowed negative capacity")
                self.conn.rollback()
            except sqlite3.IntegrityError:
                self.log_test_result("Negative Capacity", "PASS", "System correctly prevented negative capacity")
                self.conn.rollback()
                
        except Exception as e:
            self.log_test_result("Negative Capacity", "ERROR", f"Test failed: {e}")
            self.conn.rollback()
    
    def test_duplicate_attendance_scenario(self):
        """Test duplicate attendance prevention."""
        print("\n🧪 Testing Duplicate Attendance Scenario...")
        
        cursor = self.conn.cursor()
        
        try:
            # Get a registration
            cursor.execute("SELECT registration_id FROM Registrations LIMIT 1")
            registration = cursor.fetchone()
            
            if not registration:
                self.log_test_result("Duplicate Attendance", "SKIP", "No registration found")
                return
            
            # First attendance (should succeed)
            cursor.execute("""
                INSERT INTO Attendance (registration_id, attended, check_in_time)
                VALUES (?, 1, datetime('now'))
            """, (registration['registration_id'],))
            
            # Second attendance (should fail)
            try:
                cursor.execute("""
                    INSERT INTO Attendance (registration_id, attended, check_in_time)
                    VALUES (?, 1, datetime('now'))
                """, (registration['registration_id'],))
                
                self.log_test_result("Duplicate Attendance", "FAIL", "System allowed duplicate attendance")
                self.conn.rollback()
            except sqlite3.IntegrityError:
                self.log_test_result("Duplicate Attendance", "PASS", "System correctly prevented duplicate attendance")
                self.conn.rollback()
                
        except Exception as e:
            self.log_test_result("Duplicate Attendance", "ERROR", f"Test failed: {e}")
            self.conn.rollback()
    
    def test_duplicate_feedback_scenario(self):
        """Test duplicate feedback prevention."""
        print("\n🧪 Testing Duplicate Feedback Scenario...")
        
        cursor = self.conn.cursor()
        
        try:
            # Get a registration with attendance
            cursor.execute("""
                SELECT r.registration_id
                FROM Registrations r
                JOIN Attendance a ON r.registration_id = a.registration_id
                WHERE a.attended = 1
                LIMIT 1
            """)
            registration = cursor.fetchone()
            
            if not registration:
                self.log_test_result("Duplicate Feedback", "SKIP", "No registration with attendance found")
                return
            
            # First feedback (should succeed)
            cursor.execute("""
                INSERT INTO Feedback (registration_id, rating, comments, submitted_at)
                VALUES (?, 5, 'Test feedback', datetime('now'))
            """, (registration['registration_id'],))
            
            # Second feedback (should fail)
            try:
                cursor.execute("""
                    INSERT INTO Feedback (registration_id, rating, comments, submitted_at)
                    VALUES (?, 4, 'Test feedback 2', datetime('now'))
                """, (registration['registration_id'],))
                
                self.log_test_result("Duplicate Feedback", "FAIL", "System allowed duplicate feedback")
                self.conn.rollback()
            except sqlite3.IntegrityError:
                self.log_test_result("Duplicate Feedback", "PASS", "System correctly prevented duplicate feedback")
                self.conn.rollback()
                
        except Exception as e:
            self.log_test_result("Duplicate Feedback", "ERROR", f"Test failed: {e}")
            self.conn.rollback()
    
    def test_late_registration_scenario(self):
        """Test late registration prevention."""
        print("\n🧪 Testing Late Registration Scenario...")
        
        cursor = self.conn.cursor()
        
        try:
            # Create a past event
            cursor.execute("""
                INSERT INTO Events (title, description, start_time, end_time, capacity, status, college_id, type_id, created_by, semester)
                VALUES ('Past Event', 'Test event', datetime('now', '-2 hours'), 
                        datetime('now', '-1 hour'), 10, 'completed', 1, 1, 1, 'Fall 2024')
            """)
            event_id = cursor.lastrowid
            
            # Get a student
            cursor.execute("SELECT student_id FROM Students LIMIT 1")
            student = cursor.fetchone()
            
            if not student:
                self.log_test_result("Late Registration", "SKIP", "No valid student found")
                return
            
            # Try to register for past event (should be prevented by trigger)
            try:
                cursor.execute("""
                    INSERT INTO Registrations (student_id, event_id, status, registration_time)
                    VALUES (?, ?, 'registered', datetime('now'))
                """, (student['student_id'], event_id))
                
                self.log_test_result("Late Registration", "FAIL", "System allowed late registration")
                self.conn.rollback()
            except sqlite3.IntegrityError:
                self.log_test_result("Late Registration", "PASS", "System correctly prevented late registration")
                self.conn.rollback()
                
        except Exception as e:
            self.log_test_result("Late Registration", "ERROR", f"Test failed: {e}")
            self.conn.rollback()
    
    def run_all_scenarios(self):
        """Run all error scenario tests."""
        print("🧪 STARTING COMPREHENSIVE ERROR SCENARIO TESTING")
        print("=" * 80)
        
        if not self.connect_db():
            return None
        
        try:
            # Run all test scenarios
            self.test_duplicate_registration_scenario()
            self.test_capacity_violation_scenario()
            self.test_invalid_feedback_scenario()
            self.test_feedback_without_attendance_scenario()
            self.test_invalid_event_times_scenario()
            self.test_negative_capacity_scenario()
            self.test_duplicate_attendance_scenario()
            self.test_duplicate_feedback_scenario()
            self.test_late_registration_scenario()
            
            # Generate test report
            return self.generate_test_report()
            
        finally:
            self.close_db()
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 80)
        print("📊 ERROR SCENARIO TESTING REPORT")
        print("=" * 80)
        
        print(f"📈 Test Summary:")
        print(f"   Total Scenarios: {self.scenarios_tested}")
        print(f"   ✅ Passed: {self.scenarios_passed}")
        print(f"   ❌ Failed: {self.scenarios_failed}")
        print(f"   ⚠️  Skipped: {self.scenarios_tested - self.scenarios_passed - self.scenarios_failed}")
        
        success_rate = (self.scenarios_passed / self.scenarios_tested * 100) if self.scenarios_tested > 0 else 0
        print(f"   📊 Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            status_emoji = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️"
            print(f"   {status_emoji} {result['scenario']}: {result['status']}")
            if result['details']:
                print(f"      {result['details']}")
        
        # Overall assessment
        if self.scenarios_failed == 0:
            print(f"\n🎉 Overall Assessment: EXCELLENT - All error scenarios handled correctly!")
        elif self.scenarios_failed <= 2:
            print(f"\n✅ Overall Assessment: GOOD - Most error scenarios handled correctly")
        else:
            print(f"\n⚠️  Overall Assessment: NEEDS ATTENTION - Multiple error scenarios failed")
        
        return {
            "total_scenarios": self.scenarios_tested,
            "passed": self.scenarios_passed,
            "failed": self.scenarios_failed,
            "success_rate": success_rate
        }


def main():
    """Main function to run error scenario testing."""
    tester = ErrorScenarioTester()
    result = tester.run_all_scenarios()
    
    if result:
        if result['failed'] == 0:
            print(f"\n🎉 System is highly resilient to errors!")
            return 0
        elif result['failed'] <= 2:
            print(f"\n✅ System handles most error scenarios correctly!")
            return 0
        else:
            print(f"\n⚠️  System needs improvement in error handling.")
            return 1
    else:
        print(f"\n❌ Testing failed - check database connection.")
        return 1


if __name__ == "__main__":
    exit(main())
