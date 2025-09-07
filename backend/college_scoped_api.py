#!/usr/bin/env python3
"""
College-Scoped API for Event Management System
Supports multi-college architecture with college-scoped unique IDs
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Path
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from pathlib import Path as PathLib
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

# Database configuration
DATABASE_PATH = PathLib(__file__).parent.parent / "database" / "event_management_db.db"

# Pydantic models
class EventCreate(BaseModel):
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
    student_id: int  # This will be college_student_id
    event_id: int    # This will be college_event_id

class AttendanceMark(BaseModel):
    registration_id: int
    attended: int
    check_in_time: Optional[str] = None

class FeedbackSubmission(BaseModel):
    registration_id: int
    rating: int
    comments: Optional[str] = None

# FastAPI app
app = FastAPI(
    title="College-Scoped Event Management API",
    description="Multi-college event management system with college-scoped unique IDs",
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
# COLLEGE MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/colleges", response_model=List[Dict[str, Any]])
async def get_colleges():
    """Get all colleges"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, 
                   COUNT(DISTINCT s.student_id) as total_students,
                   COUNT(DISTINCT e.event_id) as total_events
            FROM Colleges c
            LEFT JOIN Students s ON c.college_id = s.college_id
            LEFT JOIN Events e ON c.college_id = e.college_id
            GROUP BY c.college_id
            ORDER BY c.name
        """)
        
        colleges = rows_to_list(cursor.fetchall())
        conn.close()
        
        return colleges
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/colleges/{college_id}", response_model=Dict[str, Any])
async def get_college_details(college_id: int = Path(..., description="College ID")):
    """Get detailed information about a specific college"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get college basic info
        cursor.execute("SELECT * FROM Colleges WHERE college_id = ?", (college_id,))
        college = cursor.fetchone()
        if not college:
            raise HTTPException(status_code=404, detail="College not found")
        
        # Get statistics
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT s.student_id) as total_students,
                COUNT(DISTINCT e.event_id) as total_events,
                COUNT(DISTINCT r.registration_id) as total_registrations,
                COUNT(DISTINCT a.attendance_id) as total_attendance,
                COUNT(DISTINCT f.feedback_id) as total_feedback
            FROM Colleges c
            LEFT JOIN Students s ON c.college_id = s.college_id
            LEFT JOIN Events e ON c.college_id = e.college_id
            LEFT JOIN Registrations r ON e.event_id = r.event_id
            LEFT JOIN Attendance a ON r.registration_id = a.registration_id
            LEFT JOIN Feedback f ON r.registration_id = f.registration_id
            WHERE c.college_id = ?
        """, (college_id,))
        
        stats = cursor.fetchone()
        
        college_data = dict(college)
        college_data['statistics'] = dict(stats)
        
        conn.close()
        return college_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# COLLEGE-SCOPED EVENT ENDPOINTS
# ============================================================================

@app.post("/api/colleges/{college_id}/events", response_model=Dict[str, Any])
async def create_college_event(
    event: EventCreate,
    college_id: int = Path(..., description="College ID")
):
    """Create a new event for a specific college"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validate college exists
        cursor.execute("SELECT college_id FROM Colleges WHERE college_id = ?", (college_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="College not found")
        
        # Validate event type exists
        cursor.execute("SELECT type_id FROM EventTypes WHERE type_id = ?", (event.type_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Event type not found")
        
        # Validate admin exists and belongs to this college
        cursor.execute("SELECT admin_id FROM Admins WHERE admin_id = ? AND college_id = ?", 
                      (event.created_by, college_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Admin not found or doesn't belong to this college")
        
        # Get next college_event_id
        cursor.execute("""
            SELECT COALESCE(MAX(college_event_id), 0) + 1 as next_id
            FROM Events 
            WHERE college_id = ?
        """, (college_id,))
        next_college_event_id = cursor.fetchone()['next_id']
        
        # Insert event
        cursor.execute("""
            INSERT INTO Events (college_id, college_event_id, title, description, type_id, 
                              venue, start_time, end_time, capacity, created_by, semester, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (college_id, next_college_event_id, event.title, event.description, event.type_id, 
              event.venue, event.start_time, event.end_time, event.capacity, 
              event.created_by, event.semester, event.status))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Event created successfully",
            "event_id": event_id,
            "college_event_id": next_college_event_id,
            "college_id": college_id,
            "data": event.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/colleges/{college_id}/events", response_model=List[Dict[str, Any]])
async def get_college_events(
    college_id: int = Path(..., description="College ID"),
    event_type_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=1000)
):
    """Get all events for a specific college"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validate college exists
        cursor.execute("SELECT college_id FROM Colleges WHERE college_id = ?", (college_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="College not found")
        
        # Build query with filters
        query = """
            SELECT e.*, c.name as college_name, et.name as event_type_name, a.name as created_by_name
            FROM Events e
            LEFT JOIN Colleges c ON e.college_id = c.college_id
            LEFT JOIN EventTypes et ON e.type_id = et.type_id
            LEFT JOIN Admins a ON e.created_by = a.admin_id
            WHERE e.college_id = ?
        """
        params = [college_id]
        
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
                FROM Registrations r
                JOIN Events e2 ON r.event_id = e2.event_id
                WHERE e2.event_id = ? AND r.status = 'registered'
            """, (event['event_id'],))
            reg_count = cursor.fetchone()['reg_count']
            event['current_registrations'] = reg_count
            event['available_spots'] = event['capacity'] - reg_count
        
        conn.close()
        return events
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/colleges/{college_id}/events/{college_event_id}", response_model=Dict[str, Any])
async def get_college_event_details(
    college_id: int = Path(..., description="College ID"),
    college_event_id: int = Path(..., description="College Event ID")
):
    """Get detailed information about a specific college event"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.*, c.name as college_name, et.name as event_type_name, a.name as created_by_name
            FROM Events e
            LEFT JOIN Colleges c ON e.college_id = c.college_id
            LEFT JOIN EventTypes et ON e.type_id = et.type_id
            LEFT JOIN Admins a ON e.created_by = a.admin_id
            WHERE e.college_id = ? AND e.college_event_id = ?
        """, (college_id, college_event_id))
        
        event = row_to_dict(cursor.fetchone())
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Get registration count
        cursor.execute("""
            SELECT COUNT(*) as reg_count 
            FROM Registrations r
            JOIN Events e2 ON r.event_id = e2.event_id
            WHERE e2.event_id = ? AND r.status = 'registered'
        """, (event['event_id'],))
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
# COLLEGE-SCOPED STUDENT ENDPOINTS
# ============================================================================

@app.get("/api/colleges/{college_id}/students", response_model=List[Dict[str, Any]])
async def get_college_students(
    college_id: int = Path(..., description="College ID"),
    semester: Optional[str] = Query(None),
    limit: int = Query(100, le=1000)
):
    """Get all students for a specific college"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validate college exists
        cursor.execute("SELECT college_id FROM Colleges WHERE college_id = ?", (college_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="College not found")
        
        query = """
            SELECT s.*, c.name as college_name
            FROM Students s
            LEFT JOIN Colleges c ON s.college_id = c.college_id
            WHERE s.college_id = ?
        """
        params = [college_id]
        
        if semester:
            query += " AND s.semester = ?"
            params.append(semester)
        
        query += " ORDER BY s.name LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        students = rows_to_list(cursor.fetchall())
        
        conn.close()
        return students
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# COLLEGE-SCOPED REGISTRATION ENDPOINTS
# ============================================================================

@app.post("/api/colleges/{college_id}/events/{college_event_id}/register", response_model=Dict[str, Any])
async def register_student_for_college_event(
    registration: StudentRegistration,
    college_id: int = Path(..., description="College ID"),
    college_event_id: int = Path(..., description="College Event ID")
):
    """Register a student for a college event using college-scoped IDs"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the global event_id from college_event_id
        cursor.execute("""
            SELECT event_id FROM Events 
            WHERE college_id = ? AND college_event_id = ?
        """, (college_id, college_event_id))
        
        event_row = cursor.fetchone()
        if not event_row:
            raise HTTPException(status_code=404, detail="Event not found")
        
        global_event_id = event_row['event_id']
        
        # Get the global student_id from college_student_id
        cursor.execute("""
            SELECT student_id FROM Students 
            WHERE college_id = ? AND college_student_id = ?
        """, (college_id, registration.student_id))
        
        student_row = cursor.fetchone()
        if not student_row:
            raise HTTPException(status_code=404, detail="Student not found")
        
        global_student_id = student_row['student_id']
        
        # Validate event is active and not started
        cursor.execute("""
            SELECT event_id, capacity, start_time, status 
            FROM Events 
            WHERE event_id = ? AND status = 'active'
        """, (global_event_id,))
        
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found or not active")
        
        if datetime.now() > datetime.fromisoformat(event['start_time'].replace(' ', 'T')):
            raise HTTPException(status_code=400, detail="Cannot register for events that have already started")
        
        # Check if already registered
        cursor.execute("""
            SELECT registration_id 
            FROM Registrations 
            WHERE student_id = ? AND event_id = ?
        """, (global_student_id, global_event_id))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Student already registered for this event")
        
        # Check capacity
        cursor.execute("""
            SELECT COUNT(*) as reg_count 
            FROM Registrations 
            WHERE event_id = ? AND status = 'registered'
        """, (global_event_id,))
        
        reg_count = cursor.fetchone()['reg_count']
        if reg_count >= event['capacity']:
            raise HTTPException(status_code=400, detail="Event is at full capacity")
        
        # Register student
        cursor.execute("""
            INSERT INTO Registrations (student_id, event_id, status) 
            VALUES (?, ?, 'registered')
        """, (global_student_id, global_event_id))
        
        registration_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Student registered successfully",
            "registration_id": registration_id,
            "college_id": college_id,
            "college_event_id": college_event_id,
            "college_student_id": registration.student_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# COLLEGE-SCOPED REPORTS
# ============================================================================

@app.get("/api/colleges/{college_id}/reports/event-popularity", response_model=Dict[str, Any])
async def get_college_event_popularity_report(
    college_id: int = Path(..., description="College ID"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    event_type_id: Optional[int] = Query(None),
    limit: int = Query(50, le=1000)
):
    """Generate event popularity report for a specific college"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validate college exists
        cursor.execute("SELECT name FROM Colleges WHERE college_id = ?", (college_id,))
        college = cursor.fetchone()
        if not college:
            raise HTTPException(status_code=404, detail="College not found")
        
        # Build query
        query = """
            SELECT 
                e.college_event_id,
                e.title,
                e.start_time,
                e.capacity,
                et.name as event_type_name,
                COUNT(r.registration_id) as total_registrations,
                COUNT(CASE WHEN a.attended = 1 THEN 1 END) as total_attendance,
                ROUND(AVG(f.rating), 2) as average_rating,
                ROUND(COUNT(CASE WHEN a.attended = 1 THEN 1 END) * 100.0 / COUNT(r.registration_id), 2) as attendance_rate
            FROM Events e
            LEFT JOIN EventTypes et ON e.type_id = et.type_id
            LEFT JOIN Registrations r ON e.event_id = r.event_id AND r.status = 'registered'
            LEFT JOIN Attendance a ON r.registration_id = a.registration_id
            LEFT JOIN Feedback f ON r.registration_id = f.registration_id
            WHERE e.college_id = ?
        """
        params = [college_id]
        
        if start_date:
            query += " AND e.start_time >= ?"
            params.append(f"{start_date} 00:00:00")
        
        if end_date:
            query += " AND e.start_time <= ?"
            params.append(f"{end_date} 23:59:59")
        
        if event_type_id:
            query += " AND e.type_id = ?"
            params.append(event_type_id)
        
        query += " GROUP BY e.event_id ORDER BY total_registrations DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        events = rows_to_list(cursor.fetchall())
        
        # Calculate summary
        if events:
            total_events = len(events)
            total_registrations = sum(event['total_registrations'] for event in events)
            total_attendance = sum(event['total_attendance'] for event in events)
            avg_registrations = total_registrations / total_events
        else:
            total_events = 0
            total_registrations = 0
            total_attendance = 0
            avg_registrations = 0
        
        conn.close()
        
        return {
            "report_type": "College Event Popularity Report",
            "college_id": college_id,
            "college_name": college['name'],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_events": total_events,
                "total_registrations": total_registrations,
                "total_attendance": total_attendance,
                "average_registrations_per_event": round(avg_registrations, 2)
            },
            "events": events
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/colleges/{college_id}/reports/student-participation", response_model=Dict[str, Any])
async def get_college_student_participation_report(
    college_id: int = Path(..., description="College ID"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(100, le=1000)
):
    """Generate student participation report for a specific college"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validate college exists
        cursor.execute("SELECT name FROM Colleges WHERE college_id = ?", (college_id,))
        college = cursor.fetchone()
        if not college:
            raise HTTPException(status_code=404, detail="College not found")
        
        # Build query
        query = """
            SELECT 
                s.college_student_id,
                s.name as student_name,
                s.email as student_email,
                s.semester,
                COUNT(DISTINCT r.event_id) as total_events_registered,
                COUNT(DISTINCT CASE WHEN a.attended = 1 THEN r.event_id END) as total_events_attended,
                COUNT(DISTINCT f.feedback_id) as total_feedback_submitted,
                ROUND(AVG(f.rating), 2) as average_feedback_rating,
                ROUND(COUNT(DISTINCT CASE WHEN a.attended = 1 THEN r.event_id END) * 100.0 / COUNT(DISTINCT r.event_id), 2) as attendance_rate
            FROM Students s
            LEFT JOIN Registrations r ON s.student_id = r.student_id AND r.status = 'registered'
            LEFT JOIN Events e ON r.event_id = e.event_id
            LEFT JOIN Attendance a ON r.registration_id = a.registration_id
            LEFT JOIN Feedback f ON r.registration_id = f.registration_id
            WHERE s.college_id = ?
        """
        params = [college_id]
        
        if start_date:
            query += " AND e.start_time >= ?"
            params.append(f"{start_date} 00:00:00")
        
        if end_date:
            query += " AND e.start_time <= ?"
            params.append(f"{end_date} 23:59:59")
        
        query += " GROUP BY s.student_id ORDER BY total_events_attended DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        students = rows_to_list(cursor.fetchall())
        
        # Calculate summary
        if students:
            total_students = len(students)
            total_events_attended = sum(student['total_events_attended'] for student in students)
            avg_events_per_student = total_events_attended / total_students
        else:
            total_students = 0
            total_events_attended = 0
            avg_events_per_student = 0
        
        conn.close()
        
        return {
            "report_type": "College Student Participation Report",
            "college_id": college_id,
            "college_name": college['name'],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_students": total_students,
                "total_events_attended": total_events_attended,
                "average_events_per_student": round(avg_events_per_student, 2)
            },
            "students": students
        }
        
    except HTTPException:
        raise
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
        cursor.execute("SELECT COUNT(*) as count FROM Colleges")
        college_count = cursor.fetchone()['count']
        conn.close()
        
        return {
            "status": "healthy",
            "database_connected": True,
            "total_colleges": college_count,
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

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting College-Scoped Event Management API")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🏫 Multi-College Support with College-Scoped IDs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
