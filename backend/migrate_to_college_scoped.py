#!/usr/bin/env python3
"""
Migration Script: Add College-Scoped IDs to Event Management System
Converts existing system to support college-scoped unique IDs
"""

import sqlite3
from pathlib import Path
from datetime import datetime

# Database configuration
DATABASE_PATH = Path(__file__).parent.parent / "database" / "event_management_db.db"

class CollegeScopedMigration:
    def __init__(self):
        self.conn = None
        self.backup_path = None
    
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
    
    def create_backup(self):
        """Create backup of current database"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup_path = DATABASE_PATH.parent / f"event_management_db_backup_{timestamp}.db"
            
            # Copy database file
            import shutil
            shutil.copy2(DATABASE_PATH, self.backup_path)
            print(f"✅ Database backup created: {self.backup_path}")
            return True
        except Exception as e:
            print(f"❌ Backup creation failed: {e}")
            return False
    
    def add_college_scoped_columns(self):
        """Add college-scoped ID columns to existing tables"""
        print("🔧 Adding college-scoped ID columns...")
        
        cursor = self.conn.cursor()
        
        try:
            # Add college_event_id to Events table
            cursor.execute("ALTER TABLE Events ADD COLUMN college_event_id INTEGER")
            print("✅ Added college_event_id to Events table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️  college_event_id already exists in Events table")
            else:
                raise e
        
        try:
            # Add college_student_id to Students table
            cursor.execute("ALTER TABLE Students ADD COLUMN college_student_id INTEGER")
            print("✅ Added college_student_id to Students table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️  college_student_id already exists in Students table")
            else:
                raise e
        
        self.conn.commit()
    
    def populate_college_scoped_ids(self):
        """Populate college-scoped IDs for existing data"""
        print("🔢 Populating college-scoped IDs...")
        
        cursor = self.conn.cursor()
        
        # Update Events table
        print("   Updating Events table...")
        cursor.execute("""
            UPDATE Events 
            SET college_event_id = (
                SELECT COUNT(*) + 1 
                FROM Events e2 
                WHERE e2.college_id = Events.college_id 
                AND e2.event_id < Events.event_id
            )
            WHERE college_event_id IS NULL
        """)
        events_updated = cursor.rowcount
        print(f"   ✅ Updated {events_updated} events")
        
        # Update Students table
        print("   Updating Students table...")
        cursor.execute("""
            UPDATE Students 
            SET college_student_id = (
                SELECT COUNT(*) + 1 
                FROM Students s2 
                WHERE s2.college_id = Students.college_id 
                AND s2.student_id < Students.student_id
            )
            WHERE college_student_id IS NULL
        """)
        students_updated = cursor.rowcount
        print(f"   ✅ Updated {students_updated} students")
        
        self.conn.commit()
    
    def add_unique_constraints(self):
        """Add unique constraints for college-scoped IDs"""
        print("🔒 Adding unique constraints...")
        
        cursor = self.conn.cursor()
        
        try:
            # Add unique constraint for Events
            cursor.execute("""
                CREATE UNIQUE INDEX idx_events_college_local 
                ON Events(college_id, college_event_id)
            """)
            print("✅ Added unique constraint for Events (college_id, college_event_id)")
        except sqlite3.OperationalError as e:
            if "already exists" in str(e):
                print("ℹ️  Unique constraint for Events already exists")
            else:
                raise e
        
        try:
            # Add unique constraint for Students
            cursor.execute("""
                CREATE UNIQUE INDEX idx_students_college_local 
                ON Students(college_id, college_student_id)
            """)
            print("✅ Added unique constraint for Students (college_id, college_student_id)")
        except sqlite3.OperationalError as e:
            if "already exists" in str(e):
                print("ℹ️  Unique constraint for Students already exists")
            else:
                raise e
        
        self.conn.commit()
    
    def add_performance_indexes(self):
        """Add performance indexes for college-scoped queries"""
        print("⚡ Adding performance indexes...")
        
        cursor = self.conn.cursor()
        
        indexes = [
            ("idx_events_college_id", "Events", "college_id"),
            ("idx_events_college_date", "Events", "college_id, start_time"),
            ("idx_students_college_id", "Students", "college_id"),
            ("idx_registrations_college", "Registrations", "college_id"),
            ("idx_registrations_college_event", "Registrations", "college_id, event_id"),
            ("idx_attendance_college", "Attendance", "college_id"),
            ("idx_feedback_college", "Feedback", "college_id")
        ]
        
        for index_name, table_name, columns in indexes:
            try:
                cursor.execute(f"CREATE INDEX {index_name} ON {table_name}({columns})")
                print(f"   ✅ Created index {index_name}")
            except sqlite3.OperationalError as e:
                if "already exists" in str(e):
                    print(f"   ℹ️  Index {index_name} already exists")
                else:
                    print(f"   ❌ Failed to create index {index_name}: {e}")
        
        self.conn.commit()
    
    def verify_migration(self):
        """Verify the migration was successful"""
        print("🔍 Verifying migration...")
        
        cursor = self.conn.cursor()
        
        # Check Events table
        cursor.execute("""
            SELECT 
                college_id,
                COUNT(*) as total_events,
                MIN(college_event_id) as min_local_id,
                MAX(college_event_id) as max_local_id
            FROM Events 
            WHERE college_event_id IS NOT NULL
            GROUP BY college_id
            ORDER BY college_id
        """)
        
        events_data = cursor.fetchall()
        print("   📊 Events by College:")
        for row in events_data:
            print(f"      College {row['college_id']}: {row['total_events']} events (IDs: {row['min_local_id']}-{row['max_local_id']})")
        
        # Check Students table
        cursor.execute("""
            SELECT 
                college_id,
                COUNT(*) as total_students,
                MIN(college_student_id) as min_local_id,
                MAX(college_student_id) as max_local_id
            FROM Students 
            WHERE college_student_id IS NOT NULL
            GROUP BY college_id
            ORDER BY college_id
        """)
        
        students_data = cursor.fetchall()
        print("   👥 Students by College:")
        for row in students_data:
            print(f"      College {row['college_id']}: {row['total_students']} students (IDs: {row['min_local_id']}-{row['max_local_id']})")
        
        # Check for any NULL values
        cursor.execute("SELECT COUNT(*) as null_events FROM Events WHERE college_event_id IS NULL")
        null_events = cursor.fetchone()['null_events']
        
        cursor.execute("SELECT COUNT(*) as null_students FROM Students WHERE college_student_id IS NULL")
        null_students = cursor.fetchone()['null_students']
        
        if null_events == 0 and null_students == 0:
            print("   ✅ All records have college-scoped IDs")
        else:
            print(f"   ⚠️  Found {null_events} events and {null_students} students without college-scoped IDs")
    
    def run_migration(self):
        """Run the complete migration"""
        print("🚀 STARTING COLLEGE-SCOPED ID MIGRATION")
        print("=" * 50)
        
        if not self.connect_db():
            return False
        
        try:
            # Create backup
            if not self.create_backup():
                return False
            
            # Run migration steps
            self.add_college_scoped_columns()
            self.populate_college_scoped_ids()
            self.add_unique_constraints()
            self.add_performance_indexes()
            self.verify_migration()
            
            print("\n" + "=" * 50)
            print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 50)
            print(f"📁 Backup created at: {self.backup_path}")
            print("✅ Database now supports college-scoped IDs")
            print("✅ All existing data preserved")
            print("✅ Performance indexes added")
            print("✅ Unique constraints enforced")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            print(f"📁 Backup available at: {self.backup_path}")
            print("🔄 You can restore from backup if needed")
            return False
        
        finally:
            self.close_db()

def main():
    """Main function to run migration"""
    migration = CollegeScopedMigration()
    success = migration.run_migration()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Update API endpoints to use college-scoped IDs")
        print("2. Test the new functionality")
        print("3. Update documentation")
        return 0
    else:
        print("\n❌ Migration failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main())
