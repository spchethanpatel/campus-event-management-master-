#!/usr/bin/env python3
"""
Comprehensive Error Check for Event Management System
Checks database, API, and all components for errors
"""

import sqlite3
import sys
from pathlib import Path
import traceback

def check_database_connection():
    """Check database connection and basic operations"""
    print("🗄️  DATABASE CONNECTION CHECK")
    print("=" * 50)
    
    try:
        db_path = Path(__file__).parent.parent / "database" / "event_management_db.db"
        
        if not db_path.exists():
            print("❌ Database file not found!")
            print(f"   Expected path: {db_path}")
            return False
        
        print(f"✅ Database file exists: {db_path}")
        
        # Test connection
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"✅ Database connection successful")
        print(f"✅ Found {len(tables)} tables: {[t[0] for t in tables]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"   Error details: {traceback.format_exc()}")
        return False

def check_database_schema():
    """Check database schema and data integrity"""
    print("\n📊 DATABASE SCHEMA CHECK")
    print("=" * 50)
    
    try:
        db_path = Path(__file__).parent.parent / "database" / "event_management_db.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check each table structure
        tables_to_check = [
            "Colleges", "Admins", "Students", "EventTypes", 
            "Events", "Registrations", "Attendance", "Feedback", "AuditLogs"
        ]
        
        for table in tables_to_check:
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                
                if columns:
                    print(f"✅ {table}: {len(columns)} columns")
                else:
                    print(f"❌ {table}: Table not found or empty")
                    
            except Exception as e:
                print(f"❌ {table}: Error - {e}")
        
        # Check data counts
        print(f"\n📈 Data Counts:")
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   {table}: {count} records")
            except Exception as e:
                print(f"   {table}: Error - {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Schema check failed: {e}")
        return False

def check_python_imports():
    """Check if all required Python modules can be imported"""
    print("\n🐍 PYTHON IMPORTS CHECK")
    print("=" * 50)
    
    required_modules = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'pydantic', 
        'pathlib', 'datetime', 'typing'
    ]
    
    all_imports_ok = True
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            all_imports_ok = False
    
    return all_imports_ok

def check_fastapi_app():
    """Check if FastAPI app can be loaded"""
    print("\n🚀 FASTAPI APP CHECK")
    print("=" * 50)
    
    try:
        # Try to import the simple main app
        sys.path.append(str(Path(__file__).parent))
        from simple_main import app
        
        print("✅ FastAPI app imported successfully")
        print(f"✅ App title: {app.title}")
        print(f"✅ App version: {app.version}")
        
        # Check if app has routes
        routes = [route.path for route in app.routes]
        print(f"✅ Found {len(routes)} routes")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI app import failed: {e}")
        print(f"   Error details: {traceback.format_exc()}")
        return False

def check_file_structure():
    """Check if all required files exist"""
    print("\n📁 FILE STRUCTURE CHECK")
    print("=" * 50)
    
    backend_dir = Path(__file__).parent
    required_files = [
        "simple_main.py", "main.py", "config.py", "database.py",
        "models.py", "schemas.py", "test_db.py", "requirements.txt"
    ]
    
    all_files_exist = True
    
    for file in required_files:
        file_path = backend_dir / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {file} ({size} bytes)")
        else:
            print(f"❌ {file}: File not found")
            all_files_exist = False
    
    # Check routers directory
    routers_dir = backend_dir / "routers"
    if routers_dir.exists():
        router_files = list(routers_dir.glob("*.py"))
        print(f"✅ routers/ directory with {len(router_files)} files")
    else:
        print(f"❌ routers/ directory not found")
        all_files_exist = False
    
    return all_files_exist

def check_database_constraints():
    """Check database constraints and foreign keys"""
    print("\n🔗 DATABASE CONSTRAINTS CHECK")
    print("=" * 50)
    
    try:
        db_path = Path(__file__).parent.parent / "database" / "event_management_db.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check foreign key constraints
        cursor.execute("PRAGMA foreign_keys")
        fk_enabled = cursor.fetchone()[0]
        print(f"Foreign Keys: {'✅ Enabled' if fk_enabled else '⚠️  Disabled'}")
        
        # Check for orphaned records
        print(f"\n🔍 Checking for orphaned records:")
        
        # Check students without valid college
        cursor.execute("""
            SELECT COUNT(*) FROM Students s 
            LEFT JOIN Colleges c ON s.college_id = c.college_id 
            WHERE c.college_id IS NULL
        """)
        orphaned_students = cursor.fetchone()[0]
        print(f"   Orphaned Students: {orphaned_students}")
        
        # Check events without valid college
        cursor.execute("""
            SELECT COUNT(*) FROM Events e 
            LEFT JOIN Colleges c ON e.college_id = c.college_id 
            WHERE c.college_id IS NULL
        """)
        orphaned_events = cursor.fetchone()[0]
        print(f"   Orphaned Events: {orphaned_events}")
        
        # Check registrations without valid student/event
        cursor.execute("""
            SELECT COUNT(*) FROM Registrations r 
            LEFT JOIN Students s ON r.student_id = s.student_id
            LEFT JOIN Events e ON r.event_id = e.event_id
            WHERE s.student_id IS NULL OR e.event_id IS NULL
        """)
        orphaned_registrations = cursor.fetchone()[0]
        print(f"   Orphaned Registrations: {orphaned_registrations}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Constraints check failed: {e}")
        return False

def check_data_consistency():
    """Check data consistency and business rules"""
    print("\n📋 DATA CONSISTENCY CHECK")
    print("=" * 50)
    
    try:
        db_path = Path(__file__).parent.parent / "database" / "event_management_db.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        issues = []
        
        # Check for duplicate emails
        cursor.execute("""
            SELECT email, COUNT(*) as count 
            FROM Students 
            GROUP BY email 
            HAVING COUNT(*) > 1
        """)
        duplicate_emails = cursor.fetchall()
        if duplicate_emails:
            issues.append(f"Duplicate student emails: {duplicate_emails}")
        
        # Check for invalid ratings
        cursor.execute("""
            SELECT COUNT(*) FROM Feedback 
            WHERE rating < 1 OR rating > 5
        """)
        invalid_ratings = cursor.fetchone()[0]
        if invalid_ratings > 0:
            issues.append(f"Invalid feedback ratings: {invalid_ratings}")
        
        # Check for future events with past start times
        cursor.execute("""
            SELECT COUNT(*) FROM Events 
            WHERE start_time < datetime('now') AND status = 'active'
        """)
        past_events = cursor.fetchone()[0]
        if past_events > 0:
            issues.append(f"Past events marked as active: {past_events}")
        
        if issues:
            print("⚠️  Found data consistency issues:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ No data consistency issues found")
        
        conn.close()
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Data consistency check failed: {e}")
        return False

def main():
    """Run all error checks"""
    print("🔍 COMPREHENSIVE ERROR CHECK - EVENT MANAGEMENT SYSTEM")
    print("=" * 70)
    
    checks = [
        ("Database Connection", check_database_connection),
        ("Database Schema", check_database_schema),
        ("Python Imports", check_python_imports),
        ("FastAPI App", check_fastapi_app),
        ("File Structure", check_file_structure),
        ("Database Constraints", check_database_constraints),
        ("Data Consistency", check_data_consistency)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check crashed: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 ERROR CHECK SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Your system is working correctly.")
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()
