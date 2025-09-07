#!/usr/bin/env python3
"""
Simplified FastAPI application for Event Management System.
Uses direct SQLite queries instead of SQLAlchemy for better compatibility.
"""
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings

# Database configuration
DATABASE_PATH = Path(__file__).parent.parent / "database" / "event_management_db.db"

# FastAPI app
app = FastAPI(
    title="Event Management System API",
    description="Simplified FastAPI backend for event management with SQLite database",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_connection():
    """Get database connection with error handling."""
    if not DATABASE_PATH.exists():
        raise HTTPException(status_code=500, detail="Database file not found")
    
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def row_to_dict(row) -> Optional[Dict[str, Any]]:
    """Convert SQLite row to dictionary."""
    return dict(row) if row else None


def rows_to_list(rows) -> List[Dict[str, Any]]:
    """Convert SQLite rows to list of dictionaries."""
    return [dict(row) for row in rows]

# Root endpoints
@app.get("/")
async def root():
    return {
        "message": "Event Management System API", 
        "database_path": str(DATABASE_PATH),
        "docs_url": "/docs",
        "health_url": "/health"
    }

@app.get("/health")
async def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM EventTypes")
        result = cursor.fetchone()
        conn.close()
        
        return {
            "status": "healthy", 
            "database_connected": True,
            "database_path": str(DATABASE_PATH),
            "event_types_count": result['count']
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database_connected": False,
            "error": str(e)
        }

# Event Types endpoints
@app.get("/event-types")
async def get_event_types():
    """Get all event types"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM EventTypes")
        event_types = rows_to_list(cursor.fetchall())
        conn.close()
        return event_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/event-types/{type_id}")
async def get_event_type(type_id: int):
    """Get event type by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM EventTypes WHERE type_id = ?", (type_id,))
        event_type = row_to_dict(cursor.fetchone())
        conn.close()
        
        if not event_type:
            raise HTTPException(status_code=404, detail="Event type not found")
        
        return event_type
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Colleges endpoints
@app.get("/colleges")
async def get_colleges():
    """Get all colleges"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Colleges")
        colleges = rows_to_list(cursor.fetchall())
        conn.close()
        return colleges
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/colleges/{college_id}")
async def get_college(college_id: int):
    """Get college by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Colleges WHERE college_id = ?", (college_id,))
        college = row_to_dict(cursor.fetchone())
        conn.close()
        
        if not college:
            raise HTTPException(status_code=404, detail="College not found")
        
        return college
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Students endpoints
@app.get("/students")
async def get_students():
    """Get all students"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Students")
        students = rows_to_list(cursor.fetchall())
        conn.close()
        return students
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students/{student_id}")
async def get_student(student_id: int):
    """Get student by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Students WHERE student_id = ?", (student_id,))
        student = row_to_dict(cursor.fetchone())
        conn.close()
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return student
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Events endpoints
@app.get("/events")
async def get_events():
    """Get all events"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*, et.name as event_type_name, c.name as college_name
            FROM Events e
            LEFT JOIN EventTypes et ON e.type_id = et.type_id
            LEFT JOIN Colleges c ON e.college_id = c.college_id
        """)
        events = rows_to_list(cursor.fetchall())
        conn.close()
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/{event_id}")
async def get_event(event_id: int):
    """Get event by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*, et.name as event_type_name, c.name as college_name
            FROM Events e
            LEFT JOIN EventTypes et ON e.type_id = et.type_id
            LEFT JOIN Colleges c ON e.college_id = c.college_id
            WHERE e.event_id = ?
        """, (event_id,))
        event = row_to_dict(cursor.fetchone())
        conn.close()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Registrations endpoints
@app.get("/registrations")
async def get_registrations():
    """Get all registrations"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.*, s.name as student_name, e.title as event_title
            FROM Registrations r
            LEFT JOIN Students s ON r.student_id = s.student_id
            LEFT JOIN Events e ON r.event_id = e.event_id
        """)
        registrations = rows_to_list(cursor.fetchall())
        conn.close()
        return registrations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/registrations/{registration_id}")
async def get_registration(registration_id: int):
    """Get registration by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.*, s.name as student_name, e.title as event_title
            FROM Registrations r
            LEFT JOIN Students s ON r.student_id = s.student_id
            LEFT JOIN Events e ON r.event_id = e.event_id
            WHERE r.registration_id = ?
        """, (registration_id,))
        registration = row_to_dict(cursor.fetchone())
        conn.close()
        
        if not registration:
            raise HTTPException(status_code=404, detail="Registration not found")
        
        return registration
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Statistics endpoints
@app.get("/stats")
async def get_statistics():
    """Get system statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Count colleges
        cursor.execute("SELECT COUNT(*) as count FROM Colleges")
        stats['colleges'] = cursor.fetchone()['count']
        
        # Count students
        cursor.execute("SELECT COUNT(*) as count FROM Students")
        stats['students'] = cursor.fetchone()['count']
        
        # Count events
        cursor.execute("SELECT COUNT(*) as count FROM Events")
        stats['events'] = cursor.fetchone()['count']
        
        # Count registrations
        cursor.execute("SELECT COUNT(*) as count FROM Registrations")
        stats['registrations'] = cursor.fetchone()['count']
        
        # Count event types
        cursor.execute("SELECT COUNT(*) as count FROM EventTypes")
        stats['event_types'] = cursor.fetchone()['count']
        
        conn.close()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting Event Management System API")
    print(f"📁 Database: {DATABASE_PATH}")
    print(f"🌐 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

