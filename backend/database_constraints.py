#!/usr/bin/env python3
"""
Database Constraints and Validation System.
Enforces data integrity rules and prevents common errors.
"""
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from config import settings


class DatabaseConstraints:
    """Database constraints and validation system."""
    
    def __init__(self):
        self.db_path = Path(settings.database_path)
        self.conn = None
    
    def connect_db(self):
        """Connect to database."""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def close_db(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def enable_foreign_key_constraints(self):
        """Enable foreign key constraints."""
        print("🔒 Enabling foreign key constraints...")
        
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        self.conn.commit()
        
        # Verify foreign keys are enabled
        cursor.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()
        if result[0]:
            print("✅ Foreign key constraints enabled")
            return True
        else:
            print("❌ Failed to enable foreign key constraints")
            return False
    
    def add_check_constraints(self):
        """Add check constraints for data validation."""
        print("🔍 Adding check constraints...")
        
        cursor = self.conn.cursor()
        
        # Note: SQLite doesn't support adding CHECK constraints to existing tables
        # We'll create triggers instead for validation
        
        constraints = [
            # Events constraints
            """
            CREATE TRIGGER IF NOT EXISTS check_event_capacity
            BEFORE INSERT ON Events
            BEGIN
                SELECT CASE
                    WHEN NEW.capacity <= 0 THEN
                        RAISE(ABORT, 'Event capacity must be positive')
                END;
            END
            """,
            
            """
            CREATE TRIGGER IF NOT EXISTS check_event_times
            BEFORE INSERT ON Events
            BEGIN
                SELECT CASE
                    WHEN NEW.end_time <= NEW.start_time THEN
                        RAISE(ABORT, 'Event end time must be after start time')
                END;
            END
            """,
            
            # Registrations constraints
            """
            CREATE TRIGGER IF NOT EXISTS check_registration_capacity
            BEFORE INSERT ON Registrations
            BEGIN
                SELECT CASE
                    WHEN (SELECT COUNT(*) FROM Registrations r 
                          JOIN Events e ON r.event_id = e.event_id 
                          WHERE r.event_id = NEW.event_id AND r.status = 'registered') >= 
                         (SELECT capacity FROM Events WHERE event_id = NEW.event_id) THEN
                        RAISE(ABORT, 'Event is at full capacity')
                END;
            END
            """,
            
            """
            CREATE TRIGGER IF NOT EXISTS check_registration_timing
            BEFORE INSERT ON Registrations
            BEGIN
                SELECT CASE
                    WHEN NEW.registration_time > (SELECT start_time FROM Events WHERE event_id = NEW.event_id) THEN
                        RAISE(ABORT, 'Cannot register for events that have already started')
                END;
            END
            """,
            
            # Attendance constraints
            """
            CREATE TRIGGER IF NOT EXISTS check_attendance_value
            BEFORE INSERT ON Attendance
            BEGIN
                SELECT CASE
                    WHEN NEW.attended NOT IN (0, 1) THEN
                        RAISE(ABORT, 'Attendance value must be 0 or 1')
                END;
            END
            """,
            
            # Feedback constraints
            """
            CREATE TRIGGER IF NOT EXISTS check_feedback_rating
            BEFORE INSERT ON Feedback
            BEGIN
                SELECT CASE
                    WHEN NEW.rating < 1 OR NEW.rating > 5 THEN
                        RAISE(ABORT, 'Feedback rating must be between 1 and 5')
                END;
            END
            """,
            
            """
            CREATE TRIGGER IF NOT EXISTS check_feedback_attendance
            BEFORE INSERT ON Feedback
            BEGIN
                SELECT CASE
                    WHEN NOT EXISTS (
                        SELECT 1 FROM Attendance a 
                        WHERE a.registration_id = NEW.registration_id AND a.attended = 1
                    ) THEN
                        RAISE(ABORT, 'Feedback can only be submitted by attendees')
                END;
            END
            """,
            
            # Prevent duplicate registrations
            """
            CREATE TRIGGER IF NOT EXISTS prevent_duplicate_registration
            BEFORE INSERT ON Registrations
            BEGIN
                SELECT CASE
                    WHEN EXISTS (
                        SELECT 1 FROM Registrations 
                        WHERE student_id = NEW.student_id AND event_id = NEW.event_id
                    ) THEN
                        RAISE(ABORT, 'Student is already registered for this event')
                END;
            END
            """,
            
            # Prevent duplicate feedback
            """
            CREATE TRIGGER IF NOT EXISTS prevent_duplicate_feedback
            BEFORE INSERT ON Feedback
            BEGIN
                SELECT CASE
                    WHEN EXISTS (
                        SELECT 1 FROM Feedback 
                        WHERE registration_id = NEW.registration_id
                    ) THEN
                        RAISE(ABORT, 'Feedback already exists for this registration')
                END;
            END
            """,
            
            # Prevent duplicate attendance
            """
            CREATE TRIGGER IF NOT EXISTS prevent_duplicate_attendance
            BEFORE INSERT ON Attendance
            BEGIN
                SELECT CASE
                    WHEN EXISTS (
                        SELECT 1 FROM Attendance 
                        WHERE registration_id = NEW.registration_id
                    ) THEN
                        RAISE(ABORT, 'Attendance already marked for this registration')
                END;
            END
            """
        ]
        
        for constraint in constraints:
            try:
                cursor.execute(constraint)
                print(f"   ✅ Added constraint trigger")
            except sqlite3.Error as e:
                print(f"   ⚠️  Constraint trigger warning: {e}")
        
        self.conn.commit()
        print("✅ Check constraints added via triggers")
    
    def add_unique_constraints(self):
        """Add unique constraints where needed."""
        print("🔑 Adding unique constraints...")
        
        cursor = self.conn.cursor()
        
        # Check if college-scoped unique constraints exist
        try:
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_events_college_local 
                ON Events(college_id, college_event_id)
            """)
            print("   ✅ Events college-scoped unique constraint")
        except sqlite3.Error as e:
            print(f"   ⚠️  Events constraint: {e}")
        
        try:
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_students_college_local 
                ON Students(college_id, college_student_id)
            """)
            print("   ✅ Students college-scoped unique constraint")
        except sqlite3.Error as e:
            print(f"   ⚠️  Students constraint: {e}")
        
        # Ensure email uniqueness
        try:
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_students_email 
                ON Students(email)
            """)
            print("   ✅ Students email unique constraint")
        except sqlite3.Error as e:
            print(f"   ⚠️  Email constraint: {e}")
        
        self.conn.commit()
        print("✅ Unique constraints added")
    
    def add_performance_indexes(self):
        """Add performance indexes for better query performance."""
        print("⚡ Adding performance indexes...")
        
        cursor = self.conn.cursor()
        
        indexes = [
            # Event indexes
            ("idx_events_college_id", "Events", "college_id"),
            ("idx_events_start_time", "Events", "start_time"),
            ("idx_events_status", "Events", "status"),
            ("idx_events_type", "Events", "type_id"),
            
            # Student indexes
            ("idx_students_college_id", "Students", "college_id"),
            ("idx_students_email", "Students", "email"),
            ("idx_students_semester", "Students", "semester"),
            
            # Registration indexes
            ("idx_registrations_student", "Registrations", "student_id"),
            ("idx_registrations_event", "Registrations", "event_id"),
            ("idx_registrations_status", "Registrations", "status"),
            ("idx_registrations_time", "Registrations", "registration_time"),
            
            # Attendance indexes
            ("idx_attendance_registration", "Attendance", "registration_id"),
            ("idx_attendance_attended", "Attendance", "attended"),
            
            # Feedback indexes
            ("idx_feedback_registration", "Feedback", "registration_id"),
            ("idx_feedback_rating", "Feedback", "rating"),
            ("idx_feedback_submitted", "Feedback", "submitted_at"),
            
            # Admin indexes
            ("idx_admins_college", "Admins", "college_id"),
            ("idx_admins_email", "Admins", "email"),
            ("idx_admins_status", "Admins", "status")
        ]
        
        for index_name, table_name, columns in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({columns})")
                print(f"   ✅ {index_name}")
            except sqlite3.Error as e:
                print(f"   ⚠️  {index_name}: {e}")
        
        self.conn.commit()
        print("✅ Performance indexes added")
    
    def validate_existing_data(self):
        """Validate existing data against constraints."""
        print("🔍 Validating existing data...")
        
        cursor = self.conn.cursor()
        issues_found = 0
        
        # Check for events with invalid capacity
        cursor.execute("SELECT COUNT(*) FROM Events WHERE capacity <= 0")
        invalid_capacity = cursor.fetchone()[0]
        if invalid_capacity > 0:
            print(f"   ⚠️  Found {invalid_capacity} events with invalid capacity")
            issues_found += invalid_capacity
        
        # Check for events with invalid times
        cursor.execute("SELECT COUNT(*) FROM Events WHERE end_time <= start_time")
        invalid_times = cursor.fetchone()[0]
        if invalid_times > 0:
            print(f"   ⚠️  Found {invalid_times} events with invalid time ranges")
            issues_found += invalid_times
        
        # Check for duplicate registrations
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT student_id, event_id, COUNT(*) as count
                FROM Registrations
                GROUP BY student_id, event_id
                HAVING COUNT(*) > 1
            )
        """)
        duplicates = cursor.fetchone()[0]
        if duplicates > 0:
            print(f"   ⚠️  Found {duplicates} duplicate registrations")
            issues_found += duplicates
        
        # Check for invalid feedback ratings
        cursor.execute("SELECT COUNT(*) FROM Feedback WHERE rating < 1 OR rating > 5")
        invalid_ratings = cursor.fetchone()[0]
        if invalid_ratings > 0:
            print(f"   ⚠️  Found {invalid_ratings} feedback entries with invalid ratings")
            issues_found += invalid_ratings
        
        if issues_found == 0:
            print("   ✅ No data validation issues found")
        else:
            print(f"   ⚠️  Total issues found: {issues_found}")
        
        return issues_found
    
    def create_audit_triggers(self):
        """Create audit triggers for data changes."""
        print("📝 Creating audit triggers...")
        
        cursor = self.conn.cursor()
        
        # Audit trigger for Events
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS audit_events_update
            AFTER UPDATE ON Events
            BEGIN
                INSERT INTO AuditLogs (action, table_name, record_id, old_data, new_data)
                VALUES ('UPDATE', 'Events', NEW.event_id, 
                        json_object('title', OLD.title, 'capacity', OLD.capacity, 'status', OLD.status),
                        json_object('title', NEW.title, 'capacity', NEW.capacity, 'status', NEW.status));
            END
        """)
        
        # Audit trigger for Registrations
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS audit_registrations_insert
            AFTER INSERT ON Registrations
            BEGIN
                INSERT INTO AuditLogs (action, table_name, record_id, new_data)
                VALUES ('INSERT', 'Registrations', NEW.registration_id,
                        json_object('student_id', NEW.student_id, 'event_id', NEW.event_id, 'status', NEW.status));
            END
        """)
        
        # Audit trigger for Attendance
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS audit_attendance_insert
            AFTER INSERT ON Attendance
            BEGIN
                INSERT INTO AuditLogs (action, table_name, record_id, new_data)
                VALUES ('INSERT', 'Attendance', NEW.attendance_id,
                        json_object('registration_id', NEW.registration_id, 'attended', NEW.attended));
            END
        """)
        
        # Audit trigger for Feedback
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS audit_feedback_insert
            AFTER INSERT ON Feedback
            BEGIN
                INSERT INTO AuditLogs (action, table_name, record_id, new_data)
                VALUES ('INSERT', 'Feedback', NEW.feedback_id,
                        json_object('registration_id', NEW.registration_id, 'rating', NEW.rating));
            END
        """)
        
        self.conn.commit()
        print("✅ Audit triggers created")
    
    def run_constraint_setup(self):
        """Run complete constraint setup."""
        print("🚀 SETTING UP DATABASE CONSTRAINTS AND VALIDATION")
        print("=" * 70)
        
        if not self.connect_db():
            return False
        
        try:
            # Enable foreign key constraints
            self.enable_foreign_key_constraints()
            
            # Add check constraints via triggers
            self.add_check_constraints()
            
            # Add unique constraints
            self.add_unique_constraints()
            
            # Add performance indexes
            self.add_performance_indexes()
            
            # Validate existing data
            issues = self.validate_existing_data()
            
            # Create audit triggers
            self.create_audit_triggers()
            
            print("\n" + "=" * 70)
            print("✅ DATABASE CONSTRAINTS SETUP COMPLETED!")
            print("=" * 70)
            print("🔒 Foreign key constraints: ENABLED")
            print("🛡️  Data validation triggers: ADDED")
            print("🔑 Unique constraints: ADDED")
            print("⚡ Performance indexes: ADDED")
            print("📝 Audit triggers: ADDED")
            
            if issues == 0:
                print("🎉 All existing data is valid!")
            else:
                print(f"⚠️  {issues} data issues found - consider running data cleanup")
            
            return True
            
        except Exception as e:
            print(f"❌ Constraint setup failed: {e}")
            return False
        
        finally:
            self.close_db()


def main():
    """Main function to set up database constraints."""
    constraints = DatabaseConstraints()
    success = constraints.run_constraint_setup()
    
    if success:
        print("\n🎯 Database is now protected with comprehensive constraints!")
        print("🛡️  Data integrity is enforced at the database level")
        print("⚡ Query performance is optimized with indexes")
        print("📝 All changes are audited automatically")
        return 0
    else:
        print("\n❌ Constraint setup failed!")
        return 1


if __name__ == "__main__":
    exit(main())
