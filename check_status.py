#!/usr/bin/env python3
"""
Event Management System Status Checker
This script checks if the backend server is running and accessible.
"""

import requests
import sys
import os
from pathlib import Path

def check_backend_status():
    """Check if the backend server is running."""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running on http://localhost:8000")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Database: {data.get('database_connected', False)}")
            return True
        else:
            print(f"❌ Backend server responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running or not accessible")
        return False
    except requests.exceptions.Timeout:
        print("❌ Backend server request timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking backend status: {e}")
        return False

def check_database():
    """Check if the database file exists."""
    db_path = Path("database/event_management_db.db")
    if db_path.exists():
        print(f"✅ Database file found: {db_path}")
        return True
    else:
        print(f"❌ Database file not found: {db_path}")
        return False

def check_frontend():
    """Check if frontend files exist."""
    frontend_path = Path("frontend")
    if frontend_path.exists():
        print("✅ Frontend directory found")
        return True
    else:
        print("❌ Frontend directory not found")
        return False

def main():
    print("🔍 Event Management System Status Check")
    print("=" * 50)
    
    # Check database
    db_ok = check_database()
    
    # Check frontend
    frontend_ok = check_frontend()
    
    # Check backend
    backend_ok = check_backend_status()
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print(f"   Database: {'✅ OK' if db_ok else '❌ Missing'}")
    print(f"   Frontend: {'✅ OK' if frontend_ok else '❌ Missing'}")
    print(f"   Backend:  {'✅ Running' if backend_ok else '❌ Not Running'}")
    
    if not backend_ok:
        print("\n🚀 To start the backend server:")
        print("   1. Open a new terminal/command prompt")
        print("   2. Navigate to the project directory")
        print("   3. Run: cd backend && python main.py")
        print("   4. Or double-click: start_backend.bat")
    
    if not frontend_ok:
        print("\n🚀 To start the frontend server:")
        print("   1. Open a new terminal/command prompt")
        print("   2. Navigate to the project directory")
        print("   3. Run: cd frontend && npm run dev")
        print("   4. Or double-click: start_frontend.bat")
    
    if backend_ok and frontend_ok:
        print("\n🎉 System is ready! Access the application at:")
        print("   Frontend: http://localhost:5173 or http://localhost:5174")
        print("   Backend API: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
