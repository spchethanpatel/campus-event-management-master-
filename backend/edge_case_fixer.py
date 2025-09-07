#!/usr/bin/env python3
"""
Edge Case Fixer for Event Management System
Automatically fixes common edge cases and data inconsistencies
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Database configuration
DATABASE_PATH = Path(__file__).parent.parent / "database" / "event_management_db.db"

class EdgeCaseFixer:
    def __init__(self):
        self.fixes_applied = []
        self.conn = None
    
    def connect_db(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(str(DATABASE_PATH))
            self.conn.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def log_fix(self, fix_type: str, description: str, affected_records: int = 0):
        """Log a fix that was applied"""
        fix = {
            "type": fix_type,
            "description": description,
            "affected_records": affected_records,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.fixes_applied.append(fix)
        print(f"✅ {description} (affected {affected_records} records)")
    
    def fix_past_active_events(self):
        """Fix past events that are still marked as active"""
        print("🔧 Fixing past events marked as active...")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT event_id, title, start_time
            FROM Events
            WHERE start_time < datetime('now') AND status = 'active'
        """)
        
        past_active = cursor.fetchall()
        if past_active:
            cursor.execute("""
                UPDATE Events
                SET status = 'completed'
                WHERE start_time < datetime('now') AND status = 'active'
            """)
            self.conn.commit()
            self.log_fix(
                "PAST_ACTIVE_EVENTS",
                f"Updated {len(past_active)} past events from 'active' to 'completed'",
                len(past_active)
            )
        else:
            print("✅ No past active events to fix")
    
    def fix_future_completed_events(self):
        """Fix future events that are marked as completed"""
        print("🔧 Fixing future events marked as completed...")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT event_id, title, start_time
            FROM Events
            WHERE start_time > datetime('now') AND status = 'completed'
        """)
        
        future_completed = cursor.fetchall()
        if future_completed:
            cursor.execute("""
                UPDATE Events
                SET status = 'active'
                WHERE start_time > datetime('now') AND status = 'completed'
            """)
            self.conn.commit()
            self.log_fix(
                "FUTURE_COMPLETED_EVENTS",
                f"Updated {len(future_completed)} future events from 'completed' to 'active'",
                len(future_completed)
            )
        else:
            print("✅ No future completed events to fix")
    
    def fix_duplicate_registrations(self):
        """Remove duplicate registrations, keeping the latest one"""
        print("🔧 Fixing duplicate registrations...")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT student_id, event_id, COUNT(*) as count
            FROM Registrations
            GROUP BY student_id, event_id
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        if duplicates:
            fixed_count = 0
            for dup in duplicates:
                # Keep the latest registration, delete others
                cursor.execute("""
                    DELETE FROM Registrations
                    WHERE student_id = ? AND event_id = ?
                    AND registration_id NOT IN (
                        SELECT registration_id FROM Registrations
                        WHERE student_id = ? AND event_id = ?
                        ORDER BY registration_time DESC
                        LIMIT 1
                    )
                """, (dup['student_id'], dup['event_id'], dup['student_id'], dup['event_id']))
                fixed_count += cursor.rowcount
            
            self.conn.commit()
            self.log_fix(
                "DUPLICATE_REGISTRATIONS",
                f"Removed {fixed_count} duplicate registrations",
                fixed_count
            )
        else:
            print("✅ No duplicate registrations to fix")
    
    def fix_orphaned_attendance(self):
        """Remove attendance records without valid registrations"""
        print("🔧 Fixing orphaned attendance records...")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT a.attendance_id
            FROM Attendance a
            LEFT JOIN Registrations r ON a.registration_id = r.registration_id
            WHERE r.registration_id IS NULL
        """)
        
        orphaned_attendance = cursor.fetchall()
        if orphaned_attendance:
            cursor.execute("""
                DELETE FROM Attendance
                WHERE registration_id NOT IN (
                    SELECT registration_id FROM Registrations
                )
            """)
            deleted_count = cursor.rowcount
            self.conn.commit()
            self.log_fix(
                "ORPHANED_ATTENDANCE",
                f"Removed {deleted_count} orphaned attendance records",
                deleted_count
            )
        else:
            print("✅ No orphaned attendance records to fix")
    
    def fix_orphaned_feedback(self):
        """Remove feedback records without valid registrations"""
        print("🔧 Fixing orphaned feedback records...")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT f.feedback_id
            FROM Feedback f
            LEFT JOIN Registrations r ON f.registration_id = r.registration_id
            WHERE r.registration_id IS NULL
        """)
        
        orphaned_feedback = cursor.fetchall()
        if orphaned_feedback:
            cursor.execute("""
                DELETE FROM Feedback
                WHERE registration_id NOT IN (
                    SELECT registration_id FROM Registrations
                )
            """)
            deleted_count = cursor.rowcount
            self.conn.commit()
            self.log_fix(
                "ORPHANED_FEEDBACK",
                f"Removed {deleted_count} orphaned feedback records",
                deleted_count
            )
        else:
            print("✅ No orphaned feedback records to fix")
    
    def fix_invalid_ratings(self):
        """Fix invalid feedback ratings (set to 3 if invalid)"""
        print("🔧 Fixing invalid feedback ratings...")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT feedback_id, rating
            FROM Feedback
            WHERE rating < 1 OR rating > 5
        """)
        
        invalid_ratings = cursor.fetchall()
        if invalid_ratings:
            cursor.execute("""
                UPDATE Feedback
                SET rating = 3
                WHERE rating < 1 OR rating > 5
            """)
            fixed_count = cursor.rowcount
            self.conn.commit()
            self.log_fix(
                "INVALID_RATINGS",
                f"Fixed {fixed_count} invalid ratings (set to 3)",
                fixed_count
            )
        else:
            print("✅ No invalid ratings to fix")
    
    def fix_negative_capacity(self):
        """Fix events with negative capacity"""
        print("🔧 Fixing negative capacity events...")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT event_id, capacity
            FROM Events
            WHERE capacity < 0
        """)
        
        negative_capacity = cursor.fetchall()
        if negative_capacity:
            cursor.execute("""
                UPDATE Events
                SET capacity = 10
                WHERE capacity < 0
            """)
            fixed_count = cursor.rowcount
            self.conn.commit()
            self.log_fix(
                "NEGATIVE_CAPACITY",
                f"Fixed {fixed_count} events with negative capacity (set to 10)",
                fixed_count
            )
        else:
            print("✅ No negative capacity events to fix")
    
    def fix_invalid_time_ranges(self):
        """Fix events with end time before start time"""
        print("🔧 Fixing invalid time ranges...")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT event_id, start_time, end_time
            FROM Events
            WHERE end_time < start_time
        """)
        
        invalid_times = cursor.fetchall()
        if invalid_times:
            for event in invalid_times:
                # Set end time to 2 hours after start time
                start_dt = datetime.fromisoformat(event['start_time'].replace(' ', 'T'))
                end_dt = start_dt + timedelta(hours=2)
                new_end_time = end_dt.strftime("%Y-%m-%d %H:%M:%S")
                
                cursor.execute("""
                    UPDATE Events
                    SET end_time = ?
                    WHERE event_id = ?
                """, (new_end_time, event['event_id']))
            
            self.conn.commit()
            self.log_fix(
                "INVALID_TIME_RANGES",
                f"Fixed {len(invalid_times)} events with invalid time ranges",
                len(invalid_times)
            )
        else:
            print("✅ No invalid time ranges to fix")
    
    def fix_capacity_violations(self):
        """Fix events that exceed capacity by updating capacity"""
        print("🔧 Fixing capacity violations...")
        
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
                new_capacity = violation['actual_registrations'] + 5  # Add buffer
                cursor.execute("""
                    UPDATE Events
                    SET capacity = ?
                    WHERE event_id = ?
                """, (new_capacity, violation['event_id']))
            
            self.conn.commit()
            self.log_fix(
                "CAPACITY_VIOLATIONS",
                f"Fixed {len(capacity_violations)} capacity violations by increasing capacity",
                len(capacity_violations)
            )
        else:
            print("✅ No capacity violations to fix")
    
    def create_missing_feedback_placeholders(self):
        """Create placeholder feedback for attendees who haven't provided feedback"""
        print("🔧 Creating placeholder feedback for missing feedback...")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT r.registration_id, s.name as student_name, e.title as event_title
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
                cursor.execute("""
                    INSERT INTO Feedback (registration_id, rating, comments)
                    VALUES (?, ?, ?)
                """, (missing['registration_id'], 3, "No feedback provided - placeholder entry"))
            
            self.conn.commit()
            self.log_fix(
                "MISSING_FEEDBACK_PLACEHOLDERS",
                f"Created {len(missing_feedback)} placeholder feedback entries",
                len(missing_feedback)
            )
        else:
            print("✅ No missing feedback to create placeholders for")
    
    def enable_foreign_key_constraints(self):
        """Enable foreign key constraints for better data integrity"""
        print("🔧 Enabling foreign key constraints...")
        
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        self.conn.commit()
        self.log_fix(
            "FOREIGN_KEY_CONSTRAINTS",
            "Enabled foreign key constraints for better data integrity",
            0
        )
    
    def generate_fix_summary(self):
        """Generate a summary of all fixes applied"""
        print("\n" + "="*60)
        print("🔧 EDGE CASE FIXES SUMMARY")
        print("="*60)
        
        total_fixes = len(self.fixes_applied)
        total_records_affected = sum(fix['affected_records'] for fix in self.fixes_applied)
        
        print(f"🔧 Total Fixes Applied: {total_fixes}")
        print(f"📊 Total Records Affected: {total_records_affected}")
        
        if total_fixes > 0:
            print("\n📋 FIXES APPLIED:")
            print("-" * 40)
            for i, fix in enumerate(self.fixes_applied, 1):
                print(f"{i}. [{fix['type']}] {fix['description']}")
                print(f"   Time: {fix['timestamp']}")
                print()
        else:
            print("\n🎉 No fixes needed! System is already in good shape.")
        
        return {
            "total_fixes": total_fixes,
            "total_records_affected": total_records_affected,
            "fixes": self.fixes_applied
        }
    
    def run_all_fixes(self):
        """Run all available fixes"""
        print("🔧 STARTING AUTOMATIC EDGE CASE FIXES")
        print("="*60)
        
        if not self.connect_db():
            return None
        
        try:
            # Run all fixes
            self.fix_past_active_events()
            self.fix_future_completed_events()
            self.fix_duplicate_registrations()
            self.fix_orphaned_attendance()
            self.fix_orphaned_feedback()
            self.fix_invalid_ratings()
            self.fix_negative_capacity()
            self.fix_invalid_time_ranges()
            self.fix_capacity_violations()
            self.create_missing_feedback_placeholders()
            self.enable_foreign_key_constraints()
            
            # Generate summary
            return self.generate_fix_summary()
            
        finally:
            self.close_db()

def main():
    """Main function to run edge case fixes"""
    fixer = EdgeCaseFixer()
    result = fixer.run_all_fixes()
    
    if result:
        print(f"\n📋 Fixes completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if result['total_fixes'] > 0:
            print(f"\n✅ Successfully applied {result['total_fixes']} fixes!")
            print("Run the edge case checker again to verify all issues are resolved.")
        else:
            print("\n🎉 No fixes needed - system is already clean!")
        
        return 0
    else:
        print("\n❌ Fixes failed - check database connection")
        return 1

if __name__ == "__main__":
    exit(main())
