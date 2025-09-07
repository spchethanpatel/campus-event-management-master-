#!/usr/bin/env python3
"""
Error Recovery and Data Repair System.
Automatically detects and fixes common database errors and inconsistencies.
"""
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

from config import settings


class ErrorRecoverySystem:
    """Comprehensive error recovery and data repair system."""
    
    def __init__(self):
        self.db_path = Path(settings.database_path)
        self.conn = None
        self.recovery_log = []
        self.fixes_applied = []
    
    def connect_db(self):
        """Connect to database with error handling."""
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
    
    def log_recovery_action(self, action: str, details: str, affected_records: int = 0):
        """Log recovery actions."""
        log_entry = {
            "action": action,
            "details": details,
            "affected_records": affected_records,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.recovery_log.append(log_entry)
        self.fixes_applied.append(f"{action}: {details}")
        print(f"🔧 {action}: {details} (affected {affected_records} records)")
    
    def fix_duplicate_registrations(self):
        """Fix duplicate registrations by keeping the latest one."""
        print("\n🔧 Fixing duplicate registrations...")
        
        cursor = self.conn.cursor()
        
        # Find duplicates
        cursor.execute("""
            SELECT student_id, event_id, COUNT(*) as count
            FROM Registrations
            GROUP BY student_id, event_id
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        total_fixed = 0
        
        for dup in duplicates:
            # Keep the latest registration, remove others
            cursor.execute("""
                DELETE FROM Registrations
                WHERE student_id = ? AND event_id = ?
                AND registration_id NOT IN (
                    SELECT registration_id FROM Registrations
                    WHERE student_id = ? AND event_id = ?
                    ORDER BY registration_time DESC
                    LIMIT 1
                )
            """, (dup['student_id'], dup['event_id'], 
                  dup['student_id'], dup['event_id']))
            
            deleted_count = cursor.rowcount
            total_fixed += deleted_count
            
            self.log_recovery_action(
                "Remove Duplicate Registration",
                f"Student {dup['student_id']}, Event {dup['event_id']}",
                deleted_count
            )
        
        if total_fixed > 0:
            self.conn.commit()
            print(f"✅ Fixed {total_fixed} duplicate registrations")
        else:
            print("✅ No duplicate registrations found")
    
    def fix_orphaned_records(self):
        """Fix orphaned records in related tables."""
        print("\n🔧 Fixing orphaned records...")
        
        cursor = self.conn.cursor()
        total_fixed = 0
        
        # Fix orphaned attendance records
        cursor.execute("""
            DELETE FROM Attendance
            WHERE registration_id NOT IN (
                SELECT registration_id FROM Registrations
            )
        """)
        attendance_fixed = cursor.rowcount
        total_fixed += attendance_fixed
        
        if attendance_fixed > 0:
            self.log_recovery_action(
                "Remove Orphaned Attendance",
                "Attendance records without valid registrations",
                attendance_fixed
            )
        
        # Fix orphaned feedback records
        cursor.execute("""
            DELETE FROM Feedback
            WHERE registration_id NOT IN (
                SELECT registration_id FROM Registrations
            )
        """)
        feedback_fixed = cursor.rowcount
        total_fixed += feedback_fixed
        
        if feedback_fixed > 0:
            self.log_recovery_action(
                "Remove Orphaned Feedback",
                "Feedback records without valid registrations",
                feedback_fixed
            )
        
        # Fix orphaned registrations
        cursor.execute("""
            DELETE FROM Registrations
            WHERE student_id NOT IN (SELECT student_id FROM Students)
            OR event_id NOT IN (SELECT event_id FROM Events)
        """)
        registration_fixed = cursor.rowcount
        total_fixed += registration_fixed
        
        if registration_fixed > 0:
            self.log_recovery_action(
                "Remove Orphaned Registrations",
                "Registrations with invalid student or event references",
                registration_fixed
            )
        
        if total_fixed > 0:
            self.conn.commit()
            print(f"✅ Fixed {total_fixed} orphaned records")
        else:
            print("✅ No orphaned records found")
    
    def fix_invalid_feedback(self):
        """Fix invalid feedback entries."""
        print("\n🔧 Fixing invalid feedback...")
        
        cursor = self.conn.cursor()
        total_fixed = 0
        
        # Remove feedback from non-attendees
        cursor.execute("""
            DELETE FROM Feedback
            WHERE registration_id IN (
                SELECT f.registration_id
                FROM Feedback f
                LEFT JOIN Attendance a ON f.registration_id = a.registration_id AND a.attended = 1
                WHERE a.attendance_id IS NULL
            )
        """)
        non_attendee_feedback = cursor.rowcount
        total_fixed += non_attendee_feedback
        
        if non_attendee_feedback > 0:
            self.log_recovery_action(
                "Remove Invalid Feedback",
                "Feedback from non-attendees",
                non_attendee_feedback
            )
        
        # Fix invalid ratings (set to 3 if invalid)
        cursor.execute("""
            UPDATE Feedback
            SET rating = 3
            WHERE rating < 1 OR rating > 5
        """)
        invalid_ratings = cursor.rowcount
        total_fixed += invalid_ratings
        
        if invalid_ratings > 0:
            self.log_recovery_action(
                "Fix Invalid Ratings",
                "Set invalid ratings to 3",
                invalid_ratings
            )
        
        # Remove duplicate feedback (keep latest)
        cursor.execute("""
            DELETE FROM Feedback
            WHERE feedback_id NOT IN (
                SELECT feedback_id FROM Feedback
                ORDER BY submitted_at DESC
            )
            AND registration_id IN (
                SELECT registration_id FROM Feedback
                GROUP BY registration_id
                HAVING COUNT(*) > 1
            )
        """)
        duplicate_feedback = cursor.rowcount
        total_fixed += duplicate_feedback
        
        if duplicate_feedback > 0:
            self.log_recovery_action(
                "Remove Duplicate Feedback",
                "Keep latest feedback per registration",
                duplicate_feedback
            )
        
        if total_fixed > 0:
            self.conn.commit()
            print(f"✅ Fixed {total_fixed} feedback issues")
        else:
            print("✅ No feedback issues found")
    
    def fix_capacity_violations(self):
        """Fix events that exceed capacity."""
        print("\n🔧 Fixing capacity violations...")
        
        cursor = self.conn.cursor()
        
        # Find events exceeding capacity
        cursor.execute("""
            SELECT e.event_id, e.title, e.capacity,
                   COUNT(r.registration_id) as actual_registrations
            FROM Events e
            LEFT JOIN Registrations r ON e.event_id = r.event_id AND r.status = 'registered'
            GROUP BY e.event_id
            HAVING actual_registrations > e.capacity
        """)
        
        violations = cursor.fetchall()
        total_fixed = 0
        
        for violation in violations:
            # Update capacity to accommodate all registrations plus buffer
            new_capacity = violation['actual_registrations'] + 5
            cursor.execute("""
                UPDATE Events
                SET capacity = ?
                WHERE event_id = ?
            """, (new_capacity, violation['event_id']))
            
            total_fixed += 1
            self.log_recovery_action(
                "Fix Capacity Violation",
                f"Event '{violation['title']}' capacity increased to {new_capacity}",
                1
            )
        
        if total_fixed > 0:
            self.conn.commit()
            print(f"✅ Fixed {total_fixed} capacity violations")
        else:
            print("✅ No capacity violations found")
    
    def fix_temporal_inconsistencies(self):
        """Fix temporal inconsistencies."""
        print("\n🔧 Fixing temporal inconsistencies...")
        
        cursor = self.conn.cursor()
        total_fixed = 0
        
        # Fix events with end time before start time
        cursor.execute("""
            SELECT event_id, title, start_time, end_time
            FROM Events
            WHERE end_time <= start_time
        """)
        
        invalid_events = cursor.fetchall()
        
        for event in invalid_events:
            # Set end time to 2 hours after start time
            start_dt = datetime.fromisoformat(event['start_time'].replace(' ', 'T'))
            end_dt = start_dt + timedelta(hours=2)
            new_end_time = end_dt.strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute("""
                UPDATE Events
                SET end_time = ?
                WHERE event_id = ?
            """, (new_end_time, event['event_id']))
            
            total_fixed += 1
            self.log_recovery_action(
                "Fix Invalid Event Times",
                f"Event '{event['title']}' end time corrected",
                1
            )
        
        # Fix negative capacity
        cursor.execute("""
            UPDATE Events
            SET capacity = 10
            WHERE capacity <= 0
        """)
        negative_capacity = cursor.rowcount
        total_fixed += negative_capacity
        
        if negative_capacity > 0:
            self.log_recovery_action(
                "Fix Negative Capacity",
                "Set negative capacity to 10",
                negative_capacity
            )
        
        if total_fixed > 0:
            self.conn.commit()
            print(f"✅ Fixed {total_fixed} temporal inconsistencies")
        else:
            print("✅ No temporal inconsistencies found")
    
    def fix_cancelled_registration_issues(self):
        """Fix issues with cancelled registrations."""
        print("\n🔧 Fixing cancelled registration issues...")
        
        cursor = self.conn.cursor()
        total_fixed = 0
        
        # Remove attendance for cancelled registrations
        cursor.execute("""
            DELETE FROM Attendance
            WHERE registration_id IN (
                SELECT registration_id FROM Registrations
                WHERE status = 'cancelled'
            )
        """)
        cancelled_attendance = cursor.rowcount
        total_fixed += cancelled_attendance
        
        if cancelled_attendance > 0:
            self.log_recovery_action(
                "Remove Cancelled Attendance",
                "Attendance records for cancelled registrations",
                cancelled_attendance
            )
        
        # Remove feedback for cancelled registrations
        cursor.execute("""
            DELETE FROM Feedback
            WHERE registration_id IN (
                SELECT registration_id FROM Registrations
                WHERE status = 'cancelled'
            )
        """)
        cancelled_feedback = cursor.rowcount
        total_fixed += cancelled_feedback
        
        if cancelled_feedback > 0:
            self.log_recovery_action(
                "Remove Cancelled Feedback",
                "Feedback records for cancelled registrations",
                cancelled_feedback
            )
        
        if total_fixed > 0:
            self.conn.commit()
            print(f"✅ Fixed {total_fixed} cancelled registration issues")
        else:
            print("✅ No cancelled registration issues found")
    
    def fix_missing_data(self):
        """Fix missing required data."""
        print("\n🔧 Fixing missing data...")
        
        cursor = self.conn.cursor()
        total_fixed = 0
        
        # Fix empty event titles
        cursor.execute("""
            UPDATE Events
            SET title = 'Untitled Event'
            WHERE title IS NULL OR title = ''
        """)
        empty_titles = cursor.rowcount
        total_fixed += empty_titles
        
        if empty_titles > 0:
            self.log_recovery_action(
                "Fix Empty Event Titles",
                "Set empty titles to 'Untitled Event'",
                empty_titles
            )
        
        # Fix empty student names
        cursor.execute("""
            UPDATE Students
            SET name = 'Unknown Student'
            WHERE name IS NULL OR name = ''
        """)
        empty_names = cursor.rowcount
        total_fixed += empty_names
        
        if empty_names > 0:
            self.log_recovery_action(
                "Fix Empty Student Names",
                "Set empty names to 'Unknown Student'",
                empty_names
            )
        
        # Fix empty student emails
        cursor.execute("""
            UPDATE Students
            SET email = 'unknown' || student_id || '@example.com'
            WHERE email IS NULL OR email = ''
        """)
        empty_emails = cursor.rowcount
        total_fixed += empty_emails
        
        if empty_emails > 0:
            self.log_recovery_action(
                "Fix Empty Student Emails",
                "Generate placeholder emails",
                empty_emails
            )
        
        if total_fixed > 0:
            self.conn.commit()
            print(f"✅ Fixed {total_fixed} missing data issues")
        else:
            print("✅ No missing data issues found")
    
    def create_missing_feedback_placeholders(self):
        """Create placeholder feedback for attendees who haven't provided feedback."""
        print("\n🔧 Creating missing feedback placeholders...")
        
        cursor = self.conn.cursor()
        
        # Find attendees without feedback (for events that ended more than 1 day ago)
        cursor.execute("""
            SELECT r.registration_id, s.name as student_name, e.title as event_title
            FROM Registrations r
            JOIN Students s ON r.student_id = s.student_id
            JOIN Events e ON r.event_id = e.event_id
            JOIN Attendance a ON r.registration_id = a.registration_id
            LEFT JOIN Feedback f ON r.registration_id = f.registration_id
            WHERE a.attended = 1 
            AND f.feedback_id IS NULL
            AND e.start_time < datetime('now', '-1 day')
        """)
        
        missing_feedback = cursor.fetchall()
        total_created = 0
        
        for missing in missing_feedback:
            cursor.execute("""
                INSERT INTO Feedback (registration_id, rating, comments)
                VALUES (?, 3, 'No feedback provided - placeholder entry')
            """, (missing['registration_id'],))
            
            total_created += 1
            self.log_recovery_action(
                "Create Placeholder Feedback",
                f"Student: {missing['student_name']}, Event: {missing['event_title']}",
                1
            )
        
        if total_created > 0:
            self.conn.commit()
            print(f"✅ Created {total_created} placeholder feedback entries")
        else:
            print("✅ No missing feedback found")
    
    def run_complete_recovery(self):
        """Run complete error recovery process."""
        print("🚀 STARTING COMPREHENSIVE ERROR RECOVERY")
        print("=" * 70)
        
        if not self.connect_db():
            return False
        
        try:
            # Run all recovery operations
            self.fix_duplicate_registrations()
            self.fix_orphaned_records()
            self.fix_invalid_feedback()
            self.fix_capacity_violations()
            self.fix_temporal_inconsistencies()
            self.fix_cancelled_registration_issues()
            self.fix_missing_data()
            self.create_missing_feedback_placeholders()
            
            # Generate recovery report
            self.generate_recovery_report()
            
            return True
            
        except Exception as e:
            print(f"❌ Recovery process failed: {e}")
            return False
        
        finally:
            self.close_db()
    
    def generate_recovery_report(self):
        """Generate comprehensive recovery report."""
        print("\n" + "=" * 70)
        print("📊 ERROR RECOVERY REPORT")
        print("=" * 70)
        
        total_fixes = len(self.fixes_applied)
        total_records_affected = sum(log['affected_records'] for log in self.recovery_log)
        
        print(f"🔧 Total Recovery Actions: {total_fixes}")
        print(f"📊 Total Records Affected: {total_records_affected}")
        
        if total_fixes > 0:
            print(f"\n📋 Recovery Actions Applied:")
            for i, fix in enumerate(self.fixes_applied, 1):
                print(f"   {i}. {fix}")
        
        print(f"\n📝 Detailed Recovery Log:")
        for log in self.recovery_log:
            print(f"   • {log['action']}: {log['details']}")
            print(f"     Records affected: {log['affected_records']}")
            print(f"     Time: {log['timestamp']}")
            print()
        
        if total_fixes == 0:
            print("🎉 No errors found - database is in perfect condition!")
        else:
            print(f"✅ Database recovery completed successfully!")
            print(f"🛡️  {total_fixes} issues have been resolved")
        
        return {
            "total_fixes": total_fixes,
            "total_records_affected": total_records_affected,
            "recovery_log": self.recovery_log
        }


def main():
    """Main function to run error recovery."""
    recovery = ErrorRecoverySystem()
    success = recovery.run_complete_recovery()
    
    if success:
        print("\n🎯 Database error recovery completed successfully!")
        print("🛡️  All identified issues have been resolved")
        print("✅ Database is now in optimal condition")
        return 0
    else:
        print("\n❌ Error recovery failed!")
        return 1


if __name__ == "__main__":
    exit(main())
