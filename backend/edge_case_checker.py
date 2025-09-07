#!/usr/bin/env python3
"""
Edge Case and Assumption Checker for Event Management System
Checks for: duplicate registrations, missing feedback, cancelled events, data inconsistencies
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

# Database configuration
DATABASE_PATH = Path(__file__).parent.parent / "database" / "event_management_db.db"

class EdgeCaseChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.conn = None
    
    def connect_db(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(str(DATABASE_PATH))
            self.conn.row_factory = sqlite3.Row
            return True
        except Exception as e:
            self.issues.append(f"Database connection failed: {e}")
            return False
    
    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def add_issue(self, category: str, description: str, severity: str = "ERROR"):
        """Add an issue to the list"""
        issue = {
            "category": category,
            "description": description,
            "severity": severity,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if severity == "ERROR":
            self.issues.append(issue)
        else:
            self.warnings.append(issue)
    
    def check_duplicate_registrations(self):
        """Check for duplicate student registrations for the same event"""
        print("🔍 Checking for duplicate registrations...")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT student_id, event_id, COUNT(*) as count
            FROM Registrations
            GROUP BY student_id, event_id
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        if duplicates:
            for dup in duplicates:
                self.add_issue(
                    "DUPLICATE_REGISTRATION",
                    f"Student {dup['student_id']} registered {dup['count']} times for event {dup['event_id']}",
                    "ERROR"
                )
        else:
            print("✅ No duplicate registrations found")
    
    def check_missing_feedback(self):
        """Check for missing feedback from attendees"""
        print("🔍 Checking for missing feedback...")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT r.registration_id, s.name as student_name, e.title as event_title,
                   e.start_time, a.check_in_time
            FROM Registrations r
            JOIN Students s ON r.student_id = s.student_id
            JOIN Events e ON r.event_id = e.event_id
            JOIN Attendance a ON r.registration_id = a.registration_id
            LEFT JOIN Feedback f ON r.registration_id = f.registration_id
            WHERE a.attended = 1 AND f.feedback_id IS NULL
            AND e.start_time < datetime('now', '-1 day')
        """)
        
        missing_feedback = cursor.fetchall()
        if missing_feedback:
            for missing in missing_feedback:
                self.add_issue(
                    "MISSING_FEEDBACK",
                    f"Student {missing['student_name']} attended '{missing['event_title']}' but no feedback provided",
                    "WARNING"
                )
        else:
            print("✅ All attendees have provided feedback")
    
    def check_cancelled_events(self):
        """Check for cancelled events and their impact"""
        print("🔍 Checking for cancelled events...")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT e.event_id, e.title, e.start_time, e.status,
                   COUNT(r.registration_id) as registration_count
            FROM Events e
            LEFT JOIN Registrations r ON e.event_id = r.event_id
            WHERE e.status = 'cancelled'
            GROUP BY e.event_id
        """)
        
        cancelled_events = cursor.fetchall()
        if cancelled_events:
            for event in cancelled_events:
                if event['registration_count'] > 0:
                    self.add_issue(
                        "CANCELLED_EVENT_WITH_REGISTRATIONS",
                        f"Cancelled event '{event['title']}' has {event['registration_count']} registrations",
                        "WARNING"
                    )
        else:
            print("✅ No cancelled events found")
    
    def check_past_active_events(self):
        """Check for past events still marked as active"""
        print("🔍 Checking for past events still marked as active...")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT event_id, title, start_time, status
            FROM Events
            WHERE start_time < datetime('now') AND status = 'active'
        """)
        
        past_active = cursor.fetchall()
        if past_active:
            for event in past_active:
                self.add_issue(
                    "PAST_ACTIVE_EVENT",
                    f"Event '{event['title']}' (ID: {event['event_id']}) ended but still marked as active",
                    "ERROR"
                )
        else:
            print("✅ No past events marked as active")
    
    def check_future_completed_events(self):
        """Check for future events marked as completed"""
        print("🔍 Checking for future events marked as completed...")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT event_id, title, start_time, status
            FROM Events
            WHERE start_time > datetime('now') AND status = 'completed'
        """)
        
        future_completed = cursor.fetchall()
        if future_completed:
            for event in future_completed:
                self.add_issue(
                    "FUTURE_COMPLETED_EVENT",
                    f"Event '{event['title']}' (ID: {event['event_id']}) is in the future but marked as completed",
                    "WARNING"
                )
        else:
            print("✅ No future events marked as completed")
    
    def check_attendance_without_registration(self):
        """Check for attendance records without corresponding registrations"""
        print("🔍 Checking for attendance without registration...")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT a.attendance_id, a.registration_id
            FROM Attendance a
            LEFT JOIN Registrations r ON a.registration_id = r.registration_id
            WHERE r.registration_id IS NULL
        """)
        
        orphaned_attendance = cursor.fetchall()
        if orphaned_attendance:
            for attendance in orphaned_attendance:
                self.add_issue(
                    "ORPHANED_ATTENDANCE",
                    f"Attendance record {attendance['attendance_id']} has no corresponding registration",
                    "ERROR"
                )
        else:
            print("✅ All attendance records have valid registrations")
    
    def check_feedback_without_attendance(self):
        """Check for feedback from non-attendees"""
        print("🔍 Checking for feedback without attendance...")
        
        cursor = self.conn.cursor()
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
            for feedback in invalid_feedback:
                self.add_issue(
                    "FEEDBACK_WITHOUT_ATTENDANCE",
                    f"Student {feedback['student_name']} provided feedback for '{feedback['event_title']}' but didn't attend",
                    "ERROR"
                )
        else:
            print("✅ All feedback is from attendees only")
    
    def check_capacity_violations(self):
        """Check for events exceeding capacity"""
        print("🔍 Checking for capacity violations...")
        
        cursor = self.conn.cursor()
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
            for violation in capacity_violations:
                self.add_issue(
                    "CAPACITY_VIOLATION",
                    f"Event '{violation['title']}' has {violation['actual_registrations']} registrations but capacity is {violation['capacity']}",
                    "ERROR"
                )
        else:
            print("✅ No capacity violations found")
    
    def check_invalid_ratings(self):
        """Check for invalid feedback ratings"""
        print("🔍 Checking for invalid feedback ratings...")
        
        cursor = self.conn.cursor()
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
            for rating in invalid_ratings:
                self.add_issue(
                    "INVALID_RATING",
                    f"Student {rating['student_name']} gave invalid rating {rating['rating']} for '{rating['event_title']}'",
                    "ERROR"
                )
        else:
            print("✅ All feedback ratings are valid (1-5)")
    
    def check_orphaned_records(self):
        """Check for orphaned records in related tables"""
        print("🔍 Checking for orphaned records...")
        
        cursor = self.conn.cursor()
        
        # Check registrations without valid students
        cursor.execute("""
            SELECT r.registration_id, r.student_id
            FROM Registrations r
            LEFT JOIN Students s ON r.student_id = s.student_id
            WHERE s.student_id IS NULL
        """)
        orphaned_registrations = cursor.fetchall()
        if orphaned_registrations:
            for reg in orphaned_registrations:
                self.add_issue(
                    "ORPHANED_REGISTRATION",
                    f"Registration {reg['registration_id']} references non-existent student {reg['student_id']}",
                    "ERROR"
                )
        
        # Check registrations without valid events
        cursor.execute("""
            SELECT r.registration_id, r.event_id
            FROM Registrations r
            LEFT JOIN Events e ON r.event_id = e.event_id
            WHERE e.event_id IS NULL
        """)
        orphaned_event_registrations = cursor.fetchall()
        if orphaned_event_registrations:
            for reg in orphaned_event_registrations:
                self.add_issue(
                    "ORPHANED_EVENT_REGISTRATION",
                    f"Registration {reg['registration_id']} references non-existent event {reg['event_id']}",
                    "ERROR"
                )
        
        if not orphaned_registrations and not orphaned_event_registrations:
            print("✅ No orphaned records found")
    
    def check_data_consistency(self):
        """Check for general data consistency issues"""
        print("🔍 Checking data consistency...")
        
        cursor = self.conn.cursor()
        
        # Check for events with negative capacity
        cursor.execute("SELECT event_id, title, capacity FROM Events WHERE capacity < 0")
        negative_capacity = cursor.fetchall()
        if negative_capacity:
            for event in negative_capacity:
                self.add_issue(
                    "NEGATIVE_CAPACITY",
                    f"Event '{event['title']}' has negative capacity: {event['capacity']}",
                    "ERROR"
                )
        
        # Check for events with end time before start time
        cursor.execute("""
            SELECT event_id, title, start_time, end_time
            FROM Events
            WHERE end_time < start_time
        """)
        invalid_times = cursor.fetchall()
        if invalid_times:
            for event in invalid_times:
                self.add_issue(
                    "INVALID_TIME_RANGE",
                    f"Event '{event['title']}' has end time before start time",
                    "ERROR"
                )
        
        if not negative_capacity and not invalid_times:
            print("✅ Data consistency checks passed")
    
    def check_business_logic_violations(self):
        """Check for business logic violations"""
        print("🔍 Checking business logic violations...")
        
        cursor = self.conn.cursor()
        
        # Check for registrations after event has started
        cursor.execute("""
            SELECT r.registration_id, s.name as student_name, e.title as event_title,
                   r.registration_time, e.start_time
            FROM Registrations r
            JOIN Students s ON r.student_id = s.student_id
            JOIN Events e ON r.event_id = e.event_id
            WHERE r.registration_time > e.start_time
        """)
        
        late_registrations = cursor.fetchall()
        if late_registrations:
            for reg in late_registrations:
                self.add_issue(
                    "LATE_REGISTRATION",
                    f"Student {reg['student_name']} registered for '{reg['event_title']}' after it started",
                    "WARNING"
                )
        
        # Check for attendance before event start
        cursor.execute("""
            SELECT a.attendance_id, s.name as student_name, e.title as event_title,
                   a.check_in_time, e.start_time
            FROM Attendance a
            JOIN Registrations r ON a.registration_id = r.registration_id
            JOIN Students s ON r.student_id = s.student_id
            JOIN Events e ON r.event_id = e.event_id
            WHERE a.check_in_time < e.start_time
        """)
        
        early_attendance = cursor.fetchall()
        if early_attendance:
            for att in early_attendance:
                self.add_issue(
                    "EARLY_ATTENDANCE",
                    f"Student {att['student_name']} marked attendance for '{att['event_title']}' before it started",
                    "WARNING"
                )
        
        if not late_registrations and not early_attendance:
            print("✅ Business logic checks passed")
    
    def generate_summary_report(self):
        """Generate a summary report of all issues found"""
        print("\n" + "="*60)
        print("📊 EDGE CASE ANALYSIS SUMMARY")
        print("="*60)
        
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        
        print(f"🔴 Critical Issues Found: {total_issues}")
        print(f"🟡 Warnings Found: {total_warnings}")
        print(f"📈 Total Issues: {total_issues + total_warnings}")
        
        if total_issues > 0:
            print("\n🚨 CRITICAL ISSUES:")
            print("-" * 40)
            for i, issue in enumerate(self.issues, 1):
                print(f"{i}. [{issue['category']}] {issue['description']}")
        
        if total_warnings > 0:
            print("\n⚠️  WARNINGS:")
            print("-" * 40)
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. [{warning['category']}] {warning['description']}")
        
        if total_issues == 0 and total_warnings == 0:
            print("\n🎉 EXCELLENT! No edge case issues found!")
            print("Your system is handling all edge cases correctly.")
        elif total_issues == 0:
            print("\n✅ Good! No critical issues found.")
            print("Only minor warnings that should be reviewed.")
        else:
            print(f"\n❌ {total_issues} critical issues need immediate attention!")
        
        return {
            "total_issues": total_issues,
            "total_warnings": total_warnings,
            "issues": self.issues,
            "warnings": self.warnings
        }
    
    def run_all_checks(self):
        """Run all edge case checks"""
        print("🔍 STARTING COMPREHENSIVE EDGE CASE ANALYSIS")
        print("="*60)
        
        if not self.connect_db():
            return None
        
        try:
            # Run all checks
            self.check_duplicate_registrations()
            self.check_missing_feedback()
            self.check_cancelled_events()
            self.check_past_active_events()
            self.check_future_completed_events()
            self.check_attendance_without_registration()
            self.check_feedback_without_attendance()
            self.check_capacity_violations()
            self.check_invalid_ratings()
            self.check_orphaned_records()
            self.check_data_consistency()
            self.check_business_logic_violations()
            
            # Generate summary
            return self.generate_summary_report()
            
        finally:
            self.close_db()

def main():
    """Main function to run edge case analysis"""
    checker = EdgeCaseChecker()
    result = checker.run_all_checks()
    
    if result:
        print(f"\n📋 Analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Return exit code based on issues found
        if result['total_issues'] > 0:
            print("\n❌ Critical issues found - system needs attention!")
            return 1
        elif result['total_warnings'] > 0:
            print("\n⚠️  Warnings found - review recommended")
            return 0
        else:
            print("\n🎉 Perfect! No issues found!")
            return 0
    else:
        print("\n❌ Analysis failed - check database connection")
        return 1

if __name__ == "__main__":
    exit(main())
