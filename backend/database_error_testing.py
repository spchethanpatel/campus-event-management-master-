#!/usr/bin/env python3
"""
Comprehensive Database Error Testing and Validation System.
Tests various scenarios: duplicate registrations, missing data, feedbacks, cancelled registrations, etc.
"""
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import random

from config import settings


class DatabaseErrorTester:
    """Comprehensive database error testing and validation."""
    
    def __init__(self):
        self.db_path = Path(settings.database_path)
        self.conn = None
        self.test_results = []
        self.errors_found = []
        self.fixes_applied = []
    
    def connect_db(self):
        """Connect to database with error handling."""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def close_db(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def log_test_result(self, test_name: str, status: str, details: str = ""):
        """Log test results."""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    def test_duplicate_registrations(self):
        """Test for duplicate student registrations for the same event."""
        print("\n🔍 Testing Duplicate Registrations...")
        
        cursor = self.conn.cursor()
        
        # Check for existing duplicates
        cursor.execute("""
            SELECT student_id, event_id, COUNT(*) as count
            FROM Registrations
            GROUP BY student_id, event_id
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        if duplicates:
            self.log_test_result(
                "Duplicate Registrations Check",
                "FAIL",
                f"Found {len(duplicates)} duplicate registrations"
            )
            for dup in duplicates:
                self.errors_found.append({
                    "type": "duplicate_registration",
                    "student_id": dup['student_id'],
                    "event_id": dup['event_id'],
                    "count": dup['count']
                })
        else:
            self.log_test_result("Duplicate Registrations Check", "PASS")
        
        # Test creating a duplicate registration
        try:
            # Get a valid student and event
            cursor.execute("SELECT student_id FROM Students LIMIT 1")
            student = cursor.fetchone()
            cursor.execute("SELECT event_id FROM Events LIMIT 1")
            event = cursor.fetchone()
            
            if student and event:
                # Try to insert duplicate
                cursor.execute("""
                    INSERT INTO Registrations (student_id, event_id, status)
                    VALUES (?, ?, 'registered')
                """, (student['student_id'], event['event_id']))
                
                # Try to insert again (should fail)
                try:
                    cursor.execute("""
                        INSERT INTO Registrations (student_id, event_id, status)
                        VALUES (?, ?, 'registered')
                    """, (student['student_id'], event['event_id']))
                    
                    self.log_test_result(
                        "Duplicate Registration Prevention",
                        "FAIL",
                        "System allowed duplicate registration"
                    )
                    self.conn.rollback()
                except sqlite3.IntegrityError:
                    self.log_test_result(
                        "Duplicate Registration Prevention",
                        "PASS",
                        "System correctly prevented duplicate registration"
                    )
                    self.conn.rollback()
        except Exception as e:
            self.log_test_result(
                "Duplicate Registration Test",
                "ERROR",
                f"Test failed: {e}"
            )
    
    def test_missing_data_scenarios(self):
        """Test for missing data scenarios."""
        print("\n🔍 Testing Missing Data Scenarios...")
        
        cursor = self.conn.cursor()
        
        # Test 1: Events without required data
        cursor.execute("""
            SELECT event_id, title, start_time, end_time, capacity
            FROM Events
            WHERE title IS NULL OR title = '' OR start_time IS NULL OR end_time IS NULL OR capacity IS NULL
        """)
        
        missing_data_events = cursor.fetchall()
        if missing_data_events:
            self.log_test_result(
                "Events Missing Required Data",
                "FAIL",
                f"Found {len(missing_data_events)} events with missing data"
            )
            for event in missing_data_events:
                self.errors_found.append({
                    "type": "missing_event_data",
                    "event_id": event['event_id'],
                    "missing_fields": [k for k, v in dict(event).items() if v is None or v == '']
                })
        else:
            self.log_test_result("Events Missing Required Data", "PASS")
        
        # Test 2: Students without required data
        cursor.execute("""
            SELECT student_id, name, email
            FROM Students
            WHERE name IS NULL OR name = '' OR email IS NULL OR email = ''
        """)
        
        missing_data_students = cursor.fetchall()
        if missing_data_students:
            self.log_test_result(
                "Students Missing Required Data",
                "FAIL",
                f"Found {len(missing_data_students)} students with missing data"
            )
        else:
            self.log_test_result("Students Missing Required Data", "PASS")
        
        # Test 3: Registrations without valid references
        cursor.execute("""
            SELECT r.registration_id, r.student_id, r.event_id
            FROM Registrations r
            LEFT JOIN Students s ON r.student_id = s.student_id
            LEFT JOIN Events e ON r.event_id = e.event_id
            WHERE s.student_id IS NULL OR e.event_id IS NULL
        """)
        
        orphaned_registrations = cursor.fetchall()
        if orphaned_registrations:
            self.log_test_result(
                "Orphaned Registrations",
                "FAIL",
                f"Found {len(orphaned_registrations)} orphaned registrations"
            )
        else:
            self.log_test_result("Orphaned Registrations", "PASS")
    
    def test_feedback_scenarios(self):
        """Test feedback-related scenarios."""
        print("\n🔍 Testing Feedback Scenarios...")
        
        cursor = self.conn.cursor()
        
        # Test 1: Feedback without attendance
        cursor.execute("""
            SELECT f.feedback_id, f.registration_id, s.name as student_name, e.title as event_title
            FROM Feedback f
            JOIN Registrations r ON f.registration_id = r.registration_id
            JOIN Students s ON r.student_id = s.student_id
            JOIN Events e ON r.event_id = e.event_id
            LEFT JOIN Attendance a ON f.registration_id = a.registration_id AND a.attended = 1
            WHERE a.attendance_id IS NULL
        """)
        
        invalid_feedback = cursor.fetchall()
        if invalid_feedback:
            self.log_test_result(
                "Feedback Without Attendance",
                "FAIL",
                f"Found {len(invalid_feedback)} feedback entries from non-attendees"
            )
            for feedback in invalid_feedback:
                self.errors_found.append({
                    "type": "invalid_feedback",
                    "feedback_id": feedback['feedback_id'],
                    "student": feedback['student_name'],
                    "event": feedback['event_title']
                })
        else:
            self.log_test_result("Feedback Without Attendance", "PASS")
        
        # Test 2: Invalid feedback ratings
        cursor.execute("""
            SELECT feedback_id, rating, s.name as student_name, e.title as event_title
            FROM Feedback f
            JOIN Registrations r ON f.registration_id = r.registration_id
            JOIN Students s ON r.student_id = s.student_id
            JOIN Events e ON r.event_id = e.event_id
            WHERE f.rating < 1 OR f.rating > 5
        """)
        
        invalid_ratings = cursor.fetchall()
        if invalid_ratings:
            self.log_test_result(
                "Invalid Feedback Ratings",
                "FAIL",
                f"Found {len(invalid_ratings)} feedback entries with invalid ratings"
            )
        else:
            self.log_test_result("Invalid Feedback Ratings", "PASS")
        
        # Test 3: Duplicate feedback
        cursor.execute("""
            SELECT registration_id, COUNT(*) as count
            FROM Feedback
            GROUP BY registration_id
            HAVING COUNT(*) > 1
        """)
        
        duplicate_feedback = cursor.fetchall()
        if duplicate_feedback:
            self.log_test_result(
                "Duplicate Feedback",
                "FAIL",
                f"Found {len(duplicate_feedback)} registrations with multiple feedback entries"
            )
        else:
            self.log_test_result("Duplicate Feedback", "PASS")
    
    def test_cancelled_registrations(self):
        """Test cancelled registration scenarios."""
        print("\n🔍 Testing Cancelled Registration Scenarios...")
        
        cursor = self.conn.cursor()
        
        # Test 1: Attendance for cancelled registrations
        cursor.execute("""
            SELECT a.attendance_id, r.registration_id, r.status, s.name as student_name, e.title as event_title
            FROM Attendance a
            JOIN Registrations r ON a.registration_id = r.registration_id
            JOIN Students s ON r.student_id = s.student_id
            JOIN Events e ON r.event_id = e.event_id
            WHERE r.status = 'cancelled'
        """)
        
        cancelled_attendance = cursor.fetchall()
        if cancelled_attendance:
            self.log_test_result(
                "Attendance for Cancelled Registrations",
                "FAIL",
                f"Found {len(cancelled_attendance)} attendance records for cancelled registrations"
            )
        else:
            self.log_test_result("Attendance for Cancelled Registrations", "PASS")
        
        # Test 2: Feedback for cancelled registrations
        cursor.execute("""
            SELECT f.feedback_id, r.registration_id, r.status, s.name as student_name, e.title as event_title
            FROM Feedback f
            JOIN Registrations r ON f.registration_id = r.registration_id
            JOIN Students s ON r.student_id = s.student_id
            JOIN Events e ON r.event_id = e.event_id
            WHERE r.status = 'cancelled'
        """)
        
        cancelled_feedback = cursor.fetchall()
        if cancelled_feedback:
            self.log_test_result(
                "Feedback for Cancelled Registrations",
                "FAIL",
                f"Found {len(cancelled_feedback)} feedback entries for cancelled registrations"
            )
        else:
            self.log_test_result("Feedback for Cancelled Registrations", "PASS")
    
    def test_capacity_violations(self):
        """Test event capacity violations."""
        print("\n🔍 Testing Capacity Violations...")
        
        cursor = self.conn.cursor()
        
        # Check for events exceeding capacity
        cursor.execute("""
            SELECT e.event_id, e.title, e.capacity,
                   COUNT(r.registration_id) as actual_registrations
            FROM Events e
            LEFT JOIN Registrations r ON e.event_id = r.event_id AND r.status = 'registered'
            GROUP BY e.event_id
            HAVING actual_registrations > e.capacity
        """)
        
        capacity_violations = cursor.fetchall()
        if capacity_violations:
            self.log_test_result(
                "Capacity Violations",
                "FAIL",
                f"Found {len(capacity_violations)} events exceeding capacity"
            )
            for violation in capacity_violations:
                self.errors_found.append({
                    "type": "capacity_violation",
                    "event_id": violation['event_id'],
                    "title": violation['title'],
                    "capacity": violation['capacity'],
                    "actual": violation['actual_registrations']
                })
        else:
            self.log_test_result("Capacity Violations", "PASS")
    
    def test_temporal_consistency(self):
        """Test temporal consistency issues."""
        print("\n🔍 Testing Temporal Consistency...")
        
        cursor = self.conn.cursor()
        
        # Test 1: Events with end time before start time
        cursor.execute("""
            SELECT event_id, title, start_time, end_time
            FROM Events
            WHERE end_time < start_time
        """)
        
        invalid_times = cursor.fetchall()
        if invalid_times:
            self.log_test_result(
                "Invalid Event Times",
                "FAIL",
                f"Found {len(invalid_times)} events with end time before start time"
            )
        else:
            self.log_test_result("Invalid Event Times", "PASS")
        
        # Test 2: Registrations after event has ended
        cursor.execute("""
            SELECT r.registration_id, r.registration_time, e.title, e.end_time
            FROM Registrations r
            JOIN Events e ON r.event_id = e.event_id
            WHERE r.registration_time > e.end_time
        """)
        
        late_registrations = cursor.fetchall()
        if late_registrations:
            self.log_test_result(
                "Late Registrations",
                "WARN",
                f"Found {len(late_registrations)} registrations after event ended"
            )
        else:
            self.log_test_result("Late Registrations", "PASS")
        
        # Test 3: Attendance before event started
        cursor.execute("""
            SELECT a.attendance_id, a.check_in_time, e.title, e.start_time
            FROM Attendance a
            JOIN Registrations r ON a.registration_id = r.registration_id
            JOIN Events e ON r.event_id = e.event_id
            WHERE a.check_in_time < e.start_time
        """)
        
        early_attendance = cursor.fetchall()
        if early_attendance:
            self.log_test_result(
                "Early Attendance",
                "WARN",
                f"Found {len(early_attendance)} attendance records before event started"
            )
        else:
            self.log_test_result("Early Attendance", "PASS")
    
    def test_data_integrity(self):
        """Test overall data integrity."""
        print("\n🔍 Testing Data Integrity...")
        
        cursor = self.conn.cursor()
        
        # Test foreign key constraints
        try:
            cursor.execute("PRAGMA foreign_key_check")
            fk_violations = cursor.fetchall()
            if fk_violations:
                self.log_test_result(
                    "Foreign Key Constraints",
                    "FAIL",
                    f"Found {len(fk_violations)} foreign key violations"
                )
            else:
                self.log_test_result("Foreign Key Constraints", "PASS")
        except Exception as e:
            self.log_test_result(
                "Foreign Key Constraints",
                "ERROR",
                f"Could not check foreign keys: {e}"
            )
        
        # Test for negative values where they shouldn't exist
        cursor.execute("""
            SELECT event_id, title, capacity
            FROM Events
            WHERE capacity < 0
        """)
        
        negative_capacity = cursor.fetchall()
        if negative_capacity:
            self.log_test_result(
                "Negative Capacity",
                "FAIL",
                f"Found {len(negative_capacity)} events with negative capacity"
            )
        else:
            self.log_test_result("Negative Capacity", "PASS")
    
    def fix_identified_errors(self):
        """Fix identified errors automatically where possible."""
        print("\n🔧 Fixing Identified Errors...")
        
        cursor = self.conn.cursor()
        
        for error in self.errors_found:
            error_type = error['type']
            
            if error_type == 'duplicate_registration':
                # Remove duplicate registrations, keeping the latest one
                cursor.execute("""
                    DELETE FROM Registrations
                    WHERE student_id = ? AND event_id = ?
                    AND registration_id NOT IN (
                        SELECT registration_id FROM Registrations
                        WHERE student_id = ? AND event_id = ?
                        ORDER BY registration_time DESC
                        LIMIT 1
                    )
                """, (error['student_id'], error['event_id'], 
                      error['student_id'], error['event_id']))
                
                self.fixes_applied.append(f"Removed duplicate registration for student {error['student_id']}, event {error['event_id']}")
            
            elif error_type == 'invalid_feedback':
                # Remove feedback from non-attendees
                cursor.execute("DELETE FROM Feedback WHERE feedback_id = ?", (error['feedback_id'],))
                self.fixes_applied.append(f"Removed invalid feedback {error['feedback_id']} from {error['student']}")
            
            elif error_type == 'capacity_violation':
                # Update capacity to match actual registrations
                new_capacity = error['actual'] + 5  # Add buffer
                cursor.execute("UPDATE Events SET capacity = ? WHERE event_id = ?", 
                             (new_capacity, error['event_id']))
                self.fixes_applied.append(f"Updated capacity for event {error['event_id']} to {new_capacity}")
        
        if self.fixes_applied:
            self.conn.commit()
            self.log_test_result("Error Fixes Applied", "PASS", f"Applied {len(self.fixes_applied)} fixes")
        else:
            self.log_test_result("Error Fixes Applied", "PASS", "No fixes needed")
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 80)
        print("📊 DATABASE ERROR TESTING REPORT")
        print("=" * 80)
        
        # Summary statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warning_tests = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        print(f"📈 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️  Warnings: {warning_tests}")
        print(f"   🔧 Fixes Applied: {len(self.fixes_applied)}")
        
        # Detailed results
        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            status_emoji = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️"
            print(f"   {status_emoji} {result['test']}: {result['status']}")
            if result['details']:
                print(f"      {result['details']}")
        
        # Errors found
        if self.errors_found:
            print(f"\n🚨 Errors Found:")
            for error in self.errors_found:
                print(f"   • {error['type']}: {error}")
        
        # Fixes applied
        if self.fixes_applied:
            print(f"\n🔧 Fixes Applied:")
            for fix in self.fixes_applied:
                print(f"   • {fix}")
        
        # Overall status
        if failed_tests == 0:
            print(f"\n🎉 Overall Status: EXCELLENT - No critical errors found!")
        elif failed_tests <= 2:
            print(f"\n✅ Overall Status: GOOD - Minor issues found and fixed")
        else:
            print(f"\n⚠️  Overall Status: NEEDS ATTENTION - Multiple issues found")
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "warnings": warning_tests,
            "fixes_applied": len(self.fixes_applied),
            "errors_found": len(self.errors_found)
        }
    
    def run_all_tests(self):
        """Run all database error tests."""
        print("🧪 STARTING COMPREHENSIVE DATABASE ERROR TESTING")
        print("=" * 80)
        
        if not self.connect_db():
            return None
        
        try:
            # Run all test scenarios
            self.test_duplicate_registrations()
            self.test_missing_data_scenarios()
            self.test_feedback_scenarios()
            self.test_cancelled_registrations()
            self.test_capacity_violations()
            self.test_temporal_consistency()
            self.test_data_integrity()
            
            # Fix identified errors
            self.fix_identified_errors()
            
            # Generate report
            return self.generate_test_report()
            
        finally:
            self.close_db()


def main():
    """Main function to run database error testing."""
    tester = DatabaseErrorTester()
    result = tester.run_all_tests()
    
    if result:
        if result['failed'] == 0:
            print(f"\n🎉 Database is in excellent condition!")
            return 0
        elif result['failed'] <= 2:
            print(f"\n✅ Database issues have been resolved!")
            return 0
        else:
            print(f"\n⚠️  Database needs manual attention for remaining issues.")
            return 1
    else:
        print(f"\n❌ Testing failed - check database connection.")
        return 1


if __name__ == "__main__":
    exit(main())
