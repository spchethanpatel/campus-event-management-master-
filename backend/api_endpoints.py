#!/usr/bin/env python3
"""
Comprehensive API Endpoints for Event Management System
- Creating Events
- Registering Students  
- Marking Attendance
- Generating Reports
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

# Database configuration
DATABASE_PATH = Path(__file__).parent.parent / "database" / "event_management_db.db"

# Pydantic models for request/response
class EventCreate(BaseModel):
    college_id: int
    title: str
    description: Optional[str] = None
    type_id: int
    venue: Optional[str] = None
    start_time: str
    end_time: str
    capacity: int
    created_by: int
    semester: str
    status: str = "active"

class StudentRegistration(BaseModel):
    student_id: int
    event_id: int
    status: str = "registered"

class AttendanceMark(BaseModel):
    registration_id: int
    attended: int  # 1 for attended, 0 for absent
    check_in_time: Optional[str] = None

class FeedbackSubmit(BaseModel):
    registration_id: int
    rating: int  # 1-5 scale
    comments: Optional[str] = None

class ReportRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    college_id: Optional[int] = None
    event_type_id: Optional[int] = None

# FastAPI app
app = FastAPI(
    title="Event Management System API",
    description="Complete API for event management with endpoints for events, registrations, attendance, and reports",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    """Get database connection"""
    if not DATABASE_PATH.exists():
        raise HTTPException(status_code=500, detail="Database file not found")
    
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row):
    """Convert SQLite row to dictionary"""
    return dict(row) if row else None

def rows_to_list(rows):
    """Convert SQLite rows to list of dictionaries"""
    return [dict(row) for row in rows]

# ============================================================================
# EVENT MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/events/create", response_model=Dict[str, Any])
async def create_event(event: EventCreate):
    """Create a new event"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validate college exists
        cursor.execute("SELECT college_id FROM Colleges WHERE college_id = ?", (event.college_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="College not found")
        
        # Validate event type exists
        cursor.execute("SELECT type_id FROM EventTypes WHERE type_id = ?", (event.type_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Event type not found")
        
        # Validate admin exists
        cursor.execute("SELECT admin_id FROM Admins WHERE admin_id = ?", (event.created_by,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Admin not found")
        
        # Insert event
        cursor.execute("""
            INSERT INTO Events (college_id, title, description, type_id, venue, 
                              start_time, end_time, capacity, created_by, semester, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (event.college_id, event.title, event.description, event.type_id, 
              event.venue, event.start_time, event.end_time, event.capacity, 
              event.created_by, event.semester, event.status))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Event created successfully",
            "event_id": event_id,
            "data": event.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/events", response_model=List[Dict[str, Any]])
async def get_events(
    college_id: Optional[int] = Query(None),
    event_type_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=1000)
):
    """Get events with optional filtering"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        query = """
            SELECT e.*, c.name as college_name, et.name as event_type_name, a.name as created_by_name
            FROM Events e
            LEFT JOIN Colleges c ON e.college_id = c.college_id
            LEFT JOIN EventTypes et ON e.type_id = et.type_id
            LEFT JOIN Admins a ON e.created_by = a.admin_id
            WHERE 1=1
        """
        params = []
        
        if college_id:
            query += " AND e.college_id = ?"
            params.append(college_id)
        
        if event_type_id:
            query += " AND e.type_id = ?"
            params.append(event_type_id)
        
        if status:
            query += " AND e.status = ?"
            params.append(status)
        
        query += " ORDER BY e.start_time DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        events = rows_to_list(cursor.fetchall())
        
        # Add registration count for each event
        for event in events:
            cursor.execute("""
                SELECT COUNT(*) as reg_count 
                FROM Registrations 
                WHERE event_id = ? AND status = 'registered'
            """, (event['event_id'],))
            reg_count = cursor.fetchone()['reg_count']
            event['current_registrations'] = reg_count
            event['available_spots'] = event['capacity'] - reg_count
        
        conn.close()
        return events
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/events/{event_id}", response_model=Dict[str, Any])
async def get_event_details(event_id: int):
    """Get detailed information about a specific event"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.*, c.name as college_name, et.name as event_type_name, a.name as created_by_name
            FROM Events e
            LEFT JOIN Colleges c ON e.college_id = c.college_id
            LEFT JOIN EventTypes et ON e.type_id = et.type_id
            LEFT JOIN Admins a ON e.created_by = a.admin_id
            WHERE e.event_id = ?
        """, (event_id,))
        
        event = row_to_dict(cursor.fetchone())
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Get registration count
        cursor.execute("""
            SELECT COUNT(*) as reg_count 
            FROM Registrations 
            WHERE event_id = ? AND status = 'registered'
        """, (event_id,))
        reg_count = cursor.fetchone()['reg_count']
        
        event['current_registrations'] = reg_count
        event['available_spots'] = event['capacity'] - reg_count
        
        conn.close()
        return event
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STUDENT REGISTRATION ENDPOINTS
# ============================================================================

@app.post("/api/registrations/register", response_model=Dict[str, Any])
async def register_student(registration: StudentRegistration):
    """Register a student for an event"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validate student exists
        cursor.execute("SELECT student_id FROM Students WHERE student_id = ?", (registration.student_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Validate event exists and is active
        cursor.execute("""
            SELECT event_id, capacity, start_time, status 
            FROM Events 
            WHERE event_id = ? AND status = 'active'
        """, (registration.event_id,))
        
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found or not active")
        
        # Check if event has started
        if datetime.now() > datetime.fromisoformat(event['start_time'].replace(' ', 'T')):
            raise HTTPException(status_code=400, detail="Cannot register for events that have already started")
        
        # Check if already registered
        cursor.execute("""
            SELECT registration_id 
            FROM Registrations 
            WHERE student_id = ? AND event_id = ?
        """, (registration.student_id, registration.event_id))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Student already registered for this event")
        
        # Check capacity
        cursor.execute("""
            SELECT COUNT(*) as reg_count 
            FROM Registrations 
            WHERE event_id = ? AND status = 'registered'
        """, (registration.event_id,))
        
        reg_count = cursor.fetchone()['reg_count']
        if reg_count >= event['capacity']:
            raise HTTPException(status_code=400, detail="Event is at full capacity")
        
        # Register student
        cursor.execute("""
            INSERT INTO Registrations (student_id, event_id, status) 
            VALUES (?, ?, ?)
        """, (registration.student_id, registration.event_id, registration.status))
        
        registration_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Student registered successfully",
            "registration_id": registration_id,
            "data": registration.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/registrations", response_model=List[Dict[str, Any]])
async def get_registrations(
    event_id: Optional[int] = Query(None),
    student_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None)
):
    """Get registrations with optional filtering"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT r.*, s.name as student_name, s.email as student_email, 
                   e.title as event_title, e.start_time as event_start,
                   c.name as college_name
            FROM Registrations r
            LEFT JOIN Students s ON r.student_id = s.student_id
            LEFT JOIN Events e ON r.event_id = e.event_id
            LEFT JOIN Colleges c ON s.college_id = c.college_id
            WHERE 1=1
        """
        params = []
        
        if event_id:
            query += " AND r.event_id = ?"
            params.append(event_id)
        
        if student_id:
            query += " AND r.student_id = ?"
            params.append(student_id)
        
        if status:
            query += " AND r.status = ?"
            params.append(status)
        
        query += " ORDER BY r.registration_time DESC"
        
        cursor.execute(query, params)
        registrations = rows_to_list(cursor.fetchall())
        
        conn.close()
        return registrations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ATTENDANCE MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/attendance/mark", response_model=Dict[str, Any])
async def mark_attendance(attendance: AttendanceMark):
    """Mark attendance for a registration"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validate registration exists
        cursor.execute("""
            SELECT r.*, s.name as student_name, e.title as event_title, e.start_time
            FROM Registrations r
            LEFT JOIN Students s ON r.student_id = s.student_id
            LEFT JOIN Events e ON r.event_id = e.event_id
            WHERE r.registration_id = ?
        """, (attendance.registration_id,))
        
        registration = cursor.fetchone()
        if not registration:
            raise HTTPException(status_code=404, detail="Registration not found")
        
        # Check if attendance already marked
        cursor.execute("""
            SELECT attendance_id FROM Attendance WHERE registration_id = ?
        """, (attendance.registration_id,))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Attendance already marked for this registration")
        
        # Mark attendance
        check_in_time = attendance.check_in_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO Attendance (registration_id, attended, check_in_time) 
            VALUES (?, ?, ?)
        """, (attendance.registration_id, attendance.attended, check_in_time))
        
        attendance_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Attendance marked successfully",
            "attendance_id": attendance_id,
            "data": {
                "registration_id": attendance.registration_id,
                "attended": attendance.attended,
                "check_in_time": check_in_time,
                "student_name": registration['student_name'],
                "event_title": registration['event_title']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/attendance", response_model=List[Dict[str, Any]])
async def get_attendance(
    event_id: Optional[int] = Query(None),
    registration_id: Optional[int] = Query(None)
):
    """Get attendance records with optional filtering"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT a.*, r.registration_id, s.name as student_name, s.email as student_email,
                   e.title as event_title, e.start_time as event_start
            FROM Attendance a
            LEFT JOIN Registrations r ON a.registration_id = r.registration_id
            LEFT JOIN Students s ON r.student_id = s.student_id
            LEFT JOIN Events e ON r.event_id = e.event_id
            WHERE 1=1
        """
        params = []
        
        if event_id:
            query += " AND e.event_id = ?"
            params.append(event_id)
        
        if registration_id:
            query += " AND a.registration_id = ?"
            params.append(registration_id)
        
        query += " ORDER BY a.check_in_time DESC"
        
        cursor.execute(query, params)
        attendance_records = rows_to_list(cursor.fetchall())
        
        conn.close()
        return attendance_records
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# FEEDBACK ENDPOINTS
# ============================================================================

@app.post("/api/feedback/submit", response_model=Dict[str, Any])
async def submit_feedback(feedback: FeedbackSubmit):
    """Submit feedback for an event"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validate registration exists and has attendance
        cursor.execute("""
            SELECT r.*, s.name as student_name, e.title as event_title
            FROM Registrations r
            LEFT JOIN Students s ON r.student_id = s.student_id
            LEFT JOIN Events e ON r.event_id = e.event_id
            LEFT JOIN Attendance a ON r.registration_id = a.registration_id
            WHERE r.registration_id = ? AND a.attended = 1
        """, (feedback.registration_id,))
        
        registration = cursor.fetchone()
        if not registration:
            raise HTTPException(status_code=404, detail="Registration not found or student did not attend")
        
        # Check if feedback already submitted
        cursor.execute("""
            SELECT feedback_id FROM Feedback WHERE registration_id = ?
        """, (feedback.registration_id,))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Feedback already submitted for this registration")
        
        # Validate rating
        if not 1 <= feedback.rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Submit feedback
        cursor.execute("""
            INSERT INTO Feedback (registration_id, rating, comments) 
            VALUES (?, ?, ?)
        """, (feedback.registration_id, feedback.rating, feedback.comments))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_id,
            "data": {
                "registration_id": feedback.registration_id,
                "rating": feedback.rating,
                "comments": feedback.comments,
                "student_name": registration['student_name'],
                "event_title": registration['event_title']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# REPORT GENERATION ENDPOINTS
# ============================================================================

@app.get("/api/reports/events", response_model=Dict[str, Any])
async def generate_events_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    college_id: Optional[int] = Query(None),
    event_type_id: Optional[int] = Query(None)
):
    """Generate events report with statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        query = """
            SELECT e.*, c.name as college_name, et.name as event_type_name,
                   COUNT(r.registration_id) as total_registrations,
                   COUNT(a.attendance_id) as total_attendance,
                   AVG(f.rating) as avg_rating
            FROM Events e
            LEFT JOIN Colleges c ON e.college_id = c.college_id
            LEFT JOIN EventTypes et ON e.type_id = et.type_id
            LEFT JOIN Registrations r ON e.event_id = r.event_id AND r.status = 'registered'
            LEFT JOIN Attendance a ON r.registration_id = a.registration_id AND a.attended = 1
            LEFT JOIN Feedback f ON r.registration_id = f.registration_id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND e.start_time >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND e.start_time <= ?"
            params.append(end_date)
        
        if college_id:
            query += " AND e.college_id = ?"
            params.append(college_id)
        
        if event_type_id:
            query += " AND e.type_id = ?"
            params.append(event_type_id)
        
        query += " GROUP BY e.event_id ORDER BY e.start_time DESC"
        
        cursor.execute(query, params)
        events = rows_to_list(cursor.fetchall())
        
        # Calculate summary statistics
        total_events = len(events)
        total_registrations = sum(event['total_registrations'] for event in events)
        total_attendance = sum(event['total_attendance'] for event in events)
        avg_rating = sum(event['avg_rating'] or 0 for event in events) / total_events if total_events > 0 else 0
        
        conn.close()
        
        return {
            "summary": {
                "total_events": total_events,
                "total_registrations": total_registrations,
                "total_attendance": total_attendance,
                "average_rating": round(avg_rating, 2),
                "attendance_rate": round((total_attendance / total_registrations * 100) if total_registrations > 0 else 0, 2)
            },
            "events": events
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/attendance", response_model=Dict[str, Any])
async def generate_attendance_report(
    event_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Generate attendance report"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT e.event_id, e.title as event_title, e.start_time,
                   COUNT(r.registration_id) as total_registrations,
                   COUNT(a.attendance_id) as attended_count,
                   ROUND(COUNT(a.attendance_id) * 100.0 / COUNT(r.registration_id), 2) as attendance_rate
            FROM Events e
            LEFT JOIN Registrations r ON e.event_id = r.event_id AND r.status = 'registered'
            LEFT JOIN Attendance a ON r.registration_id = a.registration_id AND a.attended = 1
            WHERE 1=1
        """
        params = []
        
        if event_id:
            query += " AND e.event_id = ?"
            params.append(event_id)
        
        if start_date:
            query += " AND e.start_time >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND e.start_time <= ?"
            params.append(end_date)
        
        query += " GROUP BY e.event_id ORDER BY e.start_time DESC"
        
        cursor.execute(query, params)
        attendance_data = rows_to_list(cursor.fetchall())
        
        conn.close()
        
        return {
            "attendance_report": attendance_data,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/feedback", response_model=Dict[str, Any])
async def generate_feedback_report(
    event_id: Optional[int] = Query(None),
    min_rating: Optional[int] = Query(None)
):
    """Generate feedback report"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT e.event_id, e.title as event_title,
                   COUNT(f.feedback_id) as total_feedback,
                   AVG(f.rating) as average_rating,
                   MIN(f.rating) as min_rating,
                   MAX(f.rating) as max_rating
            FROM Events e
            LEFT JOIN Registrations r ON e.event_id = r.event_id
            LEFT JOIN Feedback f ON r.registration_id = f.registration_id
            WHERE f.feedback_id IS NOT NULL
        """
        params = []
        
        if event_id:
            query += " AND e.event_id = ?"
            params.append(event_id)
        
        if min_rating:
            query += " AND f.rating >= ?"
            params.append(min_rating)
        
        query += " GROUP BY e.event_id ORDER BY e.start_time DESC"
        
        cursor.execute(query, params)
        feedback_data = rows_to_list(cursor.fetchall())
        
        # Get detailed feedback
        detail_query = """
            SELECT f.*, s.name as student_name, e.title as event_title
            FROM Feedback f
            LEFT JOIN Registrations r ON f.registration_id = r.registration_id
            LEFT JOIN Students s ON r.student_id = s.student_id
            LEFT JOIN Events e ON r.event_id = e.event_id
            WHERE 1=1
        """
        detail_params = []
        
        if event_id:
            detail_query += " AND e.event_id = ?"
            detail_params.append(event_id)
        
        if min_rating:
            detail_query += " AND f.rating >= ?"
            detail_params.append(min_rating)
        
        detail_query += " ORDER BY f.submitted_at DESC"
        
        cursor.execute(detail_query, detail_params)
        detailed_feedback = rows_to_list(cursor.fetchall())
        
        conn.close()
        
        return {
            "summary": feedback_data,
            "detailed_feedback": detailed_feedback,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check():
    """System health check"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM Events")
        event_count = cursor.fetchone()['count']
        conn.close()
        
        return {
            "status": "healthy",
            "database_connected": True,
            "total_events": event_count,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database_connected": False,
            "error": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

@app.get("/api/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Count all entities
        tables = ['Colleges', 'Students', 'Events', 'Registrations', 'Attendance', 'Feedback']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            stats[table.lower()] = cursor.fetchone()['count']
        
        # Calculate rates
        if stats['registrations'] > 0:
            stats['attendance_rate'] = round((stats['attendance'] / stats['registrations']) * 100, 2)
        else:
            stats['attendance_rate'] = 0
        
        # Get average rating
        cursor.execute("SELECT AVG(rating) as avg_rating FROM Feedback")
        avg_rating = cursor.fetchone()['avg_rating']
        stats['average_rating'] = round(avg_rating, 2) if avg_rating else 0
        
        conn.close()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Event Management System API v2.0")
    print("📖 API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
